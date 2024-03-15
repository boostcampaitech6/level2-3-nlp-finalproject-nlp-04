from fastapi import FastAPI, UploadFile, File, APIRouter
from fastapi.responses import FileResponse
from datetime import datetime
import os
import requests
import os
import asyncio
import aiofiles

app = FastAPI()
router = APIRouter()

@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    os.makedirs('data', exist_ok=True)
    async with aiofiles.open(f'data/{file.filename}', 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    return {"filename": file.filename}


@router.get("/items/")
async def read_items():
    return [{"name": "Item 1"}, {"name": "Item 2"}]

@router.get("/fileinfo/{filename}")
async def get_file_info(filename: str):
    file_path = f'data/{filename}'
    if os.path.exists(file_path):
        file_info = os.stat(file_path)
        return {
            "filename": filename,
            "size": file_info.st_size,
            "uploaded_at": datetime.fromtimestamp(file_info.st_ctime).isoformat()
        }
    else:
        return {"error": "File not found"}

app = FastAPI()

app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
