from datetime import datetime

from pydantic import BaseModel, Field


class MaterialUploadResponse(BaseModel):
    id: int
    course_id: int
    course_code: str
    course_title: str
    week: int
    original_filename: str
    content_type: str
    file_size_bytes: int
    upload_status: str
    curation_status: str
    publish_requested: bool
    error_message: str | None = None
    is_published: bool
    download_url: str | None = None
    created_at: datetime
    updated_at: datetime


class SharedMaterialResponse(BaseModel):
    id: int
    upload_id: int
    course_id: int
    course_code: str
    course_title: str
    week: int
    title: str
    original_filename: str
    content_type: str
    file_size_bytes: int
    download_url: str | None = None
    is_owned_by_current_user: bool
    published_at: datetime


class PublishMaterialRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    week: int = Field(..., ge=1, le=15)


class AdminMaterialUploadResponse(BaseModel):
    id: int
    course_id: int
    course_code: str
    course_title: str
    uploader_id: int
    uploader_name: str
    uploader_email: str
    user_week: int
    shared_week: int | None = None
    shared_title: str | None = None
    original_filename: str
    content_type: str
    file_size_bytes: int
    upload_status: str
    curation_status: str
    error_message: str | None = None
    download_url: str | None = None
    created_at: datetime
    updated_at: datetime
