import sys 
from pathlib import Path
from typing import *
sys.path.append(Path(__file__).parent.parent.__str__())

from datetime import datetime
import json
import sqlite3

from codeforces.models import *

class Database:
    """ Database Connection """
    
    def __init__(self, db_path=Path(__file__).parent / "db.sqlite3") -> None: 
        self._connection = sqlite3.connect(db_path)
        self._cursor = self._connection.cursor()
        
        with open(Path(__file__).parent / "statements.json") as f:
            self.STATEMENTS: Dict[str, str] = json.load(f)

    def reset(self) -> None:
        for table in ["Problems", "Status", "Standings"]:
            self._create_table(table)
            
    def _date_to_str(self, date: datetime) -> str:
        """ Converts a datetime object to string """
        return date.strftime('%Y-%m-%d %H:%M:%S')
    
    def _str_to_date(self, date: str) -> datetime:
        """ Converts a string to datetime object """
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    
    def _drop_table(self, table: str) -> None:
        """ Drops a table with name `table_name` from database """
        self._cursor.execute(self.STATEMENTS["DROP_TABLE"].format(table=table))
        self._connection.commit()
    
    def _create_table(self, table: str) -> None:
        """ Creates a table with name `table_name` in database """
        self._drop_table(table)
        self._cursor.execute(self.STATEMENTS["CREATE_" + table.upper() + "_TABLE"])
        self._connection.commit()
    
    def get_contest(self, gym_id: int) -> Contest:
        """ Returns a contest with id `gym_id`"""
        return Contest(
            gym_id=gym_id,
            problems=self._get_problems(gym_id),
            status=self._get_status(gym_id),
            standings=self.get_standings(gym_id)
        )
    
    def add_contest(self, contest: Contest) -> None:
        """ Adds a contest to database """
        
        for problem in contest.problems:
            self._add_problem(contest.gym_id, problem)
            
        self._add_status(contest.gym_id, contest.status)
            
        for standing in contest.standings:
            self._add_standing(contest.gym_id, standing)
        
        self._connection.commit()
       
    def get_standings(self, gym_id: int) -> List[Standing]:
        """ Returns a list of standings in a contest """
        
        self._cursor.execute(self.STATEMENTS["GET_STANDINGS"].format(contest=gym_id))
        
        return [
            Standing(rank, Student.from_handle(handle), solved)
                for _, rank, handle, solved in self._cursor.fetchall()
        ]
    
    def _add_standing(self, gym_id: int, standing: Standing) -> None:
        """ Adds a standing to a contest """
        self._cursor.execute(self.STATEMENTS["ADD_STANDING"].format(
            contest=gym_id,
            rank=standing.rank,
            student=standing.student.handle,
            solved=standing.solved,
        ))
    
    def _get_problems(self, gym_id: int) -> List[str]:
        """ Returns a list of problems in a contest """
        self._cursor.execute(self.STATEMENTS["GET_PROBLEMS"].format(contest=gym_id))
        return list(map(lambda question: question[1], self._cursor.fetchall()))
    
    def _add_problem(self, contest_id: int, problem: str) -> None:
        """ Adds a problem to a contest """
        self._cursor.execute(self.STATEMENTS["ADD_PROBLEM"].format(contest=contest_id, problem=problem))
    
    def _add_status(self, gym_id: int, status: List[Submission]) -> None:
        """ Adds a list of submissions to a contest status"""
        
        for submission in status:
            self._cursor.execute(self.STATEMENTS["ADD_STATUS"].format(
                contest=gym_id,
                link=submission.link,
                time=self._date_to_str(submission.when),
                student=submission.student.handle,
                problem=submission.problem,
                lang=submission.lang,
                verdict=submission.verdict,
            ))
    
    def _get_status(self, gym_id: int) -> List[Submission]:
        """ Returns a list of submissions in a contest"""
        
        self._cursor.execute(
            self.STATEMENTS["GET_STATUS"].format(contest=gym_id)
        )
        
        return [
            Submission(
                link=link,
                when=self._str_to_date(time),
                student=Student.from_handle(student), 
                problem=problem,
                lang=lang,
                verdict=verdict
            )
            for _, link, time, student, problem, lang, verdict in self._cursor.fetchall()
        ]