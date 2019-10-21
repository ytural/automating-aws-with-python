import boto3
import click
from pathlib import Path
import mimetypes

session = boto3.Session(profile_name='pyautomation')
s3 = session.resource('s3')


@click.group()
def cli():
    """Webotron deploys websites to AWS"""
    pass


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets"""
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list-buckets-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in an s3 bucket"""
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and configure S3 bucket"""
    if session.region_name == 'us-east-1':
        s3_bucket = s3.create_bucket(Bucket=bucket)
    else:
        s3_bucket = s3.create_bucket(Bucket=bucket,
                                     CreateBucketConfiguration={'LocationConstraint': session.region_name}
                                     )
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
    }""" % s3_bucket.name
    policy = policy.strip()

    pol = s3_bucket.Policy()
    pol.put(Policy=policy)

    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    })
    return


def upload_file(s3_bucket, path, key):
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType': content_type
        })


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync content of PATHNAME to BUCKET"""
    s3_bucket = s3.Bucket(bucket)
    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        for p in target.iterdir():
            if p.is_dir():
                handle_directory(p)
            if p.is_file():
                upload_file(s3_bucket, str(p), str(p.relative_to(root).as_posix()))

    handle_directory(root)


if __name__ == '__main__':
    cli()

