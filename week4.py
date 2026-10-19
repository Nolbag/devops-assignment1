#!/usr/bin/env python3
from datetime import datetime
import boto3

bucket_name = datetime.now().strftime("projectx-bucket1-%Y-%m-%d-%s")

ec2 = boto3.resource('ec2')
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

s3 = boto3.resource("s3")
response = s3.create_bucket(Bucket=bucket_name)
print(response)

website_configuration = {
    'ErrorDocument': {'Key': 'error.html'},
    'IndexDocument': {'Suffix': 'index.html'},
}

bucket_website = s3.BucketWebsite(bucket_name)
response = bucket_website.put(WebsiteConfiguration=website_configuration)

print('Upload an index.html file to test it works!')