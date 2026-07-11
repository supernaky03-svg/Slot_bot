from typing import List

def calculate_payout(bet_animals: List[str], amount: int, results: List[str]) -> int:
    """Calculates payout based strictly on rules."""
    if len(bet_animals) == 1:
        # Single bet
        target = bet_animals[0]
        count = results.count(target)
        if count == 1:
            return amount * 2
        elif count == 2:
            return amount * 3
        elif count == 3:
            return amount * 4
        return 0
        
    elif len(bet_animals) == 2:
        a1, a2 = bet_animals
        if a1 == a2:
            # Same animal double bet
            if results.count(a1) >= 2:
                return amount * 6
            return 0
        else:
            # Different animal double bet
            if a1 in results and a2 in results:
                # Ensure we handle duplicates safely. If results are [Tiger, Tiger, Chicken] and bet is [Tiger, Chicken]
                temp_results = results.copy()
                if a1 in temp_results: temp_results.remove(a1)
                if a2 in temp_results:
                    return amount * 6
            return 0
    return 0

