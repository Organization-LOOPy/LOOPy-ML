import logging
from insight_automation.logic.sources.insight_monthly import synthesize_monthly_insight
from insight_automation.utils.storage import save_report_to_s3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_and_store_insight(cafe_id: int, period: str, use_mock: bool = True):
    try:
        logger.info(f"[Scheduler] cafe_id={cafe_id}, period={period}, use_mock={use_mock}")

        # GPT 인사이트 생성
        report = synthesize_monthly_insight(cafe_id, use_mock=use_mock)

        payload = {
            "ok": True,
            "cafeId": cafe_id,
            "period": period,
            "report": report,
        }

        # S3 저장
        save_report_to_s3(cafe_id, period, payload, overwrite=True)

        logger.info(f"[Scheduler] ✅ Insight stored in S3 for cafe {cafe_id}, period {period}")
        return payload

    except Exception as e:
        logger.exception("[Scheduler] Insight generation failed")
        raise

if __name__ == "__main__":
    generate_and_store_insight(1, "2025-08", use_mock=True)
