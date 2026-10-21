# DevOps Assignment 1
Python file utilising Boto3 to create an ec2 instance and S3 Bucket.  
The file uploads ec2 instance data and an index.html page to the ec2 instance.  
Also uploads an image and index.html to the S3 Bucket to be hosted on a static website.  
Uploads and runs a monitoring script on the ec2 instance and performs monitoring once web hosting is enabled.  
Creates an AMI based on the instance.  
Uses cloudwatch to monitor metrics related to the instance.  

## Instructions:
 - Clone the respoitory to a local folder.  
 - Save AWS login to a credentials file located at ~/%USER%/.aws.  
 - Update variables to match your AWS config i.e. pem key, ImageId, InstanceType etc.  
 - In a terminal window use the command chmod +x devops1.py to make the script executable.  