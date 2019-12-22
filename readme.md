# 50.043 Database Project

## System Overview
![system image](https://i.imgur.com/Ykq1SHa.jpg)

## Prerequisites
* Install required python packages: `pip3 install -r requirements.txt`
* Ubuntu 18.04 (For other OSes, please refer to "OS Compatibility" section)
* openssh-server
* openssh-client
* Python 3.7 and above (Support for f-strings)
* Good internet connection

## Quickstart
* Navigate to `boto3` folder (eg `cd bookreviews/boto3`)
* To launch Production and Analytics backend, run `call_master.py` like below:
```
python3 call_master.py \
    --csv_aws_credentials=<path/to/csv> \
    --instance_type="t3.large" \
    --n_nodes_analytics=4 \
```
Note: If you see the warning `ssh connection refused`, let the script continue
to run. It should eventually add the IP address of the particular server into 
your `~/.ssh/known_hosts` file.

No free lunch disclaimer: We only officially support "t3.large" instance types. 
Cheaper types risk running out of memory.

* To execute Analytics tasks, run `bash run_analytics.sh`
* To shut down all instances, run `bash shutdown_all.sh`

##  Overview of main system scripts
`bookreviews/boto3/call_master.py`
1. Configure AWS credentials based on the provided .csv
2. Create EC2 key-pair for creating instances
2. Create S3 Bucket for data transfer later
2. Generate bash scripts needed for Analytics cluster (eg cluster_launch.sh, cluster_login.sh)
3. Call `master.sh` to launch Analytics & Production backend (in parallel to save time)

`bookreviews/boto3/master.sh`
1. Launch EC2 instances
2. Run user data for MongoDB, MySQL, React and Flask servers
2. Monitor to wait until user data is complete
3. Extract data from MySQL and MongoDB, uploading to S3 Bucket
4. Configure gunicorn and nginx for Flask/React
6. Display link to access frontend webpage

`bookreviews/boto3/spark_app.py`
1. Import ETL data from S3 Bucket
2. Write data to Hadoop File System
3. Load reviews and metadata into PySpark dataframes
3. Calculate Pearson Correlation between "price" and "reviewLength" in map-reduce fashion
4. Calculate TF-IDF scores for "reviewText"
5. Export results to S3 Bucket

`bookreviews/boto3/run_analytics.sh`
1. Submit Spark job to cluster to run `spark_app.py`
2. Import analytics results from S3 Bucket to local machine

`bookreviews/boto3/shutdown_all.sh`
1. Terminate Analytics backend instances
2. Terminate Production backend instances
3. Delete S3 Bucket

## Overview of Frontend
![Image of frontend](https://i.imgur.com/fLS1Nbj.png)
* Search bar
* User registration and login
* Browse book catalog
* View reviews for each book
* Add new review (Need to login first)

## Expected output:
### Production Backend and Webapp
Launhing `call_master.py` should take about 7 to 9 minutes on t3.large. Here are the expected outputs:

First, you should see that the script creates a security group.

```
Security Group Created sg-01fedfc8fd3c46b0d in vpc vpc-f4aa599f.
Ingress Successfully Set {'ResponseMetadata': {'RequestId': '1af7fbe3-8cdd-4f93-b797-41aced6c686d', 'HTTPStatusCode': 200, 'HTTPHeaders': {'content-type': 'text/xml;charset=UTF-8', 'content-length': '259', 'date': 'Fri, 22 Nov 2019 03:14:29 GMT', 'server': 'AmazonEC2'}, 'RetryAttempts': 0}}
```
Then, you should observe that the servers are being launched via boto3. You would see the details of the servers being printed to the console. Launching the servers generate several text files and bash scripts inside `boto3/ip_addresses` and `boto3/config_files` respectively.
```
******** mongodb server info ********
new instance: i-0e89b57f6c8c2e77f
18.222.205.153
50043-keypair
2019-12-03 14:21:49+00:00

******** mysql server info ********
new instance: i-0d97337cf8702863f
13.58.169.137
50043-keypair
2019-12-03 14:22:22+00:00

******** flask server info ********
new instance: i-03c8be10d66d5bac3
3.14.147.43
50043-keypair
2019-12-03 14:22:54+00:00

******** react server info ********
new instance: i-04c733c0b36cdaad4
18.189.31.214
50043-keypair
2019-12-03 14:23:27+00:00
```
After which, the script starts checking if the servers have finished running the user data scripts. This will take awhile. so grab a cup of coffee and prepare to be amazed.
```
Server deployment done. Checking status of mysql.

Checking server status: (NOTE: ignore warnings for connection refused)
Warning: Permanently added '13.58.169.137' (ECDSA) to the list of known hosts.
.................................................
```
Once the servers have been deployed successfully, the script transfers the newly generated IP addresses and `config.js` file into every server.
```
Server done with deployment. Transferring new IP addresses to server
config_flask_ip.txt                                                                                                                                                                              100%   11     0.0KB/s   00:00    
config_mongodb_ip.txt                                                                                                                                                                            100%   14     0.1KB/s   00:00    
config_mysql_ip.txt                                                                                                                                                                              100%   13     0.1KB/s   00:00    
config_react_ip.txt                                                                                                                                                                              100%   13     0.1KB/s   00:00    
Done
```
Then the script runs the new flask and react servers. This installs sets up and installs a couple of software packages into the react server before being fully operational. Lastly, a link will be printed to the console for you to access our project via any browser.
```
*************************************************
Deployment done! Thank you for your patience! 
Access the webpage via the following link: http://18.189.31.214:80
```
### Analytics
Running the analytics command will result in lots of output on the command line. This scirpt takes about 12 to 15 minutes on t3.large to launch from our tests. The lines to look for are:
```
Downloaded: pearsonr.csv/_SUCCESS
Downloaded: pearsonr.csv/part-00000-af82b809-7402-4e54-818d-d7bb635fa728-c000.csv
Downloaded: pearsonr.csv/part-00001-af82b809-7402-4e54-818d-d7bb635fa728-c000.csv
Downloaded: tfidf.csv/_SUCCESS
Downloaded: tfidf.csv/part-00000-0280fe87-a5b9-4470-a776-c4e6d558c3e0-c000.csv
Downloaded: tfidf.csv/part-00001-0280fe87-a5b9-4470-a776-c4e6d558c3e0-c000.csv
Downloaded: tfidf.csv/part-00002-0280fe87-a5b9-4470-a776-c4e6d558c3e0-c000.csv
Downloaded: tfidf.csv/part-00003-0280fe87-a5b9-4470-a776-c4e6d558c3e0-c000.csv
Downloaded: tfidf.csv/part-00004-0280fe87-a5b9-4470-a776-c4e6d558c3e0-c000.csv
```

### Terminating all processes
Running our script to terminate all the instances would take about 2 to 3 minutes. `shutdown_all.sh` terminates all EC2 instances and S3 bucket created by our production backend and analytics scripts.
```
Destroying my-cluster...
Deleting bucket: <aws_username>-bucket-50043-group-datahoarders
```

### OS Compatibility
**Linux**: Only Ubuntu is officially supported. However, the scripts should work 
if the requirements are installed.

**Windows**: These scripts are meant to run on **UNIX based systems (linux or MacOS)**. 
If you use windows subsystem for linux (WSL), please run `dos2unix` on 
`bookreviews/boto3/status_checks/status_check.sh` and `bookreviews/boto3/master.sh`. 
This is because windows has different file line endings than unix.

**MacOS**: Not officially supported. However, the scripts should work if the 
requirements are installed.
