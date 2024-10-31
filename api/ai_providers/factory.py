#ai_providers/factory.py
import os
from ai_providers.base import BaseSummarizer
from ai_providers.openai_summarizer import OpenAISummarizer
from ai_providers.claude_summarizer import ClaudeSummarizer

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
class SummarizerFactory:
    @staticmethod
    def create_summarizer(provider: str, api_key: str, **kwargs) -> BaseSummarizer:
        providers = {
            "openai": OpenAISummarizer,
            "claude": ClaudeSummarizer,
            # Add more providers here
        }
        
        if provider not in providers:
            raise ValueError(f"Unsupported AI provider: {provider}")
            
        return providers[provider](api_key, **kwargs)
