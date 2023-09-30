from pydantic import BaseModel


class UploadStatus(BaseModel):
    Status: bool