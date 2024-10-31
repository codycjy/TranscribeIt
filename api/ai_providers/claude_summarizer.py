# ai_providers/claude_summarizer.py
from typing import Optional
from ai_providers.base import BaseSummarizer
from anthropic import Anthropic
from prompt import DEFAULT_PROMPT
DEFAULT_MODEL = "claude-3-haiku-20240307"


class ClaudeSummarizer(BaseSummarizer):
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, **kwargs):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = Anthropic(api_key=api_key)
        self.prompt = kwargs.get("prompt", DEFAULT_PROMPT)

    async def summarize(self, text: str, max_length: Optional[int] = 1000) -> str:
        max_length = max_length or 1000
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_length,
            messages=[{
                "role": "user",
                "content": text
            }]
        )
        return response.content[0].text

    async def is_available(self) -> bool:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=5,
                messages=[{
                    "role": "user",
                    "content": "test"
                }]
            )
            return True
        except:
            return False
