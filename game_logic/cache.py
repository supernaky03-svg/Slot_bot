import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class UserCacheData:
    balance: int
    highest_balance: int
    today_bet_times: int
    today_betted_amount: int
    user_name: str = ""

@dataclass
class Bet:
    user_id: int
    user_name: str
    animals: List[str]  # Normalized emoji array
    amount: int

class GameState:
    def __init__(self):
        self.state_lock = asyncio.Lock()
        
        self.group_id: Optional[int] = None
        self.status: str = "INACTIVE" # INACTIVE, BETTING, LOCKED
        
        self.duration: int = 60
        self.min_bet: int = 100
        self.max_bet: int = 5000000
        self.daily_amount: int = 500
        self.is_paused: bool = False
        self.is_running: bool = False
        
        self.users: Dict[int, UserCacheData] = {}
        self.bets: List[Bet] = []
        
        self.admin_cache: Dict[int, float] = {}  # user_id: timestamp
        self.cooldowns: Dict[int, float] = {}
        self.username_to_id: Dict[str, int] = {}

    def clear_round_data(self):
        self.bets.clear()
        self.users.clear()

cache = GameState()

