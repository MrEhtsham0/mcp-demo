import aioboto3
from config import settings
from typing import BinaryIO

async def upload_file_to_s3(file_obj: BinaryIO, bucket_name: str, object_name: str):
    session = aioboto3.Session()

    async with session.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id.get_secret_value(),
        aws_secret_access_key=settings.aws_secret_access_key.get_secret_value(),
        region_name=settings.aws_region,
    ) as s3:
        
        # Reset pointer to the start of the file/stream
        file_obj.seek(0)
        
        # Upload directly from memory
        await s3.upload_fileobj(file_obj, bucket_name, object_name)

        return f"https://{bucket_name}.s3.{settings.aws_region}.amazonaws.com/{object_name}"