# ai_providers/openai_summarizer.py
from typing import Optional, Dict, Any
from openai import OpenAI
from prompt import DEFAULT_PROMPT
from ai_providers.base import BaseSummarizer

DEFAULT_MODEL = "gpt-3.5-turbo"


class OpenAISummarizer(BaseSummarizer):
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, **kwargs):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.prompt = kwargs.get("prompt", DEFAULT_PROMPT)

    async def summarize(self, text: str, max_length: Optional[int] = 1000) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": text}
            ],
            max_tokens=max_length
        )
        if response.choices[0].message.content is not None:
            return response.choices[0].message.content
        raise Exception("Failed to summarize the text")

    async def is_available(self) -> bool:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except:
            return False
