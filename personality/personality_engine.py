"""
Personality system for Teddy
Manages consistent personality and prompt construction.
"""

import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class TeddyPersonality:
    """Teddy's personality configuration."""
    name: str
    role: str
    identity_prompt: str
    traits: List[str]
    rules: List[str]
    communication_style: str
    age_groups: Dict[str, str]  # Age-appropriate prompts
    supported_languages: List[str]


class PersonalityEngine:
    """Manages Teddy's personality and dynamic prompt construction."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize personality engine.
        
        Args:
            config_path: Path to personality YAML file
        """
        self.personality: Optional[TeddyPersonality] = None
        if config_path:
            self.load_config(config_path)
        else:
            self._load_default_personality()
    
    def _load_default_personality(self):
        """Load default Teddy personality."""
        self.personality = TeddyPersonality(
            name="Emma",
            role="A lifelong AI friend and companion for the child",
            identity_prompt=(
                "You are Emma, a warm, kind, playful, curious, and intelligent "
                "AI companion. You are not a real human; be honest that you are "
                "an AI while remaining warm and supportive."
            ),
            traits=["Warm", "Kind", "Playful", "Curious", "Encouraging", "Patient"],
            rules=[
                "Always communicate age-appropriately.",
                "Encourage curiosity and learning.",
                "Avoid frightening or dark language.",
                "Never shame or criticize the child.",
                "Be supportive and positive.",
                "Maintain consistent personality.",
                "Remember previous interactions when relevant.",
            ],
            communication_style="Friendly, warm, and engaging. Use storytelling. Celebrate the child's interests.",
            age_groups={
                "toddler": "Use very simple words. Short sentences. Ask simple questions.",
                "preschool": "Use simple language. Repeat key words. Make it playful and fun.",
                "early_school": "Use clear language. Encourage reading. Explain concepts simply.",
                "school_age": "Use age-appropriate language. Ask thought-provoking questions. Support learning.",
                "teen": "Use respectful, mature language. Acknowledge growing independence. Be a good listener.",
            },
            supported_languages=["en", "hi"],
        )
    
    def load_config(self, config_path: str):
        """Load personality from YAML config file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self.personality = TeddyPersonality(
                name=config.get("name", "Teddy"),
                role=config.get("role", ""),
                identity_prompt=config.get("identity_prompt", ""),
                traits=config.get("traits", []),
                rules=config.get("rules", []),
                communication_style=config.get("communication_style", ""),
                age_groups=config.get("age_groups", {}),
                supported_languages=config.get("supported_languages", ["en"]),
            )
        except Exception as e:
            print(f"Error loading personality config: {e}. Using defaults.")
            self._load_default_personality()
    
    def construct_system_prompt(
        self,
        child_profile: Optional[Dict[str, Any]] = None,
        memories: Optional[List[str]] = None,
        language: str = "en",
    ) -> str:
        """
        Construct system prompt combining personality, profile, and memories.
        
        Args:
            child_profile: Child's age, name, interests, etc.
            memories: List of relevant long-term memories
            language: Language code
        
        Returns:
            Constructed system prompt
        """
        if not self.personality:
            self._load_default_personality()
        
        prompt_parts = []
        
        # 1. Basic personality
        prompt_parts.append(f"You are {self.personality.name}.")
        prompt_parts.append(f"Your role: {self.personality.role}")
        if self.personality.identity_prompt:
            prompt_parts.append("")
            prompt_parts.append("Identity and behavior:")
            prompt_parts.append(self.personality.identity_prompt.strip())
        prompt_parts.append("")
        
        # 2. Personality traits
        traits_str = ", ".join(self.personality.traits)
        prompt_parts.append(f"Your personality: {traits_str}")
        prompt_parts.append("")
        
        # 3. Communication style
        prompt_parts.append(f"Communication style: {self.personality.communication_style}")
        prompt_parts.append("")
        
        # 4. Rules
        prompt_parts.append("Important rules:")
        for rule in self.personality.rules:
            prompt_parts.append(f"- {rule}")
        prompt_parts.append("")

        # 4b. Conversation language
        if language and language != "auto":
            language_guidance = {
                "english": "Respond in simple, natural English.",
                "hindi": "Respond in simple, natural Hindi. Roman Hindi is acceptable when the child uses Roman Hindi.",
                "hinglish": "Respond naturally in Hinglish, using simple Roman Hindi and English as the child does.",
            }.get(language, f"Respond in the conversation language: {language}.")
            prompt_parts.append(f"Current conversation language: {language}. {language_guidance}")
            prompt_parts.append("Keep Emma's personality the same when the language changes.")
            prompt_parts.append("")
        
        # 5. Age-appropriate guidance
        if child_profile and "age_group" in child_profile:
            age_group = child_profile["age_group"]
            if age_group in self.personality.age_groups:
                prompt_parts.append(f"Age guidance: {self.personality.age_groups[age_group]}")
                prompt_parts.append("")
        
        # 6. Child information
        if child_profile:
            prompt_parts.append("Child information:")
            if "name" in child_profile:
                prompt_parts.append(f"- Name: {child_profile['name']}")
            if "age" in child_profile:
                prompt_parts.append(f"- Age: {child_profile['age']}")
            if "interests" in child_profile and child_profile["interests"]:
                interests = ", ".join(child_profile["interests"])
                prompt_parts.append(f"- Interests: {interests}")
            prompt_parts.append("")
        
        # 7. Relevant memories
        if memories:
            prompt_parts.append("Relevant facts you remember:")
            for memory in memories:
                prompt_parts.append(f"- {memory}")
            prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """Get personality as dictionary."""
        if not self.personality:
            self._load_default_personality()
        
        return {
            "name": self.personality.name,
            "role": self.personality.role,
            "traits": self.personality.traits,
            "communication_style": self.personality.communication_style,
        }
