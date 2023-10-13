from dataclasses import dataclass
import datetime

from .Student import Student 

@dataclass
class Submission:
    link: int 
    when: datetime.datetime
    student: Student
    problem: str
    lang: str 
    verdict: str 