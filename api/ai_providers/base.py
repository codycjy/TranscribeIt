# ai_providers/base.py
from abc import ABC, abstractmethod
from typing import Optional

class BaseSummarizer(ABC):
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def summarize(self, text: str, max_length: Optional[int] = None) -> str:
        """Generate summary for the given text"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the API is available"""
        pass

    def preprocess_text(self, text: str) -> str:
        """Common text preprocessing"""
        return text.strip()

