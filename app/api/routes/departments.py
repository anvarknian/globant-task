from fastapi import UploadFile, APIRouter
from fastapi.responses import JSONResponse

app = APIRouter()


@app.post("/departments/")
async def upload_departments(file: UploadFile):
    return JSONResponse(content={"filename": file.filename, "content_type": file.content_type})
