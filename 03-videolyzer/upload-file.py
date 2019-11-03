from pathlib import Path
import boto3
import click


@click.option('--profile', default=None, help="Use a given profile")
@click.argument('bucketname')
@click.argument('pathname', type=click.Path(exists=True))


@click.command()
def upload_file(profile, pathname, bucketname):
    """Upload <PATHNAME> to <BUCKETNAME>"""

    session_cfg = {}

    if profile:
        session_cfg['profile_name'] = profile

    session = boto3.Session(**session_cfg)
    s3_client = session.resource('s3')
    bucket = s3_client.Bucket(bucketname)

    path = Path(pathname).expanduser().resolve()
    bucket.upload_file(str(path), str(path.name))


if __name__ == '__main__':
    upload_file()


