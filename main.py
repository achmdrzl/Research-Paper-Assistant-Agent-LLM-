from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.agent import run_agent
from app.tools.upload_pdf import upload_pdf
import shutil
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse


# ✅ MUST BE DEFINED BEFORE `app = FastAPI()`
app = FastAPI()

# ✅ TURN CORS ON
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use "*" for file:// or null origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/query/")
async def query_agent(prompt: str = Form(...)):
    print("📥 Received query:", prompt)
    return {"response": run_agent(prompt)}

@app.post("/upload/")
async def upload_file(file: UploadFile):
    file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = upload_pdf(file_path)
    return result

@app.post("/compare/")
async def compare_papers_route():
    from app.agent import run_compare
    result = run_compare()
    return {"response": result}


