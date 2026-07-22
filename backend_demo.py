from alembic.config import Config
from contextlib import ExitStack
from alembic import command
from pathlib import Path
import uvicorn
import os

from testcontainers.postgres import PostgresContainer
from testcontainers.minio import MinioContainer
from testcontainers.redis import RedisContainer

INITDB_DIR = Path(__file__).parent / 'initdb'


def _postgres_url(container: PostgresContainer) -> str:
    return container.get_connection_url().replace(
        'postgresql+psycopg2://', 'postgresql+psycopg://'
    )


def _redis_url(container: RedisContainer) -> str:
    host = container.get_container_host_ip()
    port = container.get_exposed_port(6379)
    return f'redis://{host}:{port}/0'


def _configure_env(
    postgres: PostgresContainer,
    redis: RedisContainer,
    minio: MinioContainer,
) -> None:
    url = _postgres_url(postgres)
    os.environ['DATABASE_URL'] = url
    os.environ['DATABASE_URL_MIGRATIONS'] = url
    os.environ['REDIS_URL'] = _redis_url(redis)

    minio_config = minio.get_config()
    os.environ['MINIO_URL'] = minio_config['endpoint']
    os.environ['MINIO_ACCESS_KEY'] = minio_config['access_key']
    os.environ['MINIO_SECRET_KEY'] = minio_config['secret_key']


def setup_minio(minio: MinioContainer) -> None:
    from service.storage_service import StorageService

    client = minio.get_client()
    for bucket in StorageService.PROPIC_BUCKET, StorageService.POST_BUCKET:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)


def run_migrations() -> None:
    cfg = Config('alembic.ini')
    cfg.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL_MIGRATIONS'])
    command.upgrade(cfg, 'head')


def main() -> None:
    print('Starting containers...')
    with ExitStack() as stack:
        postgres = PostgresContainer(
            'postgres:18',
            username='wasntaphoto',
            password='wasntaphoto',
            dbname='wasntaphoto',
        )
        postgres.with_volume_mapping(str(INITDB_DIR), '/docker-entrypoint-initdb.d')
        stack.enter_context(postgres)

        redis = stack.enter_context(RedisContainer('redis:8-alpine'))
        minio = stack.enter_context(MinioContainer(
            'minio/minio:RELEASE.2025-09-07T16-13-09Z',
            access_key='wasntaphoto',
            secret_key='wasntaphoto',
        ))

        _configure_env(postgres, redis, minio)
        print('Containers ready.')

        from app import app

        setup_minio(minio)
        run_migrations()
        uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
