from unittest.mock import Mock
from minio import S3Error
import pytest

from service.storage_service import StorageService


@pytest.mark.asyncio
async def test_s3_errors_are_propagated_if_not_no_such_key():
    minio = Mock()
    minio.get_object.side_effect = [
        S3Error(
            Mock(),
            'NoSuchKey',
            'No such object',
            '1.jpg',
            None,
            None
        ),
        S3Error(
            Mock(),
            'InternalServerError',
            'Internal Server Error',
            '1.jpg',
            None,
            None
        )
    ]

    storage_service = StorageService(minio)
    assert await storage_service.get_propic(1) is None
    with pytest.raises(S3Error):
        await storage_service.get_propic(1)
