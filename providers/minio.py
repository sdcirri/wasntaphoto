from fastapi import Request
from minio import Minio
from os import getenv

from service.storage_service import StorageService


def connect_minio_from_env() -> Minio:
    minio_url = getenv('MINIO_URL')
    minio_access_key = getenv('MINIO_ACCESS_KEY')
    minio_secret_key = getenv('MINIO_SECRET_KEY')

    if any(x is None for x in (minio_url, minio_access_key, minio_secret_key)):
        raise RuntimeError('Incomplete Minio config! Check your environment')

    return Minio(
        minio_url,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=False
    )


def get_minio_client(request: Request) -> Minio:
    return request.app.state.minio


def ensure_buckets(client: Minio) -> None:
    for bucket in StorageService.PROPIC_BUCKET, StorageService.POST_BUCKET:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
