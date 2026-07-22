from minio import Minio, S3Error
from asyncio import to_thread
from io import BytesIO


class StorageService:
    PROPIC_BUCKET = 'propics'
    POST_BUCKET = 'posts'

    minio_client: Minio = None

    def __init__(self, minio_client: Minio) -> None:
        self.minio_client = minio_client
        for bucket in self.PROPIC_BUCKET, self.POST_BUCKET:
            if not self.minio_client.bucket_exists(bucket):
                self.minio_client.make_bucket(bucket)

    async def _get_blob(self, bucket: str, storage_path: str) -> bytes | None:
        try:
            req = await to_thread(self.minio_client.get_object, bucket, storage_path)
            if req.status == 200:
                return req.data
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return None
            raise
        return None

    async def _store_blob(self, bucket: str, object_name: str, blob: bytes, mimetype: str) -> None:
        with BytesIO(blob) as f:
            await to_thread(
                self.minio_client.put_object,
                bucket,
                object_name,
                f,
                length=len(blob),
                part_size=10 * 1024 * 1024,
                content_type=mimetype
            )

    async def get_propic(self, user_id: int) -> bytes | None:
        return await self._get_blob(self.PROPIC_BUCKET, f'{user_id}.jpg')

    async def store_propic(self, user_id: int, image: bytes) -> None:
        await self._store_blob(self.PROPIC_BUCKET, f'{user_id}.jpg', image, 'image/jpeg')

    async def get_post(self, post_id: int) -> bytes | None:
        return await self._get_blob(self.POST_BUCKET, f'{post_id}.jpg')

    async def store_post(self, post_id: int, image: bytes) -> None:
        await self._store_blob(self.POST_BUCKET, f'{post_id}.jpg', image, 'image/jpeg')
