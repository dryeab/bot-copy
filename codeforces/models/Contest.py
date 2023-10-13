from pathlib import Path
import csv
from typing import *
from dataclasses import dataclass

from .Submission import Submission
from .Standing import Standing

@dataclass 
class Contest:
    gym_id: int 
    problems: List[str]
    status: List[Submission]
    standings: List[Standing]
    
    _contests = None 
    
    @staticmethod
    def contests()-> Dict[str, int]:
        """Returns contests info from `../contests.csv` file"""
        
        if Contest._contests is None:
            with open(Path(__file__).parent.parent / "contests.csv", 'r') as file:
                Contest._contests = {
                    contest_name: int(gym_id) for contest_name, gym_id in csv.reader(file)
                }
    
        return Contest._contests