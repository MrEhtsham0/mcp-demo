from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from config import settings
from app.repository.aws_repository import upload_file_to_s3

router = APIRouter(tags=["Upload"])

@router.post("/upload_files")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 1. Generate unique filename
        file_extension = file.filename.split(".")[-1]
        s3_file_name = f"{uuid.uuid4()}.{file_extension}"
        
        # 2. Upload to S3
        s3_object_details = await upload_file_to_s3(
            file_obj=file.file, 
            bucket_name=settings.aws_s3_bucket_name,
            object_name=s3_file_name
        )

        return {
            "message": "File uploaded successfully",
            "s3_object": s3_object_details
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")