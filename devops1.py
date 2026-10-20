#!/usr/bin/env python3
import subprocess
from datetime import datetime
import json
import boto3
from requests import *

# Defining variables and objects
ec2 = boto3.resource('ec2')
s3 = boto3.resource("s3")
bucket_name = datetime.now().strftime("%H%M%S-pnolan")
website_configuration = {
    'ErrorDocument': {'Key': 'error.html'},
    'IndexDocument': {'Suffix': 'index.html'},
    }
image_url = 'http://devops.setudemo.net/logo.jpg'
img_download = 'logo.jpg'
pemkey_name = 'DevOps1.pem'
URL_file = 'pnolan-websites.txt'
html_file= 'index.html'

def create_ec2_instance():
    try:
        new_instances = ec2.create_instances(
            ImageId='ami-0567589d25e06853e',
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

# Download a file from a URL and save it in the root folder.
# https://www.geeksforgeeks.org/python/how-to-download-files-from-urls-with-python/
def download_file():
    print('Downloading file.')
    try:
        response = get(image_url)
        if response.status_code == 200:
            with open(img_download, 'wb') as f:
                f.write(response.content)
            print(f'File downloaded from {image_url}.')
        else:
            print(f'Failed to download file from {image_url}. Status code: {response.status_code}')
    except Exception as error:
        print(error)

# Upload an image file and an index file to an S3 bucket.
# https://docs.aws.amazon.com/boto3/latest/guide/s3-uploading-files.html
def upload_files_to_s3():
    print(f'Uploading files to S3 bucket {bucket_name}.')
    try:
        with open(img_download, "rb") as f:
            s3.Object(bucket_name, img_download).put(Body=f, ContentType="image/jpeg")
            print (f'{img_download} uploaded to {bucket_name}.')
        with open("index.html", "rb") as f:
            s3.Object(bucket_name, "index.html").put(Body=f, ContentType="text/html")
            print (f'index.html uploaded to {bucket_name}.')
    except Exception as error:
        print (error)

# Write the URLs of the EC2 instance and the S3 static website to a text file.
# Takes in the instance object returned by the create_ec2_instance() function as an argument.
# https://www.w3schools.com/python/python_file_write.asp
def urls_to_file(instance):
    try:
        with open(URL_file, "w") as f:
            f.write(f"ec2 Instance: http://{instance.public_ip_address}/\n")
            f.write(f"S3 Static Website: http://{bucket_name}.s3-website-us-east-1.amazonaws.com/\n")
        print(f'URLs written to {URL_file}')
    except Exception as error:
        print (error)

# Upload the monitoring script to the EC2 instance and execute it. 
# Takes in the instance object returned by the create_ec2_instance() function as an argument.
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
    except Exception as error:
        print (error)

# Create an AMI from the EC2 instance created by the python script.
# Takes in the instance object returned by the create_ec2_instance() function as an argument.
# https://docs.aws.amazon.com/boto3/latest/reference/services/ec2/client/create_image.html#
def create_AMI(instance):
    try:
        image = instance.create_image(
            InstanceId=instance.id,
            Name=datetime.now().strftime("AMI PN-%Y%m-%d-%f"),
            Description='AMI Created for DevOps Assignment 1',
        )
        print(f'AMI created: {image.name} with ID: {image.id}')
    except Exception as error:
        print (error)


if __name__ == '__main__':
    instance = create_ec2_instance()
    create_s3_bucket()
    download_file()
    urls_to_file(instance)
    upload_files_to_s3()
    upload_monitoring(instance)
    create_AMI(instance)
