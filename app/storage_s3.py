import os
import uuid
import boto3
from botocore.client import Config

class S3Storage:
    def __init__(self, bucket, region, access_key=None, secret_key=None, prefix=""):
        session_kwargs = {}
        if access_key and secret_key:
            session_kwargs.update(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )
        self.session = boto3.session.Session(**session_kwargs)
        self.s3 = self.session.resource("s3", config=Config(signature_version="s3v4"))
        self.bucket = bucket
        self.prefix = prefix or ""

    def put_file(self, file_storage, logical_name: str) -> str:
        ext = os.path.splitext(logical_name)[1].lower()
        uid = uuid.uuid4().hex
        key = f"{self.prefix}{uid}{ext}"
        self.s3.Bucket(self.bucket).put_object(Key=key, Body=file_storage.stream)
        return key

    def presign(self, key: str, expires=3600) -> str:
        client = self.session.client("s3")
        return client.generate_presigned_url(
            ClientMethod="getObject",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires,
        )
