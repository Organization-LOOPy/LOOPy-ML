# app/core/config.py
import os
import sys
from typing import List, Optional, Any, Dict
from pydantic import validator, Field
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 환경 설정
    environment: str = Field(default="dev")
    
    # 앱 설정
    app_name: str = Field(default="AI Processing Service")
    version: str = Field(default="1.0.0")
    description: str = Field(default="FastAPI 내부 AI 서비스")
    
    # 서버 설정
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8001)
    workers: int = Field(default=2)
    
    # 로깅 설정
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # CORS 설정
    dev_cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5137"]
    )
    prod_cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5137"]
    )
    prod_cors_headers: List[str] = Field(
        default=["Content-Type", "X-Internal-API-Key", "X-User-ID", "X-User-Role", "X-Session-ID", "X-User-Permissions"]
    )
    
    # 보안 설정
    internal_api_key: Optional[str] = Field(default=None)
    allowed_hosts: List[str] = Field(default=["127.0.0.1", "localhost"])
    
    # OpenAI 설정
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-3.5-turbo")
    openai_max_tokens: int = Field(default=1000)
    openai_temperature: float = Field(default=0.7)
    
    # 한국어 임베딩 모델 설정
    korean_embedding_model: str = Field(default="jhgan/ko-sroberta-multitask")
    korean_sentence_model: str = Field(default="snunlp/KR-SBERT-V40K-klueNLI-augSTS")
    
    # NLP 처리 설정
    max_sequence_length: int = Field(default=512)
    batch_size: int = Field(default=32)
    similarity_threshold: float = Field(default=0.7)
    top_k_results: int = Field(default=10)
    
    # 모델 캐싱 설정
    model_cache_dir: str = Field(default="./models")
    enable_model_cache: bool = Field(default=True)
    model_download_timeout: int = Field(default=300)
    
    # 데이터 설정
    data_dir: str = Field(default="./data")
    index_dir: str = Field(default="./data/index")
    
    # 성능 설정
    use_gpu: bool = Field(default=False)
    num_threads: int = Field(default=4)
    request_timeout: int = Field(default=30)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    # 검증
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["dev", "prod", "test"]
        if v.lower() not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v.lower()
    
    @validator("similarity_threshold")
    def validate_similarity_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        return v
    
    @validator("openai_temperature")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("openai_temperature must be between 0.0 and 2.0")
        return v
    
    # 계산된 속성들
    @property
    def is_production(self) -> bool:
        return self.environment == "prod"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "dev"
    
    @property
    def debug(self) -> bool:
        return not self.is_production
    
    @property
    def log_level(self) -> int:
        return logging.INFO if self.is_production else logging.DEBUG
    
    @property
    def docs_url(self) -> Optional[str]:
        return "/docs" if not self.is_production else None
    
    @property
    def redoc_url(self) -> Optional[str]:
        return "/redoc" if not self.is_production else None
    
    @property
    def server_url(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    # 환경별 설정 메서드들
    def get_cors_settings(self) -> Dict[str, Any]:
        if self.is_production:
            return {
                "allow_origins": self.prod_cors_origins,
                "allow_credentials": False,
                "allow_methods": ["GET", "POST"],
                "allow_headers": self.prod_cors_headers,
            }
        else:
            return {
                "allow_origins": self.dev_cors_origins,
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            }
    
    def get_uvicorn_settings(self) -> Dict[str, Any]:
        if self.is_production:
            return {
                "host": self.host,
                "port": self.port,
                "log_level": "info",
                "access_log": False,
                "workers": self.workers
            }
        else:
            return {
                "host": self.host,
                "port": self.port,
                "reload": True,
                "log_level": "debug", 
                "access_log": True
            }
    
    def get_fastapi_settings(self) -> Dict[str, Any]:
        return {
            "title": self.app_name,
            "version": self.version,
            "description": self.description,
            "debug": self.debug,
            "docs_url": self.docs_url,
            "redoc_url": self.redoc_url
        }
    
    # 한국어 모델 관련 메서드들
    def get_korean_model_config(self, model_type: str = "default") -> Dict[str, Any]:
        """한국어 모델 설정 반환"""
        model_configs = {
            "default": {
                "model_name": self.korean_embedding_model,
                "max_length": self.max_sequence_length,
                "batch_size": self.batch_size
            },
            "sentence": {
                "model_name": self.korean_sentence_model,
                "max_length": self.max_sequence_length,
                "batch_size": self.batch_size
            },
            "search": {
                "model_name": self.korean_embedding_model,
                "max_length": self.max_sequence_length,
                "batch_size": self.batch_size,
                "similarity_threshold": self.similarity_threshold,
                "top_k": self.top_k_results
            }
        }
        
        return model_configs.get(model_type, model_configs["default"])
    
    def get_device_config(self) -> Dict[str, Any]:
        """디바이스 설정 반환"""
        try:
            import torch
            if self.use_gpu and torch.cuda.is_available():
                device = "cuda"
                device_count = torch.cuda.device_count()
            else:
                device = "cpu"
                device_count = 1
        except ImportError:
            device = "cpu"
            device_count = 1
        
        return {
            "device": device,
            "device_count": device_count,
            "num_threads": self.num_threads if device == "cpu" else None
        }
    
    # 유틸리티 메서드들
    def create_directories(self):
        """필요한 디렉토리들 생성"""
        directories = [self.data_dir, self.model_cache_dir, self.index_dir]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def print_settings(self):
        """현재 설정 정보 출력"""
        print("=" * 60)
        print(f"🌍 Environment: {self.environment}")
        print(f"🏷️  App Name: {self.app_name}")
        print(f"📊 Version: {self.version}")
        print(f"🖥️  Server: {self.server_url}")
        print(f"📊 Log Level: {'INFO' if self.is_production else 'DEBUG'}")
        print(f"🔧 Debug: {self.debug}")
        print("─" * 60)
        print("🇰🇷 한국어 AI 모델 설정:")
        print(f"   📝 기본 임베딩: {self.korean_embedding_model}")
        print(f"   📄 문장 임베딩: {self.korean_sentence_model}")
        print(f"   💾 모델 캐시: {self.model_cache_dir}")
        print(f"   🎯 GPU 사용: {self.use_gpu}")
        if not self.is_production:
            print(f"📖 API Docs: {self.server_url}/docs")
        print("=" * 60)


def get_environment_from_args() -> str:
    """명령행 인자 또는 환경변수에서 환경 설정 가져오기"""
    if len(sys.argv) > 1 and sys.argv[1] in ["dev", "prod"]:
        return sys.argv[1].lower()
    return os.getenv("ENVIRONMENT", "dev").lower()


@lru_cache()
def get_settings() -> Settings:
    """설정 객체 반환 (캐시됨)"""
    env = get_environment_from_args()
    os.environ["ENVIRONMENT"] = env
    return Settings()


def initialize_settings() -> Settings:
    """설정 초기화 및 필요한 디렉토리 생성"""
    settings = get_settings()
    settings.create_directories()
    
    if settings.is_development:
        settings.print_settings()
    
    return settings


if __name__ == "__main__":
    settings = initialize_settings()
    print("\n🇰🇷 한국어 모델 설정:")
    print(f"기본 모델: {settings.get_korean_model_config('default')}")
    print(f"검색 모델: {settings.get_korean_model_config('search')}")
    print(f"디바이스: {settings.get_device_config()}")