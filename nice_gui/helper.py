""" This file contains helper functions"""

import re

def extract_response_and_mood(text):
    """
    Extracts the response text and mood from a formatted message.

    Handles multiple edge cases:
    - No mood marker
    - Malformed mood marker
    - Multiple mood markers
    - Empty input
    - Non-string input
    - Mood markers with extra whitespace
    - Mood markers in different positions
    - Input containing only a mood marker (e.g., "[Angry]")

    Args:
        text (str): The input string containing a response and optional mood.

    Returns:
        tuple: (response (str), mood (str or None))
    """
    try:
        # Allowed moods (case-insensitive)
        VALID_MOODS = {'happy', 'sad', 'angry'}

        # Ensure input is a string, otherwise convert it safely
        if not isinstance(text, str):
            text = str(text)

        # Extract mood from `[Mood:X]` or `[X]` format
        mood = None
        mood_matches = re.findall(r"\[(?:Mood:)?\s*([\w]+)\s*\]", text, re.IGNORECASE)

        for mood_option in mood_matches:
            if mood_option.lower() in VALID_MOODS:
                mood = mood_option.lower()
                break  # Stop at first valid mood

        # Remove all bracketed sections (e.g., "[Mood:Happy]", "[Random Text]")
        text = re.sub(r"\[.*?\]", "", text).strip()

        # Remove the word "response" (case-insensitive)
        text = re.sub(r"\bresponse\b", "", text, flags=re.IGNORECASE).strip()

        return text, mood

    except Exception as e:
        print(f"Warning: Error processing mood - {e}")
        return "", None  # Ensure it never crashes

