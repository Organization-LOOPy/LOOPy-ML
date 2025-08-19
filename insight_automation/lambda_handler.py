import json
from datetime import datetime
from insight_automation.logic.sources.insight_monthly import synthesize_monthly_insight
from insight_automation.utils.storage import save_report_to_s3

def lambda_handler(event, context):
    # 카페 ID 예시 (실제 환경에서는 여러 카페 loop 가능)
    cafe_id = 1  
    period = datetime.now().strftime("%Y-%m-%d")

    try:
        # 인사이트 생성
        report = synthesize_monthly_insight(cafe_id=cafe_id, use_mock=False)

        # S3 저장
        save_report_to_s3(
            cafe_id=cafe_id,
            period=period,
            payload=report,
            overwrite=True
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Report generated and saved for cafe {cafe_id}",
                "report": report
            }, ensure_ascii=False)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
