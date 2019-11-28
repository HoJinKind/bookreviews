#!/bin/bash
# check status of MySQL server
python3 launch_all.py --image=ami-0d5d9d301c853a04a --keyname=yijie-ec2 --instancetype=t2.micro # runs instance and loads
source ./config_files/config_mysql.sh
echo "Server deployment done. Installing required software..."
mysql_server_ip=$server_ip
mysql_public_key=$public_key
mysql_username=$username # NOTE: server username, not mysql database username
# check status and transfer new ip addresses
source ./status_checks/status_check.sh $mysql_server_ip $mysql_public_key $mysql_username


# repeat status checks for all 3 other servers.

# start server services after copying all 