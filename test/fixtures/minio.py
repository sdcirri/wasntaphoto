from collections.abc import AsyncGenerator, Generator
from testcontainers.minio import MinioContainer
from asyncio import to_thread
from minio import Minio
from typing import Any
import pytest_asyncio
import pytest

from providers.services import get_storage_service
from service.storage_service import StorageService
from providers.minio import get_minio_client
import providers.minio as minio_provider
from app import app


@pytest.fixture(scope='session')
def minio_container() -> Generator[MinioContainer, Any, None]:
    with MinioContainer(
        'minio/minio:RELEASE.2025-09-07T16-13-09Z',
        access_key='minioadmin',
        secret_key='minioadmin',
    ) as container:
        yield container


@pytest.fixture(scope='session')
def minio_client(minio_container: MinioContainer) -> Minio:
    client = minio_container.get_client()
    for bucket in StorageService.PROPIC_BUCKET, StorageService.POST_BUCKET:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
    return client


@pytest_asyncio.fixture(autouse=True)
async def override_minio(
        monkeypatch: pytest.MonkeyPatch,
        minio_container: MinioContainer,
        minio_client: Minio,
) -> AsyncGenerator[Minio, None]:
    config = minio_container.get_config()

    monkeypatch.setattr(minio_provider, 'minio_url', config['endpoint'])
    monkeypatch.setattr(minio_provider, 'minio_access_key', config['access_key'])
    monkeypatch.setattr(minio_provider, 'minio_secret_key', config['secret_key'])
    monkeypatch.setattr(minio_provider, '_MINIO', minio_client)

    async def _get_minio_client() -> Minio:
        return minio_client

    def _get_storage_service() -> StorageService:
        return StorageService(minio_client)

    app.dependency_overrides[get_minio_client] = _get_minio_client
    app.dependency_overrides[get_storage_service] = _get_storage_service

    try:
        yield minio_client
    finally:
        app.dependency_overrides.pop(get_minio_client, None)
        app.dependency_overrides.pop(get_storage_service, None)
        minio_provider._MINIO = None


@pytest_asyncio.fixture(autouse=True)
async def _clean_minio(minio_client: Minio) -> AsyncGenerator[None, None]:
    yield
    for bucket in StorageService.PROPIC_BUCKET, StorageService.POST_BUCKET:
        if not minio_client.bucket_exists(bucket):
            continue
        for obj in minio_client.list_objects(bucket, recursive=True):
            await to_thread(minio_client.remove_object, bucket, obj.object_name)
