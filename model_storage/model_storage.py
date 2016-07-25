import boto3
import boto3.session
import os
import pickle
from urllib.parse import urlparse


def is_s3_url(url):
    return url.startswith("s3://")


def parse_s3_url(s3_url):
    """
    Convert an S3 URL of the form s3://bucket/path/to/file into a bucket and a key.

    Args:
        s3_url (str): full URL to data in S3

    Returns:
        a 2-element tuple containing the name of the bucket, and the key
    """
    result = urlparse(s3_url)
    bucket = result.netloc
    path = result.path.strip('/')
    return (bucket, path)


def connect(profile=None, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Get an S3 connection, using the named profile if one is specified.

    If no profile is specified, then we fall back through auth configs using the
    hierarchy specified in the boto3 docs. Outside of the dev environment, we
    expect to use the role associated with the EC2 instance that this runs on.

    Args:
        profile: (Optional) string, the named profile to use

    Returns:
        boto3.s3.connection.S3Connection
    """
    s3 = None

    if profile:
        s3 = boto3.session.Session(profile_name=profile).resource('s3')
    elif aws_access_key_id and aws_secret_access_key:
        s3 = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key).resource('s3')
    else:
        s3 = boto3.resource('s3')

    return s3


def get_(bucket, key, s3=None):
    """
    Downloads the given data from an S3 bucket.

    Args:
        bucket: the bucket name
        key: the actual key name, or path, within the bucket
        s3: (Optional) an S3 connection

    Returns:
        The contents of the S3 file as bytes
    """
    if s3 is None:
        s3 = connect()

    obj = s3.Object(bucket, key).get()
    return obj['Body'].read()


def get_to_file(local_path, bucket, key, s3=None):
    """
    Downloads the given data from an S3 bucket, and writes it to the given path.

    Args:
        local_path: where to put the data
        bucket: the bucket name
        key: the actual key name, or path, within the bucket
        s3: (Optional) an S3 connection
    """
    if s3 is None:
        s3 = connect()

    dirname = os.path.dirname(local_path)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    s3.Bucket(bucket).download_file(key, local_path)


def set_(data, bucket, key, s3=None):
    """
    Uploads the given data to an S3 bucket.

    Args:
        data: bytes
        bucket: the bucket name
        key: the actual key name, or path, within the bucket
        s3: (Optional) an S3 connection
    """
    if s3 is None:
        s3 = connect()

    s3.Object(bucket, key).put(Body=data)


def set_from_file(local_path, bucket, key=None, s3=None):
    """
    Uploads the contents of a named file to an S3 bucket.

    Args:
        local_path: the named file
        bucket: the bucket name
        key: (Optional) the key name to use (defaults to the final component of local_path)
        s3: (Optional) an S3 connection
    """
    if s3 is None:
        s3 = connect()

    if not key:
        key = os.path.basename(local_path)

    with open(local_path, 'rb') as f:
        set_(f, bucket, key, s3)


def save(model, path):
    """
    Persist the model to disk as a binary pickle file.

    Args:
        path (str): The output path to which the model should be written
    """
    with open(path, "wb") as outfile:
        pickle.dump(model, outfile)


def load(pickle_file):
    """
    Load a model from a pickle file and make a new instance from that.

    Args:
        pickle_file (str): The pickled model to load

    Returns:
        A new instance of a ColumnClassifier
    """
    with open(pickle_file, 'rb') as infile:
        return pickle.load(infile)
