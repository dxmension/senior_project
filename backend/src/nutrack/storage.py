import asyncio
import re
from pathlib import Path

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError

from nutrack.config import settings

_MULTISPACE_RE = re.compile(r"\s+")
_UNSAFE_RE = re.compile(r"[^a-z0-9._-]+")


def slugify(value: str) -> str:
    text = _MULTISPACE_RE.sub("-", value.strip().lower())
    cleaned = _UNSAFE_RE.sub("-", text).strip("-")
    return cleaned or "course"


def sanitize_filename(filename: str) -> str:
    suffix = Path(filename or "").suffix.lower()
    stem = Path(filename or "").stem.lower()
    safe_stem = _UNSAFE_RE.sub("-", stem).strip("-") or "file"
    return f"{safe_stem}{suffix}"


class ObjectStorage:
    def __init__(self) -> None:
        self.bucket_name = settings.AWS_BUCKET_NAME
        self.endpoint_url = settings.AWS_ENDPOINT_URL or None
        self.public_endpoint_url = settings.AWS_PUBLIC_ENDPOINT_URL or self.endpoint_url
        self._client: BaseClient | None = None
        self._public_client: BaseClient | None = None

    def _build_client(self, endpoint_url: str | None) -> BaseClient:
        config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path" if settings.AWS_S3_FORCE_PATH_STYLE else "auto"},
        )
        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION,
            endpoint_url=endpoint_url,
            config=config,
        )

    @property
    def client(self) -> BaseClient:
        if self._client is None:
            self._client = self._build_client(self.endpoint_url)
        return self._client

    @property
    def public_client(self) -> BaseClient:
        if self._public_client is None:
            self._public_client = self._build_client(self.public_endpoint_url)
        return self._public_client

    async def ensure_bucket(self) -> None:
        await asyncio.to_thread(self._ensure_bucket_sync)

    def _ensure_bucket_sync(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            params = {"Bucket": self.bucket_name}
            if settings.AWS_REGION != "us-east-1":
                params["CreateBucketConfiguration"] = {
                    "LocationConstraint": settings.AWS_REGION
                }
            self.client.create_bucket(**params)

    async def upload_file(
        self,
        source_path: str,
        key: str,
        content_type: str,
    ) -> None:
        await asyncio.to_thread(
            self.client.upload_file,
            source_path,
            self.bucket_name,
            key,
            ExtraArgs={"ContentType": content_type},
        )

    async def delete_file(self, key: str) -> None:
        await asyncio.to_thread(
            self.client.delete_object,
            Bucket=self.bucket_name,
            Key=key,
        )

    async def generate_download_url(self, key: str) -> str:
        return await asyncio.to_thread(
            self.public_client.generate_presigned_url,
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=settings.MATERIAL_PRESIGNED_URL_TTL_SECONDS,
        )
