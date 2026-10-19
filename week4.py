#!/usr/bin/env python3
from datetime import datetime
import boto3

ec2 = boto3.resource('ec2')
s3 = boto3.resource("s3")
bucket_name = datetime.now().strftime("%H%M%S-pnolan")
website_configuration = {
    'ErrorDocument': {'Key': 'error.html'},
    'IndexDocument': {'Suffix': 'index.html'},
    }

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
    systemctl start httpd''',
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

    bucket_website = s3.BucketWebsite(bucket_name)
    response = bucket_website.put(WebsiteConfiguration=website_configuration)
    print(response)
    print('Upload an index.html file to test it works!')

if __name__ == '__main__':
    create_ec2_instance()
    create_s3_bucket()
