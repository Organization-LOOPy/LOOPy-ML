# app/main.py
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time
import uvicorn

from app.core.config import get_settings, initialize_settings

settings = initialize_settings()

logging.basicConfig(level=settings.log_level, format=settings.log_format)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 FastAPI 서비스 시작 중...")
    
    if settings.is_production:
        logger.info("🏭 프로덕션 환경으로 시작합니다")
    else:
        logger.debug("🔧 개발 환경으로 시작합니다")
    
    logger.info("✅ 모든 서비스 초기화 완료")
    yield
    logger.info("🛑 FastAPI 서비스 종료 중...")

app = FastAPI(**settings.get_fastapi_settings(), lifespan=lifespan)

cors_settings = settings.get_cors_settings()
app.add_middleware(CORSMiddleware, **cors_settings)

if settings.is_production:
    logger.info("🔒 프로덕션 CORS 설정 적용")
else:
    logger.debug("🔓 개발용 CORS 설정 적용")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    client_host = "unknown"
    if request.client:
        client_host = request.client.host
    
    if settings.is_production:
        logger.info(f"{request.method} {request.url.path}")
    else:
        logger.debug(f"📥 {request.method} {request.url.path} from {client_host}")
        if logger.isEnabledFor(logging.DEBUG):
            for header, value in request.headers.items():
                if header.lower().startswith('x-'):
                    logger.debug(f"   Header: {header}: {value}")
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    if settings.is_production:
        if response.status_code >= 400:
            logger.warning(f"{response.status_code} {request.method} {request.url.path} {process_time:.3f}s")
    else:
        logger.debug(f"📤 {response.status_code} in {process_time:.3f}s")
    
    if not settings.is_production:
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Environment"] = settings.environment
    
    return response

@app.get("/")
async def root():
    return {
        "message": settings.app_name,
        "version": settings.version,
        "status": "running", 
        "type": "internal_service",
        "environment": settings.environment,
        "docs": settings.docs_url,
        "redoc": settings.redoc_url,
        "debug": settings.debug
    }

@app.get("/health")
async def health_check():
    health_info = {
        "status": "healthy",
        "service": "ai_processing",
        "version": settings.version,
        "environment": settings.environment,
        "timestamp": time.time()
    }
    
    if not settings.is_production:
        health_info.update({
            "debug": True,
            "log_level": "DEBUG",
            "docs_enabled": True,
            "korean_models": {
                "embedding_model": settings.korean_embedding_model,
                "sentence_model": settings.korean_sentence_model,
                "model_cache_dir": settings.model_cache_dir
            }
        })
    else:
        health_info["log_level"] = "INFO"
    
    return health_info

if not settings.is_production:
    @app.get("/test")
    async def test_endpoint():
        logger.debug("🧪 테스트 엔드포인트 호출됨")
        return {
            "message": "FastAPI 서비스가 정상 작동 중입니다!",
            "success": True,
            "environment": settings.environment,
            "debug_mode": True,
            "korean_ai_models": {
                "embedding": settings.korean_embedding_model,
                "sentence": settings.korean_sentence_model
            }
        }

def start_server():
    uvicorn_settings = settings.get_uvicorn_settings()
    
    if settings.is_production:
        logger.info("🏭 프로덕션 모드로 서버 시작")
        uvicorn.run(app, **uvicorn_settings)
    else:
        logger.info("🔧 개발 모드로 서버 시작")
        logger.info(f"📖 API 문서: {settings.server_url}/docs")
        logger.info(f"🧪 테스트: {settings.server_url}/test")
        
        # 개발 모드에서는 reload 비활성화하고 app 객체 직접 사용
        dev_settings = uvicorn_settings.copy()
        dev_settings.pop("reload", None)  # reload 제거
        uvicorn.run(app, **dev_settings)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("📋 사용법:")
        print("  python app/main.py dev    # 개발 환경")
        print("  python app/main.py prod   # 프로덕션 환경")
        print()
        print("🚀 기본값으로 개발 환경 시작...")
        print()
    
    start_server()