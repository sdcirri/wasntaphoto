from testcontainers.minio import MinioContainer
from typing import Any, Generator
from minio import Minio
import pytest
import os

from service.storage_service import StorageService
from providers.minio import connect_minio_from_env


@pytest.fixture(scope='session', autouse=True)
def minio_container() -> Generator[MinioContainer, Any, None]:
    with MinioContainer(
        'minio/minio:RELEASE.2025-09-07T16-13-09Z',
        access_key='minioadmin',
        secret_key='minioadmin',
    ) as container:
        os.environ['MINIO_URL'] = f'{container.get_container_host_ip()}:{container.get_exposed_port(9000)}'
        os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
        os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
        yield container


@pytest.fixture(scope='session')
def minio_client() -> Generator[Minio, None]:
    minio = connect_minio_from_env()
    for bucket in StorageService.PROPIC_BUCKET, StorageService.POST_BUCKET:
        if not minio.bucket_exists(bucket):
            minio.make_bucket(bucket)
    yield minio


@pytest.fixture(autouse=True)
def _clean_minio(minio_client: Minio) -> None:
    for bucket in StorageService.PROPIC_BUCKET, StorageService.POST_BUCKET:
        if minio_client.bucket_exists(bucket):
            for obj in minio_client.list_objects(bucket, recursive=True):
                minio_client.remove_object(bucket, obj.object_name)
