from typing import Any
from openai import OpenAI
#init saves api key and model into variables. Connects to OpenAI model, engineers and sends prompt,
#fixes max tokens and temperature. Gets answer
class LLMClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 300) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful, factual assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.2,  # stable answers
        )

        return response.choices[0].message.content.strip()
