""" This file contains helper functions"""

import re
from typing import List
import random
from rapidfuzz import fuzz # for fuzzy matching

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



def select_images_for_input(user_input: str, image_files: List[str], filename_keywords: dict[str, set[str]]) -> List[str]:
    """
    Selects exactly 3 image filenames based on user input.
    This function uses get_matching_images() and get_categories_from_input()

    Priority:
    1. Keyword-based image match (from filename content)
       - If 3+ images match, return 3 randomly.
       - If <3, top up with category-based matches.
    2. Category-based match (using get_categories_from_input)
       - If category match, pull 3 from those categories randomly.
       - If no keyword match, pull 3 from general categories.

    Args:
        user_input (str): The text input from the user.
        image_files (List[str]): A list of available image filenames (e.g., from static/).
        filename_keywords (dict[str, set[str]]): Dictionary mapping each filename to the set of keywords in its name.

    Returns:
        List[str]: A list of 3 image filenames to display, based on keyword or category matches.
    """

    # Get matching images!
    matched_images = get_matching_images(user_input, filename_keywords)

    if matched_images:
        if len(matched_images) >= 3:
            return random.sample(matched_images, 3)

        # Fewer than 3 keyword matches → top up with category matches
        categories = get_categories_from_input(user_input)
        category_filtered = [
            f for f in image_files
            if any(cat.lower() in f.lower() for cat in categories)
            and f not in matched_images  # avoid duplicates
        ]

        needed = 3 - len(matched_images)
        top_ups = random.sample(category_filtered, min(needed, len(category_filtered)))
        return matched_images + top_ups

    # No keyword matches at all → use general category
    categories = get_categories_from_input(user_input)
    category_filtered = [
        f for f in image_files
        if any(cat.lower() in f.lower() for cat in categories)
    ]

    return random.sample(category_filtered, min(3, len(category_filtered)))


def get_categories_from_input(user_input: str) -> list[str]:
    """
    Maps user input to one or more general image categories based on keyword matching.

    Categories include: CASUAL, FAMILY, LAB, PERSONAL, SCIENCE.
    Each category has a list of associated keywords.
    Some categories (e.g., PERSONAL) include keywords from other categories (e.g., FAMILY).

    Args:
        user_input (str): Raw user input string to analyze.

    Returns:
        list[str]: A list of 2 or more matched categories (always includes at least 'CASUAL').
    """

    text = user_input.lower()  # Normalize input for case-insensitive matching

    # --- Category-specific keyword sets ---

    # Casual: greetings and friendly phrases
    casual_keywords = [
        'hi', 'hello', 'hey', 'how are you', 'how’s it going', 'greetings',
        'what’s up', 'whats up', 'sup', 'yo', 'good morning', 'good evening',
        'howdy', 'nice to meet you', 'doing well', 'hope you’re okay', 'how are things'
    ]

    # Family-related terms (used by FAMILY and also included in PERSONAL)
    family_keywords = [
        'mother', 'mom', 'mum', 'father', 'dad', 'parent', 'parents',
        'sister', 'brother', 'siblings', 'cousin', 'aunt', 'uncle', 'grandmother',
        'grandfather', 'family', 'relatives', 'niece', 'nephew', 'kin', 'household'
    ]

    # Lab/technical environment terms
    lab_keywords = [
        'lab', 'notebook', 'experiment', 'experiments', 'microscope', 'research',
        'scientist', 'researcher', 'x-ray', 'xray', 'crystallography', 'titration',
        'chemistry', 'physics', 'nobel', 'award', 'study', 'analyze', 'pipette'
    ]

    # Personal/biographical/academic terms (includes FAMILY terms)
    personal_keywords = [
        'school', 'education', 'university', 'college', 'study', 'learning',
        'student', 'mentor', 'teacher', 'classroom', 'volunteer', 'life',
        'experience', 'inspiration', 'background', 'childhood', 'career', 'oxford'
    ] + family_keywords  # Add family-related keywords to PERSONAL category

    # Science-specific terms (molecular, biological, etc. Includes LAB terms too)
    science_keywords = [
        'insulin', 'penicillin', 'vitamin', 'molecule', 'molecules', 'protein',
        'structure', 'structural', 'electron', 'density', 'scientific', 'chemistry',
        'biology', 'bio', 'genetics', 'atoms', 'crystals', 'bonds', 'reaction',
        'pathway', 'enzyme', 'diffraction'
    ] + lab_keywords  # Add lab terms to SCIENCE category

    matched_categories = set()  # Use a set to avoid duplicates

    # Helper function to check if any keyword is in the user input
    def has_keywords(keywords):
        return any(re.search(rf'\b{kw}\b', text) for kw in keywords)

    # Check each category independently
    if has_keywords(casual_keywords):
        matched_categories.add('CASUAL')

    if has_keywords(family_keywords):
        matched_categories.add('FAMILY')

    if has_keywords(lab_keywords):
        matched_categories.add('LAB')

    if has_keywords(personal_keywords):
        matched_categories.add('PERSONAL')

    if has_keywords(science_keywords):
        matched_categories.add('SCIENCE')

    # Ensure at least one fallback category if no matches found
    if len(matched_categories) < 2:
        matched_categories.add('CASUAL')  # Always return at least CASUAL

    return list(matched_categories)


def get_matching_images(user_input: str, filename_keywords: dict[str, set[str]]) -> list[str] | None:
    """
    Matches user input to relevant image filenames using exact or fuzzy keyword overlap.

    Args:
        user_input (str): The user's input text.
        filename_keywords (dict[str, set[str]]): A mapping of image filenames to sets of keywords
                                                 extracted from their names (preprocessed once).

    Returns:
        list[str] | None: A list of filenames with matching or closely matching keywords,
                          or None if no matches are found.
    """
    text = user_input.lower()
    input_words = set(re.findall(r'\b\w+\b', text))

    matched_images = []

    for fname, keywords in filename_keywords.items():
        # Exact match
        if input_words & keywords:
            matched_images.append(fname)
            continue

        # Fuzzy match (e.g. 'cobalmine' ≈ 'cobalamin')
        for word in input_words:
            for keyword in keywords:
                if fuzz.ratio(word, keyword) > 85:  # tune threshold as needed
                    matched_images.append(fname)
                    break
            else:
                continue
            break

    if matched_images:
        print("[DEBUG]: Fuzzy match found", matched_images)

    return matched_images if matched_images else None


def build_filename_keyword_index(image_files: list[str]) -> dict[str, set[str]]:
    """
    Builds a dictionary mapping each image filename to a set of keywords
    extracted from the filename (underscored).

    Returns:
        dict: {filename: set(keywords)}
    """
    return {
        fname: set(fname.lower().rsplit('.', 1)[0].split('_'))
        for fname in image_files
    }
