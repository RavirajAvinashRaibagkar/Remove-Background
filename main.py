import os
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from rembg import remove

app = FastAPI(title="Background Remover")


@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    contents = await file.read()

    try:
        input_image = Image.open(BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read the uploaded image.")

    output_image = remove(input_image)

    buffer = BytesIO()
    output_image.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=no-bg.png"},
    )


# Serve the frontend (index.html, etc.) from /static, and at "/" itself.
# Resolve relative to this file's location so it works no matter what
# directory you launch uvicorn from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")