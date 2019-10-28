#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Webotron: Deploy websites with aws.

Webotron automates the process of deploying static web sites
- Configure AWS S3 buckets
    - Create them
    - Set them up for static website hosting
    - Deploy local files to them
- Configure DNS with AWS Route 53
- Configure Content Delivery Network and SSL with AWS CloudFront
"""
from pprint import pprint
import boto3
import click
import webotron.util

from webotron.bucket import BucketManager
from webotron.domain import DomainManager
from webotron.certificate import CertificateManager
from webotron.cdn import DistributionManager


session = None
bucket_manager = None
domain_manager = None
certificate_manager = None
distribution_manager = None


@click.group()
@click.option('--profile', default=None, required=True,
              help="Use a given AWS profile.")
def cli(profile):
    """Webotron deploys websites to AWS."""
    global session, bucket_manager, domain_manager, certificate_manager,distribution_manager
    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile
    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)
    domain_manager = DomainManager(session)
    certificate_manager = CertificateManager(session)
    distribution_manager = DistributionManager(session)


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets"""
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list-buckets-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in an s3 bucket"""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and configure S3 bucket."""
    s3_bucket = bucket_manager.init_bucket(bucket)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)
    return


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync content of PATHNAME to BUCKET."""
    bucket_manager.sync(pathname, bucket)
    print(bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucket)))


@cli.command('setup-domain')
@click.argument('domain')
def setup_domain(domain):
    """Configure DOMAIN to point to BUCKET."""
    bucket = domain
    zone = domain_manager.find_hosted_zone(domain) or domain_manager.create_hosted_zone(domain)
    endpoint = util.get_endpoint(bucket_manager.get_region_name(bucket))
    domain_manager.create_s3_domain_record(zone, domain, endpoint)
    print("Domain configured: http://{}".format(domain))


@cli.command('find-cert')
@click.argument('domain')
def find_cert(domain):
    """Find a certificate for <DOMAIN>."""
    print(certificate_manager.find_matching_cert(domain))


@cli.command('setup-cdn')
@click.argument('domain')
@click.argument('bucket')
def setup_cdn(domain, bucket):
    """Setup CloudFront CDN for DOMAIN pointing to BUCKET."""
    dist = distribution_manager.find_matching_dist(domain)

    if not dist:
        cert = certificate_manager.find_matching_cert(domain)
        if not cert:
            print("Error: No matching cert found")
            return
        dist = distribution_manager.create_dist(domain, cert)
        print("Waiting for distribution deployment...")
        distribution_manager.await_deploy(dist)

    zone = domain_manager.find_hosted_zone(domain) or domain_manager.create_hosted_zone(domain)
    domain_manager.create_cf_domain_record(zone, domain, dist['DomainName'])
    print("Domain configured: https://{}".format(domain))
    return


if __name__ == '__main__':
    cli()

