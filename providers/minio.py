from minio import Minio
from os import getenv


minio_url = getenv('MINIO_URL')
minio_access_key = getenv('MINIO_ACCESS_KEY')
minio_secret_key = getenv('MINIO_SECRET_KEY')

if any(x is None for x in (minio_url, minio_access_key, minio_secret_key)):
    raise RuntimeError('Incomplete Minio config! Check your environment')


_MINIO: Minio | None = None


async def get_minio_client() -> Minio:
    global _MINIO
    if _MINIO is None:
        _MINIO = Minio(
            minio_url,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False
        )
    return _MINIO
