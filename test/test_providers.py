import pytest
import os

from providers.minio import connect_minio_from_env
from providers.redis import connect_redis_from_env
from providers.db import get_engine_from_env


@pytest.mark.asyncio
def test_db_provider_errors_on_no_url():
    back = os.environ.pop('DATABASE_URL')
    with pytest.raises(RuntimeError):
        get_engine_from_env()
    os.environ['DATABASE_URL'] = back


@pytest.mark.asyncio
async def test_redis_provider_errors_on_no_database():
    back = os.environ.pop('REDIS_URL')
    with pytest.raises(RuntimeError):
        await connect_redis_from_env()
    os.environ['REDIS_URL'] = back


@pytest.mark.asyncio
def test_minio_provider_errors_on_partial_config():
    for key in 'MINIO_URL', 'MINIO_ACCESS_KEY', 'MINIO_SECRET_KEY':
        back = os.environ.pop(key)
        with pytest.raises(RuntimeError):
            connect_minio_from_env()
        os.environ[key] = back
