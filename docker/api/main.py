import os
import logging
import aiofiles
import httpx
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, select
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from qdrant_client import QdrantClient

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Настройки БД ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://video_user:video_password@postgres:5432/video_db")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# --- Модель БД ---
class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    internal_filename = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="processing")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Инициализация FastAPI ---
app = FastAPI()
qdrant = QdrantClient(host="qdrant", port=6333)
VIDEO_DIR = "/app/data/video"
os.makedirs(VIDEO_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# --- Страницы ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    async with aiofiles.open("/app/static/index.html", mode="r") as f:
        return await f.read()

# --- API Эндпоинты ---

# 1. Загрузка видео (Прокси в n8n)
@app.post("/api/upload")
async def upload_video(video: UploadFile = File(...)):
    try:
        n8n_webhook_url = "http://n8n:5678/webhook-test/upload-video"
        
        # Критическое изменение: передаем сам файловый поток (video.file), 
        # а не загруженный в память массив байтов (file_bytes)
        files = {
            'video': (video.filename, video.file, video.content_type)
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(n8n_webhook_url, files=files)
            logger.info(f"Отправлено в n8n, статус: {response.status_code}")
            
        try:
            return JSONResponse(status_code=response.status_code, content=response.json())
        except Exception:
            return JSONResponse(status_code=response.status_code, content={"error": response.text})

    except Exception as e:
        logger.error(f"Ошибка загрузки: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# 2. Получить последние 10 видео (Просто читаем то, что записал n8n)
@app.get("/api/videos/list")
async def get_videos():
    html_response = ""
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(Video).order_by(Video.id.desc()).limit(10)
            result = await db.execute(stmt)
            videos = result.scalars().all()
            
        for v in videos:
            color = "#22c55e" if v.status == "ready" else "#ef4444" if v.status == "error" else "#f59e0b"
            date_str = v.created_at.strftime('%H:%M %d-%m') if v.created_at else ""
            
            html_response += f"""
            <tr>
                <td class="p-2 border-b border-slate-700">
                    <div>{v.original_filename}</div>
                    <div class="text-xs text-slate-500">sys: {v.internal_filename}</div>
                </td>
                <td class="p-2 border-b border-slate-700">
                    <span style="color: {color}; font-weight: bold;">{v.status.upper()}</span>
                </td>
                <td class="p-2 border-b border-slate-700 text-slate-400 text-sm">{date_str}</td>
            </tr>
            """
    except Exception as e:
        logger.error(f"Ошибка получения списка видео: {e}")
        html_response = "<tr><td colspan='3' class='p-4 text-center text-red-500'>Ошибка подключения к БД</td></tr>"
        
    if not html_response:
        html_response = "<tr><td colspan='3' class='p-4 text-center text-slate-500'>Видео пока нет</td></tr>"
        
    return HTMLResponse(content=html_response)


# 3. Поиск по Qdrant
@app.post("/api/search")
async def search_video(request: Request):
    data = await request.json()
    query = data.get("query")
    
    hits = qdrant.search(
        collection_name="video_chunks", 
        query_text=query, 
        limit=5
    )
    
    results = []
    for hit in hits:
        filename = hit.payload.get("video_filename", "Неизвестно")
        text = hit.payload.get("text", "")[:200] + "..."
        results.append({"filename": filename, "text": text, "score": hit.score})
        
    return results