import pytest


class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def default_student():
    return Student("John", "Dod", "Kuntz", 8)


def test_person_initialization(default_student):
    assert default_student.first_name == "John", "First name should be John"
    assert default_student.last_name == "Dod", "Last name should be Dod"
    assert default_student.major == "Kuntz", "Kuntz"
    assert default_student.years == 8, "Years should be 8"
