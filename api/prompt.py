# ai_providers/factory.py
DEFAULT_PROMPT = """ 
Please summarize and restructure the following video transcription. This is a speech-to-text content that may contain verbal fillers, repetitions, and colloquial expressions.

Processing Requirements:

1. Content Cleanup:
- Remove verbal fillers and redundancies (e.g., "um", "uh", "like", "you know")
- Convert spoken language to proper written form
- Correct potential transcription errors and punctuation
- Maintain accuracy of original information and key messages

2. Output Structure:
[Executive Summary - Core message in 100 words or less]

[Detailed Summary]
- Context/Background:
- Key Points: (bullet points ordered by importance)
- Detailed Discussion: (organized chronologically or logically)
- Conclusions/Recommendations: (if any)

3. Special Annotations:
- Highlight important data points, numbers, and key terms
- Mark uncertain or ambiguous content with [?]
- Preserve significant quotes or case studies
- Note any technical terms or industry-specific jargon

4. Quality Guidelines:
- Maintain logical flow and coherence
- Preserve technical accuracy
- Flag any unclear audio segments
- Keep original speaker's intent and tone
- Note timestamps for crucial points [HH:MM:SS]

Please apply these requirements to the following transcription:

[Paste transcription here]
"""

DEFAULT_PROMPT_SHORT = """
Please summarize this video transcription, keeping in mind this is speech-to-text content.

1. Provide:
- A 2-3 sentence overview
- Key points (max 5)
- Main takeaways

2. While summarizing:
- Remove filler words ("um", "like", "you know")
- Convert casual speech to clear written form
- Maintain key terms and data points
- Mark unclear segments with [?]
- Note speaker changes [Speaker A/B] if multiple speakers

Format:

OVERVIEW:
[Brief summary]

KEY POINTS:
• [Point 1]
• [Point 2]
...

MAIN TAKEAWAYS:
1. [Takeaway 1]
2. [Takeaway 2]

Transcription:
[Paste content here]
"""
