import os
import json
import re
import requests
from openai_backup import OpenAI
from datetime import datetime, timedelta, timezone
from calendar import monthrange
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from insight_automation.utils.athena import fetch_monthly_metrics
from insight_automation.logic.schemas import MenuTrendItem, CafeFeatureItem
from insight_automation.utils.perplexity import fetch_menu_trends, fetch_cafe_features, ensure_dict_array_from_text
from insight_automation.utils.openai_helper import run_gpt_analysis
from insight_automation.logic.build_insight_from_data import build_insight_from_data
from insight_automation.utils.text import format_with_linebreaks

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

KST = timezone(timedelta(hours=9))

def _prev_month_range(ref_dt: Optional[datetime] = None):
    ref_dt = ref_dt or datetime.now(KST)
    year, month = ref_dt.year, ref_dt.month
    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1
    start = datetime(year, month, 1, tzinfo=KST)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=KST)
    return start, end

def _sample_indicators() -> Dict[str, Any]:
    # TODO: Athena 연동 함수로 교체 (예: utils.athena.fetch_monthly_metrics)
    return {
        "month": "샘플",
        "kpis": {
            "visits": 1480,
            "newCustomers": 210,
            "revisitRate": 0.45,
            "couponUseRate": 0.18,
            "challengeJoin": 96
        }
    }

def get_monthly_indicators(cafe_id: int, ref_dt: Optional[datetime] = None, use_mock=True) -> Dict[str, Any]:
    if use_mock:
        return _sample_indicators()
    else:
        return fetch_monthly_metrics(cafe_id, ref_dt or datetime.now(KST))

def _generate_service_recommendations(kpis: Dict[str, Any]) -> str:
    """KPI 상황에 따라 챌린지/쿠폰 등 서비스 기능 추천 문구 생성"""
    recommendations = []
    revisit_rate = kpis.get('revisitRate', 0)
    visits = kpis.get('visits', 0)
    new_customers = kpis.get('newCustomers', 0)
    coupon_use_rate = kpis.get('couponUseRate', 0)
    challenge_join = kpis.get('challengeJoin', 0)

    # 부정적 신호
    if revisit_rate < 0.4:
        recommendations.append("재방문율이 낮으므로 기존 고객을 위한 재방문 유도 쿠폰 이벤트를 진행하세요.")
    if new_customers < 200:
        recommendations.append("신규 고객 유입이 적으니 시즌 한정 메뉴나 이벤트를 주제로 한 챌린지를 개설하세요.")
    if coupon_use_rate < 0.2:
        recommendations.append("쿠폰 사용률이 낮으니 매장에서 쿠폰 혜택을 더 적극적으로 안내하세요.")
    if challenge_join < 50:
        recommendations.append("챌린지 참여율이 낮으니 참여 조건을 완화하거나 보상을 강화해보세요.")

    # 긍정적 신호
    if revisit_rate >= 0.6:
        recommendations.append("이번 달은 재방문율이 높아요. 지금처럼 단골 고객을 유지시켜주세요.")
    if visits >= 2000:
        recommendations.append("방문자 수가 많아 안정적인 유입을 확보했습니다. 매장 운영에 강점이 있습니다.")
    if coupon_use_rate >= 0.4:
        recommendations.append("쿠폰 사용률이 높아 혜택이 잘 활용되고 있습니다. 추가 쿠폰 이벤트도 긍정적입니다.")

    if not recommendations:
        recommendations.append("지표가 전반적으로 양호하니 현재 캠페인을 유지하며 꾸준히 고객과 소통하세요.")

    return " ".join(recommendations)

PROMETHEUS_URL = "https://loopyxyz.duckdns.org/api/v1/query"

def fetch_prometheus_metrics():
    """
    cafe_search_total 지표를 Prometheus에서 가져오기
    """
    query = 'cafe_search_total'
    resp = requests.get(PROMETHEUS_URL, params={"query": query})
    data = resp.json()

    results = []
    if data.get("status") == "success":
        for r in data["data"]["result"]:
            keyword = r["metric"].get("keyword", "unknown")
            value = r["value"][1]
            results.append({"keyword": keyword, "count": int(float(value))})

    return results

def synthesize_monthly_insight(cafe_id: int, use_mock=True, include_debug=False):
    # 1. KPI 불러오기
    indicators = get_monthly_indicators(cafe_id, use_mock=use_mock)
    kpis = indicators["kpis"]
    month_label = indicators["month"]

    # 2. 트렌드 데이터    
    menus = ensure_dict_array_from_text(fetch_menu_trends())
    features = ensure_dict_array_from_text(fetch_cafe_features())
    
    # 3. GPT 분석 실행
    return build_insight_from_data(kpis, month_label, menus, features)