from openai_backup import OpenAI

client = OpenAI()

def run_gpt_analysis(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant for cafe insights."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content
