# AI Service API

FastAPI 기반의 AI 서비스 API로, NLP 검색, 추천 알고리즘, OpenAI 연동 기능을 제공합니다.

## 🏗️ 아키텍처 개요

본 프로젝트는 **계층형 아키텍처(Layered Architecture)**를 채택하여 각 기능을 독립적으로 관리하고 유지보수성을 높였습니다.

```
┌─────────────────┐
│   API Layer     │  ← FastAPI Routers
├─────────────────┤
│ Service Layer   │  ← Business Logic
├─────────────────┤
│  Model Layer    │  ← Data Models
├─────────────────┤
│  Utils Layer    │  ← Common Utilities
└─────────────────┘
```

## 📁 프로젝트 구조

```
app/
├── main.py                     # FastAPI 애플리케이션 진입점
├── core/
│   ├── config.py              # 환경 설정 관리
│   └── dependencies.py        # 전역 의존성 정의
├── models/
│   ├── nlp.py                 # NLP 검색 관련 데이터 모델
│   ├── recommendation.py      # 추천 시스템 데이터 모델
│   └── openai.py             # OpenAI API 요청/응답 모델
├── services/
│   ├── nlp_service.py        # NLP 검색 비즈니스 로직
│   ├── recommendation_service.py # 추천 알고리즘 구현
│   └── openai_service.py     # OpenAI API 연동 로직
├── routers/
│   ├── nlp.py                # NLP 검색 API 엔드포인트
│   ├── recommendation.py     # 추천 API 엔드포인트
│   └── openai.py            # OpenAI API 엔드포인트
├── utils/
│   ├── pandas_helper.py      # Pandas 데이터 처리 유틸
│   └── common.py            # 공통 유틸리티 함수

```

## 🔧 주요 컴포넌트

### API Layer (Routers)
- **역할**: HTTP 요청/응답 처리, 입력 검증, 라우팅
- **기술**: FastAPI Router, Pydantic 모델 검증
- **파일**: `routers/*.py`

### Service Layer
- **역할**: 핵심 비즈니스 로직 구현, 외부 API 연동
- **특징**: 각 서비스는 독립적으로 동작하며 의존성 주입으로 테스트 가능
- **파일**: `services/*.py`

### Model Layer
- **역할**: 데이터 구조 정의, 입출력 스키마 관리
- **기술**: Pydantic BaseModel 활용
- **파일**: `models/*.py`

### Utils Layer
- **역할**: 공통 기능, 데이터 처리 헬퍼 함수
- **파일**: `utils/*.py`

## 🚀 주요 기능

### 1. NLP 검색 (`/nlp`)
- 자연어 처리 기반 텍스트 검색

### 2. 추천 시스템 (`/recommend`)
- 사용자 기반/아이템 기반 추천 알고리즘
- 협업 필터링 및 콘텐츠 기반 필터링
- 실시간 추천 결과 제공

