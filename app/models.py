from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func, Date
from datetime import datetime, date
Base= declarative_base()

class Student(Base):
    __tablename__ = "students"
    student_id: Mapped[int]= mapped_column("id",Integer, primary_key= True)
    full_name:Mapped[str]=mapped_column(String, nullable=False)
    email: Mapped[str]= mapped_column(String, nullable=False,unique=True)
    birth_date: Mapped[date]=mapped_column(Date)
    enrollment_date: Mapped[date]= mapped_column(Date,server_default=func.current_date(), nullable=False)

class Course(Base):
    __tablename__ = "courses"

    course_id:Mapped[int]= mapped_column("id", Integer, primary_key= True)
    course_name:Mapped[str]= mapped_column(String, nullable=False)
    instructor_name: Mapped[str]= mapped_column("instructor",String, nullable=False)
    credits: Mapped[int]= mapped_column(Integer, nullable=False)

class Grade(Base):
    __tablename__= "grades"

    grade_id: Mapped[int]= mapped_column(Integer, primary_key=True)
    student_id: Mapped[int]= mapped_column(ForeignKey("students.id",ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int]= mapped_column(ForeignKey("courses.id"), nullable=False)
    grade:Mapped[float]= mapped_column(Numeric(5,2),nullable=False)


