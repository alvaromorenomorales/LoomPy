"""Placeholder protection system for preserving placeholders during translation."""

import re
from typing import Dict, Tuple


# Regex patterns for detecting different placeholder formats
PLACEHOLDER_PATTERNS = [
    # {variable} format - Python/JavaScript style
    (r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', 'brace'),
    # %(name)s format - Python named format
    (r'%\([a-zA-Z_][a-zA-Z0-9_]*\)[sdifgcr]', 'named'),
    # %s, %d, %i, %f, %g, %c, %r format - printf style
    (r'%[sdifgcr]', 'printf'),
]


def extract_placeholders(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Replace placeholders with unique tokens and return mapping.
    
    Args:
        text: Input text containing placeholders
        
    Returns:
        Tuple of (protected_text, mapping) where:
        - protected_text: Text with placeholders replaced by tokens
        - mapping: Dictionary mapping tokens to original placeholders
        
    Example:
        >>> extract_placeholders("Hello {name}, you have %s messages")
        ("Hello __PH0__, you have __PH1__ messages", {"__PH0__": "{name}", "__PH1__": "%s"})
    """
    mapping = {}
    protected_text = text
    token_counter = 0
    
    # Process each placeholder pattern
    for pattern, pattern_type in PLACEHOLDER_PATTERNS:
        # Find all matches for this pattern
        matches = list(re.finditer(pattern, protected_text))
        
        # Replace matches from right to left to preserve positions
        for match in reversed(matches):
            placeholder = match.group(0)
            token = f"__PH{token_counter}__"
            mapping[token] = placeholder
            
            # Replace the placeholder with the token
            start, end = match.span()
            protected_text = protected_text[:start] + token + protected_text[end:]
            token_counter += 1
    
    return protected_text, mapping


def restore_placeholders(text: str, mapping: Dict[str, str]) -> str:
    """
    Restore original placeholders from tokens.
    
    Args:
        text: Text with placeholder tokens
        mapping: Dictionary mapping tokens to original placeholders
        
    Returns:
        Text with original placeholders restored
        
    Example:
        >>> restore_placeholders("Hello __PH0__, you have __PH1__ messages", 
        ...                      {"__PH0__": "{name}", "__PH1__": "%s"})
        "Hello {name}, you have %s messages"
    """
    restored_text = text
    
    # Replace each token with its original placeholder
    for token, placeholder in mapping.items():
        restored_text = restored_text.replace(token, placeholder)
    
    return restored_text
