# coding: utf-8
import boto3
from pathlib import Path
session = boto3.Session(profile_name='account_name')

#S3 Bucket
s3_client = session.resource('s3')
bucket = s3_client.create_bucket(
    Bucket='bucket_name')
list(s3_client.buckets.all())
pathname = r'file_path'
path = Path(pathname).expanduser().resolve()
bucket.upload_file(str(path), str(path.name))

####Rekognition
rekognition_client=session.client('rekognition')
response = rekognition_client.start_label_detection(Video={'S3Object': {'Bucket':bucket.name, 'Name':path.name}})
job_response = rekognition_client.get_label_detection(JobId='jobid')


####Parcing s3 event
event['Records'][0]['s3']['bucket']['name']
event['Records'][0]['s3']['object']['key']

####Urrlib - to parce spaces in object name
import urllib
urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])