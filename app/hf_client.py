import requests
from typing import Any
#Out of use: Moved to OpenAI model
HF_API = "https://router.huggingface.co/models/{}"


class HFClient:
    def __init__(self, hf_token: str, model_name: str):
        self.model = model_name
        self.headers = {
            "Authorization": f"Bearer {hf_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def generate(self, prompt: str, max_tokens: int = 256) -> Any:
        url = HF_API.format(self.model)
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "do_sample": False,  # IMPORTANT: stability
            },
        }

        r = requests.post(url, headers=self.headers, json=payload, timeout=60)

        if r.status_code == 503:
            return {"error": "Model is loading, try again shortly"}

        if r.status_code >= 400:
            return {"error": f"HF error {r.status_code}: {r.text}"}

        return r.json()
