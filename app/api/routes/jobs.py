from fastapi import UploadFile, APIRouter
from fastapi.responses import JSONResponse

app = APIRouter()


@app.post("/jobs/")
async def upload_jobs(file: UploadFile):
    return JSONResponse(content={"filename": file.filename, "content_type": file.content_type})
