import requests
import os
import json
import time
from typing import Any
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

def ensure_dict_array_from_text(text: Any) -> list[dict]:
    # 이미 list[dict]가 들어온 경우
    if isinstance(text, list):
        return [obj for obj in text if isinstance(obj, dict)]

    # dict 단일 객체가 들어온 경우
    if isinstance(text, dict):
        return [text]

    # 문자열(JSON string)인 경우만 json.loads() 시도
    if isinstance(text, str):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            print(f"⚠️ JSON 파싱 실패 → text 그대로 반환: {text[:200]}...")
            return []
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return [obj for obj in data if isinstance(obj, dict)]
        else:
            return []

    # 그 외 타입은 무시
    return []

def fetch_cafe_trend(prompt: str, max_tokens: int = 400, timeout: int = 60, retries: int = 3, delay: int = 5) -> list[dict]:
    """
    Perplexity API 호출 (카페 관련 트렌드/특징)
    항상 list[dict] 반환
    """
    if not PERPLEXITY_API_KEY:
        return [{"info": "데이터 없음", "reason": "PERPLEXITY_API_KEY 미설정"}]

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens
    }

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(PERPLEXITY_URL, json=data, headers=headers, timeout=timeout)
            print(f"🔍 Status: {resp.status_code}")
            print(f"🔍 Raw Response: {resp.text[:200]}...")

            resp.raise_for_status()
            j = resp.json()

            # 응답 구조 방어적 파싱
            content = (
                j.get("choices", [{}])[0]
                 .get("message", {})
                 .get("content", "")
            )
            return ensure_dict_array_from_text(content)

        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout 발생 (시도 {attempt}/{retries})")
            if attempt < retries:
                time.sleep(delay)
            else:
                return [{"info": "데이터 없음", "reason": "타임아웃 발생"}]

        except Exception as e:
            print(f"⚠️ 요청 실패: {e} (시도 {attempt}/{retries})")
            if attempt < retries:
                time.sleep(delay)
            else:
                return [{"info": "데이터 없음", "reason": str(e)}]


def fetch_menu_trends(max_tokens: int = 400, timeout: int = 60) -> list[dict]:
    """
    2025년 한국 카페 메뉴 트렌드 조사
    """
    prompt = """당신은 F&B 트렌드 분석가입니다.
2025년 현재 한국에서 인기 있는 카페 메뉴 트렌드를 조사해 주세요.
신메뉴, 재조명된 음료, 고객 반응이 좋은 메뉴 등을 중심으로 요약해 주세요.
결과는 JSON 배열로 다음 형식에 맞춰 주세요:

[
  {
    "menu": "메뉴 이름",
    "description": "이 메뉴가 어떤 특징을 가지고 있는지",
    "whyPopular": "인기 있는 이유",
    "exampleCafe": "이 메뉴를 제공하는 대표 카페 이름 또는 예시"
  }
]
한국어로 응답해 주세요.
"""
    return fetch_cafe_trend(prompt, max_tokens=max_tokens, timeout=timeout)


def fetch_cafe_features(max_tokens: int = 1024, timeout: int = 60) -> list[dict]:
    """
    2025년 한국 인기 카페들의 공통 특징 조사
    """
    prompt = """
2025년 한국에서 인기가 많은 카페들이 공통적으로 갖고 있는 특징을 조사해 주세요.
예: 분위기, 좌석 구성, 운영 시간, 서비스, 디저트 종류 등
결과는 JSON 배열로 요약해 주세요.

[
  {
    "feature": "특징 이름",
    "description": "이 특징이 왜 중요한지",
    "exampleCafe": "이 특징을 갖춘 대표 카페 이름 또는 설명"
  }
]
모든 응답은 한국어로 응답해 주세요.
"""
    return fetch_cafe_trend(prompt, max_tokens=max_tokens, timeout=timeout)
