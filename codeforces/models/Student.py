from pathlib import Path
from dataclasses import dataclass
from typing import * 

@dataclass
class Student:
    name: str
    group: str  
    handle: str 
    
    @staticmethod
    def from_handle(handle: str) -> "Student":
        """Gets Student object from student's handle"""
        return Student.students()[handle.lower()]

    _students = None 
    
    @staticmethod
    def students()-> Dict[str, "Student"]:
        """Returns dict of all students with `{handle: Student}` format"""
        
        if Student._students is None:
            students: Dict[str, Student] = {} # key: handle, value = Student
            with open(Path(__file__).parent.parent / "students.csv", 'r') as file:
                for line in file.readlines()[1:]:
                    name, handle, group = map(lambda x: x.strip(), line.split(','))
                    handle = handle.lower()
                    students[handle] = Student(name=name,handle=handle,group=group)
            Student._students = students 
    
        return Student._students