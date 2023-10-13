from datetime import datetime
from typing import List
from bs4 import BeautifulSoup, Tag

from .models import *
from .contest_loader import ContestLoader


class ContestParser:
    """Parse a contest with a given `gym_id`"""

    def __init__(self, contestLoader: ContestLoader, gym_id: int) -> None:
        self.contestLoader = contestLoader
        self.gym_id = gym_id
        self._contest = None

    @property
    async def contest(self) -> Contest:
        """
        Parses contest problems, standings and status page and returns a contest object
        """

        await self.contestLoader.login()

        if self._contest == None:
            # pages
            problems_page = BeautifulSoup(
                await self.contestLoader.get_problems_page(self.gym_id),
                features="html.parser",
            )
            status_page = BeautifulSoup(
                await self.contestLoader.get_status_page(self.gym_id),
                features="html.parser",
            )
            standings_page = BeautifulSoup(
                await self.contestLoader.get_standings_page(self.gym_id),
                features="html.parser",
            )

            status = []
            for page in range(1, self._get_number_of_status_pages(status_page) + 1):
                status_page = BeautifulSoup(
                    await self.contestLoader.get_status_page(self.gym_id, page),
                    features="html.parser",
                )
                status.extend(self._get_contest_status(status_page))

            standings = []
            for page in range(
                1, self._get_number_of_standings_pages(standings_page) + 1
            ):
                standings_page = BeautifulSoup(
                    await self.contestLoader.get_standings_page(self.gym_id, page=page),
                    features="html.parser",
                )
                standings.extend(self._get_contest_standings(standings_page))

            self._contest = Contest(
                gym_id=self.gym_id,
                problems=self._get_problems(problems_page),
                standings=standings,
                status=status,
            )

        return self._contest

    def _get_number_of_status_pages(self, status_page: BeautifulSoup) -> int:
        """Get the number of pages"""

        pages: Tag = status_page.find_all("span", class_="page-index")

        number_of_pages = 0

        if not pages:
            number_of_pages = 1
        else:
            number_of_pages = len(pages)

        return number_of_pages

    def _get_number_of_standings_pages(self, standings_page: BeautifulSoup) -> int:
        """Get the number of stadings pages"""

        pages: Tag = standings_page.find_all("span", class_="page-index")

        number_of_pages = 0

        if not pages:
            number_of_pages = 1
        else:
            number_of_pages = len(pages)

        return number_of_pages

    def _get_problems(self, problems_page: BeautifulSoup) -> List[str]:
        """
        Parses contest problems page and returns list of the questions name
        """
        table: Tag = problems_page.find("table", class_="problems")
        rows: Tag = table.find_all("tr")[1:]

        problems: List[str] = []
        for row in rows:
            if row.find("td").find("a").find("img"):
                break
            problem = row.find("td").find("a").string.strip()
            problems.append(problem)

        return problems

    def _get_contest_status(self, status_page: BeautifulSoup) -> List[Submission]:
        """
        Parses contest status page and returns list of Submission Objects
        """
        table: Tag = status_page.find("table", class_="status-frame-datatable")
        rows: Tag = table.find_all("tr")

        students: dict[str, Student] = Student.students()
        status: List[Submission] = []

        for row in rows:
            datas: List[Tag] = row.find_all("td")

            is_header = not datas
            handle = not is_header and datas[2].find("a").string.lower()

            if is_header or (handle not in students):
                continue

            link: int = int(datas[0].text)
            when: datetime = datetime.strptime(datas[1].text.strip(), "%b/%d/%Y %H:%M")
            student: Student = students[handle]
            problem: str = datas[3].text.strip().split("-")[0].strip()
            lang: str = datas[4].text.strip()
            verdict: str = datas[5].text.strip()

            submission = Submission(
                link=link,
                when=when,
                student=student,
                problem=problem,
                lang=lang,
                verdict=verdict,
            )

            status.append(submission)

        return status

    def _get_contest_standings(self, standings_page: BeautifulSoup) -> List[Standing]:
        table = standings_page.find("table", class_="standings")
        rows: List[Tag] = table.find_all("tr")

        students = Student.students()
        standings: List[Standing] = []

        for row in rows:
            datas: List[Tag] = row.find_all("td")

            is_header = not datas
            is_footer = datas and not datas[1].find("a")
            is_out_of_contest = datas and not datas[0].string.strip()

            if is_header or is_footer or is_out_of_contest:
                continue

            handle = datas[1].find("a").string.lower()
            if handle in students:
                rank = int(datas[0].string)
                student = students[handle]
                solved = int(datas[2].string)
                standing = Standing(rank=rank, student=student, solved=solved)
                standings.append(standing)

        return standings
