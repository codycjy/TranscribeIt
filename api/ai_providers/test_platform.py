import os
import pytest
from ai_providers.openai_summarizer import OpenAISummarizer
from ai_providers.claude_summarizer import ClaudeSummarizer

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
ANTHROPIC_API_KEY = "your-anthropic-key"
TEST_TEXT = """
The quick brown fox jumps over the lazy dog. This pangram contains every letter of the English alphabet at least once. 
Pangrams are often used to display font samples and test keyboards and printers.
"""

class TestSummarizers:
    @pytest.mark.asyncio
    async def test_openai_summarizer(self):
        summarizer = OpenAISummarizer(OPENAI_API_KEY)
        
        # Test normal summary
        result = await summarizer.summarize(TEST_TEXT, max_length=100)
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Test availability
        available = await summarizer.is_available()
        assert available == True

    @pytest.mark.asyncio
    async def test_claude_summarizer(self):
        summarizer = ClaudeSummarizer(ANTHROPIC_API_KEY)
        
        # Test normal summary
        result = await summarizer.summarize(TEST_TEXT, max_length=100)
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Test availability
        available = await summarizer.is_available()
        assert available == True
