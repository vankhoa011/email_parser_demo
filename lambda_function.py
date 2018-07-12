import boto3
from datetime import datetime 
import os
import time
import json
import urllib.parse

client_athena = boto3.client('athena')
s3 = boto3.client('s3')

database_name = "email"
table_name = "email_info"
# NEED TO CHANGE - S3 bucket to output query result of Athena
s3_result_path = "s3://athena-email-result-output"

# NEED TO CHANGE - Data Path 
s3_data_path = "s3://email-log-file-json/"
s3_folder = "email-log-file-json"


def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        email_content = response['Body'].read().decode('utf-8')
        email_lines = email_content.splitlines()
        file_name = key + ".json"
        file_path = "/tmp/" + file_name
        for line in range(len(email_lines)):
            email_info = {}
            if "Date" in email_lines[line]:
                email_info['Date'] = email_lines[line][6:]
                email_info['Subject'] = email_lines[line+3][9:]
                email_info['From'] = email_lines[line+4][6:]
                email_info['To'] = email_lines[line+5][4:]
                with open(file_path, 'w') as outfile:
                    json.dump(email_info, outfile)
                # Upload to S3.
                s3.upload_file(file_path, s3_folder, file_name)
                print("Upload Successful")
                break
        print("Parsing Successful")
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    # We can separate create Athena table, but for saving time . I added them in this script.
    sql_query = """
                CREATE DATABASE IF NOT EXISTS 
                """ + database_name
    response = client_athena.start_query_execution(
        QueryString=sql_query,
        ResultConfiguration={
            'OutputLocation': s3_result_path
        }
    )
    # Create table
    sql_query = """
                CREATE EXTERNAL TABLE IF NOT EXISTS """ + database_name + "." + table_name + """ (
                    `From` STRING,
                    `Date` STRING,
                    `Subject` STRING,
                    `To` STRING
                    )
                ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
                WITH SERDEPROPERTIES (
                    'serialization.format' = '1'
                    )
                LOCATION '""" + s3_data_path + """';
                """

    response = client_athena.start_query_execution(
        QueryString=sql_query,
        ResultConfiguration={
            'OutputLocation': s3_result_path
        }
    )
    # Wait for query execution finish.
    time.sleep(3)
    # Get query result
    query_result = client_athena.get_query_execution(
        QueryExecutionId=response['QueryExecutionId']
    )
    if query_result['QueryExecution']['Status']['State'] == 'FAILED':
        raise Exception(query_result['QueryExecution']['Status']['StateChangeReason'])
    else:
        print("Create Athena DB Succesfully")

