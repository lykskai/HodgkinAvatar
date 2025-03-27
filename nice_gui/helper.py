""" This file contains helper functions"""

def extract_response_and_mood(text):
        """
        Extracts the response text and mood from a formatted message.

        Expected format: "Response text. [Mood:X]"
        - Extracts everything before "[" as the response.
        - Extracts the value of X from "[Mood:X]" as the mood.
        
        Handles edge cases:
        - If no "[Mood:X]" is found, returns response with mood as None.
        - If the mood format is incorrect (e.g., missing "Mood:" or "]"), mood is set to None.
        - Strips extra spaces from both response and mood.

        Args:
            text (str): The input string containing a response and optional mood.

        Returns:
            tuple: (response (str), mood (str or None))
        """

        # Check if '[' exists in text
        if "[" in text:
            parts = text.split("[", 1)
            response = parts[0].strip()

            mood = None  # Default in case no mood is found
            mood_part = parts[1].split("]", 1)[0] if "]" in parts[1] else None  # Extracts 'Mood:X'

            if mood_part and "Mood:" in mood_part:
                mood = mood_part.split("Mood:", 1)[1].strip()  # Extracts 'X'
        else:
            # If no '[', treat entire text as response and mood as None
            response = text.strip()
            mood = None

        return response, mood
