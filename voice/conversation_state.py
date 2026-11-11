"""Small state machine for child-friendly activity conversations."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


ACTIVITIES = {
    "twinkle_twinkle": {
        "type": "poem",
        "label": "Twinkle Twinkle",
        "aliases": ["twinkle", "twinkle twinkle", "twinkle star", "star poem", "twinkle poem"],
    },
    "animal_poem": {
        "type": "poem",
        "label": "an animal poem",
        "aliases": ["animal poem", "animal rhyme"],
    },
    "funny_poem": {
        "type": "poem",
        "label": "a funny poem",
        "aliases": ["funny poem", "funny rhyme"],
    },
    "bedtime_poem": {
        "type": "poem",
        "label": "a bedtime poem",
        "aliases": ["bedtime poem", "sleepy poem"],
    },
    "baby_shark": {
        "type": "song",
        "label": "Baby Shark",
        "aliases": ["baby shark", "shark song", "shark"],
    },
    "lullaby": {
        "type": "song",
        "label": "a lullaby",
        "aliases": ["lullaby", "sleep song", "bedtime song"],
    },
    "lion_story": {
        "type": "story",
        "label": "a lion story",
        "aliases": ["lion story", "lion", "jungle lion"],
    },
    "animal_story": {
        "type": "story",
        "label": "an animal story",
        "aliases": ["animal story", "animal adventure"],
    },
    "space_story": {
        "type": "story",
        "label": "a space story",
        "aliases": ["space story", "space adventure", "rocket story"],
    },
}


@dataclass
class ConversationState:
    """Context needed to interpret the child's next short response."""

    last_intent: Optional[str] = None
    awaiting_selection: bool = False
    available_choices: List[str] = field(default_factory=list)
    selected_item: Optional[str] = None
    suggested_item: Optional[str] = None
    last_activity: Optional[str] = None
    conversation_language: str = "auto"


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold().strip())


def detect_language(text: str, previous: str = "auto") -> str:
    """Detect simple English, Hindi, or Roman-Hindi/Hinglish speech patterns."""
    normalized = _normalize(text)
    if re.search(r"[\u0900-\u097f]", text):
        return "hindi"
    hindi_words = {
        "mujhe", "kya", "kyun", "kaise", "sunao", "sunaao", "kahani", "katha",
        "chanda", "chand", "hathi", "haathi", "khata", "khati", "mein", "hai", "haan", "nahi", "wala",
        "wali", "baccha", "bachcha", "ek", "ki", "ka", "ke", "aur",
    }
    english_words = {
        "the", "what", "why", "how", "tell", "story", "poem", "song", "about",
        "please", "would", "like", "is", "are", "and", "a", "an",
    }
    tokens = set(re.findall(r"[a-z]+", normalized))
    hindi_count = len(tokens & hindi_words)
    english_count = len(tokens & english_words)
    if hindi_count and english_count:
        return "hinglish"
    if hindi_count:
        return "hindi"
    if english_count:
        return "english"
    return previous if previous != "auto" else "english"


def find_activity(text: str, choices: Optional[List[str]] = None) -> Optional[str]:
    """Find a known activity, preferring longer aliases before short ones."""
    normalized = _normalize(text)
    activity_ids = choices or list(ACTIVITIES)
    matches = []
    for activity_id in activity_ids:
        activity = ACTIVITIES.get(activity_id)
        if not activity:
            continue
        for alias in activity["aliases"]:
            if re.search(rf"\b{re.escape(alias)}\b", normalized):
                matches.append((len(alias), activity_id))
    return max(matches)[1] if matches else None


def detect_activity_intent(text: str) -> Optional[str]:
    """Return the activity family requested by a short child utterance."""
    normalized = _normalize(text)
    if re.search(r"\b(poem|poetry|rhyme|rhymes|rhyming)\b", normalized):
        return "poem_request"
    if re.search(r"\b(story|katha|tale|bedtime)\b", normalized):
        return "story_request"
    if re.search(r"\b(song|sing|music|lullaby)\b", normalized):
        return "song_request"
    return None


def begin_activity(text: str, state: ConversationState) -> Optional[str]:
    """Start a selection flow and return Emma's question, if needed."""
    activity_id = find_activity(text)
    intent = detect_activity_intent(text)
    if not intent:
        return None

    state.last_intent = intent
    state.selected_item = None
    state.suggested_item = None
    if intent == "poem_request":
        state.available_choices = ["twinkle_twinkle", "animal_poem", "funny_poem", "bedtime_poem"]
        state.suggested_item = "twinkle_twinkle"
        question = "Would you like Twinkle Twinkle, an animal poem, or a funny poem?"
    elif intent == "song_request":
        state.available_choices = ["twinkle_twinkle", "baby_shark", "lullaby"]
        state.suggested_item = "baby_shark"
        question = "Which song would you like, Baby Shark, Twinkle Twinkle, or a lullaby?"
    else:
        state.available_choices = ["animal_story", "lion_story", "space_story"]
        state.suggested_item = "lion_story"
        question = "What kind of story, an animal story, a lion story, or a space story?"

    if activity_id and activity_id in state.available_choices:
        state.selected_item = activity_id
        state.awaiting_selection = False
        state.last_activity = activity_id
        return None

    state.awaiting_selection = True
    return question


def resolve_selection(text: str, state: ConversationState) -> Optional[str]:
    """Resolve yes/no, a named choice, repeat, or stop using current context."""
    normalized = _normalize(text)
    if re.search(r"\b(stop|enough|finished|done|cancel)\b", normalized):
        state.awaiting_selection = False
        return "stop"
    if re.search(r"\b(again|more|once more)\b", normalized):
        return "again" if state.last_activity else None
    if state.awaiting_selection:
        selected = find_activity(normalized, state.available_choices)
        if selected:
            state.selected_item = selected
        elif re.search(r"\b(yes|yeah|yep|sure|please|okay|ok)\b", normalized):
            state.selected_item = state.suggested_item
        elif re.search(r"\b(no|nope|not now)\b", normalized):
            if state.suggested_item in state.available_choices:
                state.available_choices.remove(state.suggested_item)
            state.suggested_item = None
            return "ask_alternative"
        else:
            return None

        state.awaiting_selection = False
        state.last_activity = state.selected_item
        return state.selected_item
    return None


def activity_prompt(activity_id: str) -> str:
    """Create a model instruction for the selected activity."""
    activity = ACTIVITIES[activity_id]
    return (
        f"The child selected {activity['label']}. Perform this {activity['type']} now. "
        "Keep it warm, age-appropriate, concise, and in Emma's personality."
    )


def activity_label(activity_id: str) -> str:
    """Return the catalog label used to find exact local activity content."""
    return ACTIVITIES[activity_id]["label"]


def alternative_question(state: ConversationState) -> str:
    """Ask for remaining choices after a rejected suggestion."""
    labels = [ACTIVITIES[item]["label"] for item in state.available_choices[:3]]
    if len(labels) == 1:
        return f"Okay. Would you like {labels[0]}?"
    return "Okay! Would you like " + ", ".join(labels[:-1]) + f", or {labels[-1]}?"
