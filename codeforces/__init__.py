import json
import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.parent.__str__())

from pathlib import Path
from .contest_parser import ContestParser
from .contest_loader import ContestLoader
from typing import *
from db import Database
import time

from .models import *


class Codeforces:
    """Fetches data from Codeforces and stores in the database"""

    def __init__(self):
        self._db = Database()
        self._contestLoader = ContestLoader(
            json.load(open(Path(__file__).parent / "config.json"))
        )

    async def import_contest(self, gym_id: int) -> None:
        """Loads `contest_id` contest data into database"""
        contest: Contest = await ContestParser(self._contestLoader, gym_id).contest
        self._db.add_contest(contest)

    async def import_all(self) -> None:
        """Import all data from `contests.csv`"""
        self._db.reset()
        for contest_id in Contest.contests().values():
            await self.import_contest(contest_id)
            time.sleep(2)
            print("IMPORTED")

    def top_5(self, gym_id: int, group: str = "") -> List[str]:
        """Returns the top 5 students for a given contest"""

        standings: List[Standing] = self._db.get_standings(gym_id)
        if group:
            standings = list(
                filter(lambda standing: standing.student.group == group, standings)
            )

        standings.sort(key=lambda standing: standing.rank)

        return list(map(lambda standing: standing.student.name, standings[:5]))

    def solves(self, gym_id: int, group: str = "") -> List[tuple]:
        """Returns the number of solved problems """

        standings: List[Standing] = self._db.get_standings(gym_id)
        if group:
            standings = list(
                filter(lambda standing: standing.student.group == group, standings)
            )

        return list(map(lambda standing: (standing.student.name, standing.solved), standings))
    
    def attendance(self, gym_id: int, group: str = "") -> int:
        "Returns attendance of a given group or all groups for a given contest in percent"

        standings: List[Standing] = self._db.get_standings(gym_id)
        if group:
            standings = list(
                filter(lambda standing: standing.student.group == group, standings)
            )

        all_students = Student.students()
        if group:
            all_students = dict(
                filter(lambda student: student[1].group == group, all_students.items())
            )

        return [len(standings), len(all_students)]

    def not_attended(self, gym_id: int, group: str = "") -> List[str]:
        "Returns list of students name from a given group or all groups that didn't attend a contest"

        standings: List[Standing] = self._db.get_standings(gym_id)
        if group:
            standings = list(
                filter(lambda standing: standing.student.group == group, standings)
            )

        all_students = Student.students()
        if group:
            all_students = dict(
                filter(lambda student: student[1].group == group, all_students.items())
            )

        all_students_handle = set(all_students.keys())
        attended_students_handle = set(
            map(lambda standing: standing.student.handle, standings)
        )

        
        return [all_students[handle].name for handle in all_students_handle - attended_students_handle]

    def question_based_analysis(self, gym_id: int, group: str = ""):
        """Returns the number of students who solved each question"""

        contest = self._db.get_contest(gym_id)
        status = contest.status[:]

        if group:
            status = list(
                filter(lambda standing: standing.student.group == group, contest.status)
            )

        solved = []
        for problem in contest.problems:
            solved.append(
                (
                    problem,
                    len(
                        [
                            submission
                            for submission in status
                            if submission.problem == problem
                            and submission.verdict == "Accepted"
                        ]
                    ),
                )
            )

        solved.sort()

        return solved
