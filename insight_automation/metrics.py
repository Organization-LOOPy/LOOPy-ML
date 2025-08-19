from prometheus_client import Counter, generate_latest, REGISTRY, CONTENT_TYPE_LATEST

# 검색 키워드 카운터
search_keyword_counter = Counter(
    "search_keyword_count",
    "Number of searches per keyword",
    ["keyword"]
)

# 메트릭 노출 함수
def prometheus_metrics():
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
