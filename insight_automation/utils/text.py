def format_with_linebreaks(text: str, interval: int = 20) -> str:
    """주어진 텍스트를 interval 글자마다 줄바꿈 추가"""
    return "\n".join([text[i:i+interval] for i in range(0, len(text), interval)])
