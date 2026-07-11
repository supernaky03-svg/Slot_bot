import re
from config import ANIMAL_MAP, MAX_BET_LIMIT

def parse_bet_string(text: str):
    """
    Strict parsing: Extracts known aliases and digits.
    Returns (animals_list, amount) or (None, None) if invalid.
    """
    original = text.lower()
    
    # Extract numbers
    numbers = re.findall(r'\d+', original)
    if not numbers:
        return None, None
    amount = int(numbers[0])
    
    if amount <= 0 or amount > MAX_BET_LIMIT:
        return None, None
        
    # Remove the number to check remaining string
    text_no_num = original.replace(numbers[0], " ", 1)
    
    found_animals = []
    # Greedily match known animals in the remaining string
    for alias, emoji in sorted(ANIMAL_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        while alias in text_no_num:
            found_animals.append(emoji)
            text_no_num = text_no_num.replace(alias, " ", 1)
            
    # Check if any unknown characters remain (ignoring spaces/punctuation)
    remaining_clean = re.sub(r'[\s\W_]+', '', text_no_num)
    if remaining_clean.strip():
        return None, None # Extra invalid characters present
        
    if not found_animals or len(found_animals) > 2:
        return None, None
        
    found_animals.sort() # Normalize order for double bets
    return found_animals, amount

