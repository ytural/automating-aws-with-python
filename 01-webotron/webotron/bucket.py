# -*- coding: utf-8 -*-

"""Classes for S3 Buckets."""
from pathlib import Path
import mimetypes
import util

class BucketManager:
    """Manage an S3 Bucket."""

    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = self.session.resource('s3')

    def all_buckets(self):
        """Get an iterator for all buckets"""
        return self.s3.buckets.all()

    def get_region_name(self, bucket):
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket=bucket)
        return bucket_location['LocationConstraint'] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Get the website URL for this bucket."""
        return "http://{}.{}".format(bucket.name, util.get_endpoint(self.get_region_name(bucket.name)).host)

    def all_objects(self, bucket_name):
        """Get an iterator for all objects in bucket"""
        return self.s3.Bucket(bucket_name).objects.all()

    def init_bucket(self, bucket_name):
        """Create new bucket."""
        s3_bucket = None
        if self.session.region_name == 'us-east-1':
            s3_bucket = self.s3.create_bucket(Bucket=bucket_name)
        else:
            s3_bucket = self.s3.create_bucket(Bucket=bucket_name,
                                              CreateBucketConfiguration={
                                                  'LocationConstraint': self.session.region_name
                                              })
        return s3_bucket

    def set_policy(self, bucket):
        """Set bucket policy to be readable by everyone."""
        policy = """
        {
                  "Version":"2012-10-17",
                  "Statement":[{
                    "Sid":"PublicReadGetObject",
                        "Effect":"Allow",
                      "Principal": "*",
                      "Action":["s3:GetObject"],
                      "Resource":["arn:aws:s3:::%s/*"
                      ]
                    }
                  ]
        }""" % bucket.name
        policy = policy.strip()

        pol = bucket.Policy()
        pol.put(Policy=policy)

    def configure_website(self, bucket):
        """Configure s3 website hosting for bucket."""
        ws = bucket.Website()
        ws.put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        })

    @staticmethod
    def upload_file(bucket, path, key):
        """Upload path to s3_bucket at key."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            })

    def sync(self, pathname, bucket_name):
        """Sync contents of path to bucket."""
        bucket = self.s3.Bucket(bucket_name)
        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(bucket, str(p), str(p.relative_to(root).as_posix()))
        handle_directory(root)
