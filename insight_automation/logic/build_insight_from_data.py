import json
from insight_automation.utils.openai_helper import run_gpt_analysis
from insight_automation.utils.text import format_with_linebreaks


def build_insight_from_data(kpis, month, menu_trends, cafe_features):
    """
    이미 준비된 데이터(kpis, month, trends)를 받아 GPT 분석 실행
    """

    prompt = f"""
    당신은 카페 경영 인사이트를 제공하는 데이터 분석가입니다.
    다음 두 가지를 JSON으로 생성하세요.

    1. insights_text:
    - 지난달 아테나 KPI 지표를 중심으로 작성 (핵심 분석 + 실행 조언)
    - 사장님께 직접 보고하듯 자연스러운 줄글 한 단락
    - 불릿포인트, 줄바꿈 없이 이어진 문장
    - 서비스 기능 추천 반드시 포함
    - 트렌드와 모니터링 내용은 한두 문장만 덧붙여 참고 수준으로 작성
    - 한국어

    2. insights 배열:
    - 아테나 KPI 기반 핵심 결론(insights) 2~3개
    - 각 결론은 {{ "title": "짧은 요약", "detail": "구체적 설명 (수치 근거 포함)" }}

    3. 추천할 수 있는 실행 항목과 조언은 반드시 우리 서비스에서 제공하는 기능만 사용해야 합니다.
    새로운 외부 프로그램이나 우리 서비스에 없는 기능은 절대 제안하지 마세요.
    - 제공 기능 예시: 단골 고객 용 쿠폰 발급 및 사용, 포인트 알림, 챌린지 개설 및 참여, 스탬프 적립 및 관리

    4. 출력은 반드시 JSON 객체 하나로만 작성하세요.
    코드블록(````json`, ```)이나 설명 문구 없이 JSON만 반환하세요.

    {{
    "insights_text": "<아테나 KPI 중심 줄글, 끝에 트렌드/모니터링 한두 줄 첨부>",
    "insights": [
        {{"title": "주말 방문 집중", "detail": "주말 방문 비중이 60% 이상으로 집중되었습니다."}},
        {{"title": "인기 메뉴", "detail": "아메리카노와 라떼 판매가 전체의 60%를 차지했습니다."}}
    ]
    }}
    """

    raw_result = run_gpt_analysis(prompt)

    try:
        result = json.loads(raw_result)
    except Exception:
        result = {"insights_text": raw_result, "insights": []}

    # 요약 만들기
    insights_items = result.get("insights", [])
    if insights_items:
        summary_text = " ".join([f"{item.get('detail')}" for item in insights_items])
        insights_summary = format_with_linebreaks(summary_text, 20)
    else:
        insights_summary = format_with_linebreaks(result.get("insights_text", "")[:100], 20)

    return {
        "insights_text": result.get("insights_text", ""),
        "insights_summary": insights_summary,
        "insights": result.get("insights", []),
    }
