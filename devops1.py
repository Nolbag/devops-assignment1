#!/usr/bin/env python3
import subprocess
from datetime import datetime
import json
import boto3
from requests import *

ec2 = boto3.resource('ec2')
s3 = boto3.resource("s3")
bucket_name = datetime.now().strftime("%H%M%S-pnolan")
website_configuration = {
    'ErrorDocument': {'Key': 'error.html'},
    'IndexDocument': {'Suffix': 'index.html'},
    }
image_url = 'http://devops.setudemo.net/logo.jpg'
object_name = 'logo.jpg'
pemkey_name = 'DevOps1.pem'

def create_ec2_instance():
    try
        new_instances = ec2.create_instances(
            ImageId='ami-0fef201115eefe936',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.nano',
            SecurityGroups=['launch-wizard-1'],
            KeyName='DevOps1',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'WebServer1'}],
                }
            ],
            UserData='''#!/bin/bash
        yum install httpd -y
        systemctl enable httpd
        systemctl start httpd
        TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
        instance_id=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
        ipv4=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/local-ipv4)
        ami_id=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/ami-id)
        availability_zone=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone)
        echo "<html>" > index.html
        echo "Instance ID: $instance_id <br>" >> index.html
        echo "Private IP Address: $ipv4 <br>" >> index.html
        echo "AMI ID: $ami_id <br>" >> index.html
        echo "Availability Zone: $availability_zone <br>" >> index.html
        echo "</html>" >> index.html
        cp index.html /var/www/html/index.html
        ''',
        )

        print('Instance Initializing.')
        instance = new_instances[0]
        instance.wait_until_running()
        instance.reload()
        print(f'Instance {instance.id} is running.')
        return instance
    except Exception as error:
        print (error)

def create_s3_bucket():
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket created: {bucket_name}")

        s3.meta.client.delete_public_access_block(Bucket=bucket_name)

        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        s3.Bucket(bucket_name).Policy().put(Policy=json.dumps(bucket_policy))

        bucket_website = s3.BucketWebsite(bucket_name)
        bucket_website.put(WebsiteConfiguration=website_configuration)
        print('Website configured.')
    except Exception as error:
        print(error)

def download_file():
    print('Downloading file.')
    try:
        response = get(image_url)
        with open('logo.jpg', 'wb') as f:
            f.write(response.content)
        print(f'File downloaded from {image_url}.')
    except Exception as error:
        print(error)

def upload_file_to_s3():
    print(f'Uploading file to S3 bucket {bucket_name}.')
    try:
        s3.Object(bucket_name, object_name).put(Body=open(object_name, 'rb'), ContentType="image/jpeg")
        print (f'File uploaded to S3 {bucket_name}.')
    except Exception as error:
        print (error)

def upload_monitoring(instance):
    ipv4 = instance.public_ip_address
    instance_id = instance.id
    cmd1 = f"scp -o StrictHostKeyChecking=no -i {pemkey_name} monitoring.sh ec2-user@{ipv4}:."
    cmd2 = f"ssh -i {pemkey_name} ec2-user@{ipv4} 'chmod 700 monitoring.sh && ./monitoring.sh'"
    
    try:
        result = subprocess.run(cmd1, shell=True)
        if (result.returncode !=0):
            print(f'Error copying monitoring script on {instance_id}.')
        else:
            subprocess.run(cmd2, shell=True)
            print(f'Monitoring script copied to {instance_id} and executed.')
    except Exception as error:
        print (error)


if __name__ == '__main__':
    instance = create_ec2_instance()
    create_s3_bucket()
    download_file()
    upload_file_to_s3()
    upload_monitoring(instance)