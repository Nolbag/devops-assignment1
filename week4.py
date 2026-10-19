#!/usr/bin/env python3
from datetime import datetime
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

def create_ec2_instance():
    new_instances = ec2.create_instances(
        ImageId='ami-0fef201115eefe936',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.nano',
        SecurityGroups=['launch-wizard-1'],
        KeyName='DevOps2026',
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
    print('Instance Running.')
    print(instance.id)

def create_s3_bucket():
    response = s3.create_bucket(Bucket=bucket_name)
    print(response)
    print("Bucket created")

    bucket_website = s3.BucketWebsite(bucket_name)
    response = bucket_website.put(WebsiteConfiguration=website_configuration)
    print('Website configured.')

def download_file():
    print('Downloading file')
    response = get(image_url)
    with open('logo.jpg', 'wb') as f:
        f.write(response.content)
    print('File downloaded.')

if __name__ == '__main__':
    create_ec2_instance()
    create_s3_bucket()
    download_file()
