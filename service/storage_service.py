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
        """
        Retrieves a blob from the bucket
        :param bucket: bucket name
        :param storage_path: object path
        :return: the object path if it exists, None otherwise
        """
        try:
            req = await to_thread(self.minio_client.get_object, bucket, storage_path)
            if req.status == 200:
                return req.data
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return None
            raise e
        return None

    async def _store_blob(self, bucket: str, storage_path: str, blob: bytes, mimetype: str) -> None:
        """
        Stores a blob into the bucket
        :param bucket: bucket name
        :param storage_path: path where the blob will be stored
        :param blob: the blob to be stored
        :param mimetype: blob mimetype
        """
        with BytesIO(blob) as f:
            await to_thread(
                self.minio_client.put_object,
                bucket,
                storage_path,
                f,
                length=len(blob),
                part_size=10 * 1024 * 1024,
                content_type=mimetype
            )

    async def _delete_blob(self, bucket: str, storage_path: str) -> None:
        """
        Deletes a blob from the bucket
        :param bucket: bucket name
        :param storage_path: object path
        """
        await to_thread(
            self.minio_client.remove_object,
            bucket,
            storage_path
        )

    async def get_propic(self, user_id: int) -> bytes | None:
        return await self._get_blob(self.PROPIC_BUCKET, f'{user_id}.jpg')

    async def store_propic(self, user_id: int, image: bytes) -> None:
        await self._store_blob(self.PROPIC_BUCKET, f'{user_id}.jpg', image, 'image/jpeg')

    async def get_post(self, post_id: int) -> bytes | None:
        return await self._get_blob(self.POST_BUCKET, f'{post_id}.jpg')

    async def store_post(self, post_id: int, image: bytes) -> None:
        await self._store_blob(self.POST_BUCKET, f'{post_id}.jpg', image, 'image/jpeg')

    async def delete_post(self, post_id: int) -> None:
        await self._delete_blob(self.POST_BUCKET, f'{post_id}.jpg')
