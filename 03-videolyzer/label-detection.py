# coding: utf-8
import boto3
from pathlib import Path
session = boto3.Session(profile_name='burneraccount')

#S3 Bucket
s3_client = session.resource('s3')
bucket = s3_client.create_bucket(
    Bucket='turalvideorekognitaion')
list(s3_client.buckets.all())
pathname = r'C:\Users\tural\PycharmProjects\PythonLearning\GitHub\automating-aws-with-python\03-videolyzer\PexelsVideos2364298.mp4'
path = Path(pathname).expanduser().resolve()
bucket.upload_file(str(path), str(path.name))

####Rekognition
rekognition_client=session.client('rekognition')
response = rekognition_client.start_label_detection(Video={'S3Object': {'Bucket':bucket.name, 'Name':path.name}})
job_response = rekognition_client.get_label_detection(JobId='f502dd33c2624052431637008a3cc6d8f1b5e7031dc0f15c43104cfce59a27b3')