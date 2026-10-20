#!/usr/bin/bash

# until loop to check if the web server is running, if not wait for 5 seconds and check again. Loop exits when the web server is running.
# Prevents the program from continuing until the web server is running.
#https://www.w3schools.com/bash/bash_loops.php. https://www.geeksforgeeks.org/linux-unix/systemctl-in-unix/
until systemctl is-active --quiet httpd
do
    echo "Web server is not running, waiting..."
    sleep 5
done

echo "Web server is runnning"

#
# Some basic monitoring functionality; Tested on Amazon Linux 2023.
#
TOKEN=`curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
MEMORYUSAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
PROCESSES=$(expr $(ps -A | grep -c .) - 1)
HTTPD_PROCESSES=$(ps -A | grep -c httpd)

echo "Instance ID: $INSTANCE_ID"
echo "Memory utilisation: $MEMORYUSAGE"
echo "No of processes: $PROCESSES"
#Added output for the number of httpd processes running.
echo "No of httpd processes: $HTTPD_PROCESSES"
echo "Monitoring complete."