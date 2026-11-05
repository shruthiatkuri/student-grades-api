from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum


class StudentCreate(BaseModel):
    full_name: str
    email: EmailStr
    birth_date: date | None=None

class StudentUpdate(BaseModel):
    full_name:str | None=None
    email: EmailStr | None=None
    birth_date: date | None= None

class StudentsOut(BaseModel):
    model_config= ConfigDict(from_attributes=True)

    student_id: int
    full_name: str
    email: str
    birth_date: date | None= None
    enrollment_date: date

# course

class CoursesOut(BaseModel):
    model_config= ConfigDict(from_attributes=True)
    course_id: int
    course_name: str
    instructor_name: str
    credits: int

class CourseCreate(BaseModel):
    course_name: str
    instructor_name: str | None= None
    credits: int = Field(gt=0)

class CourseUpdate(BaseModel):
    course_name:str | None=None
    instructor_name: str | None=None
    credits: int | None= None

class GradesOut(BaseModel):
    model_config= ConfigDict(from_attributes=True)
    grade_id: int
    student_id:int
    course_id: int
    grade: float

class GradeCreate(BaseModel):
    student_id: int
    course_id: int
    grade: float= Field(ge=0,le=100)

class GradeUpdate(BaseModel):
    grade: float= Field(ge=0,le=100)


class StudentAverage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    full_name: str
    average_grade: float
    courses_taken: int

class CourseAverage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: int
    course_name: str
    average_grade: float
    students_graded: int






