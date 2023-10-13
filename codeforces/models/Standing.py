from dataclasses import dataclass

from .Student import Student

@dataclass
class Standing:
    rank: int 
    student: Student 
    solved: int