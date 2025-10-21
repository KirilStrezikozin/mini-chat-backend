import boto3
import botocore.client

from app.core.config import Config
from app.interfaces.utils.s3.client import S3ClientProtocol


def create_s3_client(config: Config) -> S3ClientProtocol:
    s3 = boto3.client(
        "s3",
        endpoint_url=config.s3.ENDPOINT_URL,
        aws_access_key_id=config.s3.ACCESS_KEY_ID,
        aws_secret_access_key=config.s3.SECRET_ACCESS_KEY,
        region_name=config.s3.REGION_NAME,
        config=botocore.client.Config(signature_version=config.s3.SIGNATURE_VERSION),
    )

    return s3  # type: ignore
