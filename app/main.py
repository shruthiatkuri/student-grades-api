from fastapi import FastAPI, Depends, HTTPException, Response, Query
from app.schemas import (StudentsOut, StudentCreate, StudentUpdate,
                     CoursesOut, CourseCreate, CourseUpdate,
                     GradesOut,GradeCreate, GradeUpdate,
                     StudentAverage, CourseAverage)
from app.database import get_db
from app.models import Student, Course, Grade
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

app= FastAPI(title="Students record",version="0.1.0")


# Get students list

@app.get("/students", response_model= list[StudentsOut],
         description="Retrieve students with pagination and optional name filtering.")
def list_students(
    name: str | None= Query(
        default=None,
        description="Filter students by name" 
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of students to skip. Default: 0."),
    limit: int= Query(10,ge=1, le=100,
                    description="Maximum number of students to return. Default: 100."),
    db: Session=Depends(get_db)):
     """
    Retrieve a paginated list of students.

    Args:
        name: Optional name filter. Performs a case-insensitive
            substring search against the student's full name.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return (1-100).
        db: Database session provided by the get_db dependency.

    Returns:
        list[StudentsOut]: A list of students matching the filters.

    Raises:
        HTTPException: FastAPI returns 422 if query parameters
            fail validation.
    """
     query= db.query(Student)


     if name:
        query = query.filter(Student.full_name.ilike(f"%{name}%"))
     students = query.offset(skip).limit(limit).all()
     return students
           

# Read student record

@app.get("/students/{student_id}", response_model=StudentsOut,
          description="Retrieve a student by their ID.")
def get_student(student_id:int,
                db: Session= Depends(get_db)):
    """
    Retrieve a student by their ID.

    Args:
        student_id: Unique ID of the student to retrieve.
        db: Database session provided by the get_db dependency.

    Returns:
        StudentsOut: The student matching the provided ID.

    Raises:
        HTTPException: 404 if the student does not exist.
        HTTPException: 422 if the student ID is invalid.
    """
    student= db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=404,
            detail= "student no found"
        )
    return student

# create new student record

@app.post("/students", response_model=StudentsOut, status_code= 201,
            description=" Create a new student.")
def creat_student(payload: StudentCreate,
                  db: Session= Depends(get_db)):
    """
    Create a new student.

    Args:
        payload: Student information provided in the request body.
        db: Database session provided by the get_db dependency.

    Returns:
        StudentsOut: The newly created student.

    Raises:
        HTTPException: 409 if a student with the email already exists.
        HTTPException: 422 if the request body fails validation.
    """
    student= db.query(Student).filter(
        Student.email == payload.email).first()
    if student is not None:
        raise HTTPException(status_code= 409,
                            detail= "student already exists")
    
    new_student= Student(**payload.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

#Student update

@app.patch("/students/{student_id}", response_model=StudentsOut,
           description="Partially update a student's information.")
def update_student(student_id: int,
                   payload: StudentUpdate,
                   db: Session= Depends(get_db)):
    """
    Partially update an existing student's information.

    Args:
        student_id: Unique ID of the student to update.
        payload: Fields to update. Only explicitly provided fields
            are included in the update.
        db: Database session provided by the get_db dependency.

    Returns:
        StudentsOut: The updated student information.

    Raises:
        HTTPException: 404 if the student does not exist.
        HTTPException: 409 if the new email is already used
            by another student.
        HTTPException: 422 if the request body is invalid.
    """
    student= db.get(Student, student_id)
    
    if student is None:
        raise HTTPException(
            status_code= 404,
            detail="Student not found"
        )
    update_data= payload.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_student= db.query(Student).filter(
            Student.email==update_data["email"],
            Student.student_id != student_id
        ).first()

        if existing_student is not None:
            raise HTTPException(
                status_code=409,
                detail="Email alreadyexists"
            )
        
    for field,val in update_data.items():
        setattr(student, field, val)
    db.commit()
    db.refresh(student)
    return student

# delete student
@app.delete("/students/{student_id}", status_code=204,
            description="Delete a student and all associated grades.")
def delete_student(
    student_id:int,
    db:Session= Depends(get_db)):
    """
    Delete a student and their associated grades.

    Args:
        student_id: Unique ID of the student to delete.
        db: Database session provided by the get_db dependency.

    Returns:
        None: Returns HTTP 204 when the student is successfully deleted.

    Raises:
        HTTPException: 404 if the student does not exist.
        HTTPException: 422 if the student ID is invalid.
    """
    student= db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code= 404,
            detail="student not found"
        )
    db.query(Grade).filter(
        Grade.student_id == student_id
    ).delete(synchronize_session=False)

    db.delete(student)
    db.commit()
    return Response(status_code=204)




#Course List

@app.get("/courses", 
         response_model=list[CoursesOut],
         description="Retrieve courses with pagination and optional name filtering.")
def list_courses(
    course_name:str | None= Query(
        default=None, 
        description="Filter courses by name."
    ),
    skip: int= Query(
                     default=0,
                     ge=0, description="Number of courses to skip. Default: 0."),
    limit: int= Query(
        default=5,ge=1, le=100,
        description="Maximum number of courses to return. Default: 5."),
    db:Session= Depends(get_db)
):
    """
    Retrieve a paginated list of courses with optional name filtering.

    Args:
        name: Optional course name filter. Performs a case-insensitive
            substring search.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return (1-100).
        db: Database session provided by the get_db dependency.

    Returns:
        list[CoursesOut]: A list of courses matching the filters.
    """
    query=db.query(Course)
    if course_name:
        query= query.filter(Course.course_name.ilike(f"%{course_name}%"))
    
    courses= query.offset(skip).limit(limit).all()
    
    return courses


# get one course

@app.get("/courses/{course_id}", response_model=CoursesOut,
         description="Retrieve a course by its ID.")
def get_course(course_id:int,
               db: Session= Depends(get_db)):
    """
    Retrieve a course by its ID.

    Args:
        course_id: Unique ID of the course to retrieve.
        db: Database session provided by the get_db dependency.

    Returns:
        CoursesOut: The course matching the provided ID.

    Raises:
        HTTPException: 404 if the course does not exist.
        HTTPException: 422 if the course ID is invalid.
    """
    course= db.get(Course, course_id)
    if course is None:
        raise HTTPException(
            status_code= 404,
            detail= "Course not found"
        )
    
    return course

#course create
@app.post("/courses", response_model=CoursesOut, 
          status_code= 201,
          description="Create a new course.")
def create_course(payload:CourseCreate,
                  db: Session= Depends(get_db)):
    """
    Create a new course.

    Args:
        payload: Course information submitted in the request.
        db: Database session provided by the get_db dependency.

    Returns:
        CoursesOut: The newly created course.

    Raises:
        HTTPException: 409 if the course name already exists.
        HTTPException: 422 if the request body is invalid.
    """

    existing_course = db.query(Course).filter(
        Course.course_name == payload.course_name
    ).first()

    
    if existing_course is not None:
        raise HTTPException(
            status_code= 409,
            detail="Course already exits"
        )
    
    new_course= Course(**payload.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

# update course
@app.patch("/courses/{course_id}", 
           response_model=CourseCreate,
           description="Partially update an existing course.")
def update_course(course_id: int,
                  payload:CourseUpdate,
                  db:Session= Depends(get_db)):
    """
    Partially update an existing course.

    Args:
        course_id: Unique ID of the course to update.
        payload: Course fields to update. Only explicitly provided
            fields are included in the update.
        db: Database session provided by the get_db dependency.

    Returns:
        CoursesOut: The updated course information.

    Raises:
        HTTPException: 404 if the course does not exist.
        HTTPException: 409 if the course name is already used
            by another course.
        HTTPException: 422 if the request body is invalid.
    """
    course= db.get(Course, course_id)
    if course is None:
        raise HTTPException(
            status_code= 404,
            detail="Course not found"
        )
    update_data = payload.model_dump(exclude_unset=True)

    if "course_name" in update_data:
        existing_course = db.query(Course).filter(
            Course.course_name == update_data["course_name"],
            Course.course_id != course_id
        ).first()

        if existing_course is not None:
            raise HTTPException(
                status_code=409,
                detail="Course name already exists"
            )
    for field, val in update_data.items():
        setattr(course, field, val)

    db.commit()
    db.refresh(course)
    return course

# delete a course
@app.delete("/courses/{course_id}", 
            status_code=204,
            description= "Delete a course if it has no associated grades.")
def delete_course(
    course_id:int,
    db:Session=Depends(get_db)):
    """
    Delete a course if no grades are associated with it.

    Args:
        course_id: Unique ID of the course to delete.
        db: Database session provided by the get_db dependency.

    Returns:
        None: Returns HTTP 204 when the course is successfully deleted.

    Raises:
        HTTPException: 404 if the course does not exist.
        HTTPException: 409 if the course has associated grades.
        HTTPException: 422 if the course ID is invalid.
    """

    course=db.get(Course, course_id)

    if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found"
            )

    course_grade= db.query(Grade).filter(
        Grade.course_id == course_id
    ).first()

    if course_grade is not None:
        raise HTTPException(
            status_code= 409,
            detail= "Course has grades; delete them first"
        )

    
    db.delete(course)
    db.commit()
    return Response(status_code=204)

# Get grades list
@app.get("/students/{student_id}/grades",
         response_model=list[GradesOut],
         description="Retrieve all grades belonging to a student.")
def list_grades(
    student_id:int,
    skip: int=Query(0, ge=0),
    limit: int= Query(10, ge=1, le=100),
    db: Session= Depends(get_db)
):
    """
    Retrieve a paginated list of grades belonging to a student.

    Args:
        student_id: Unique ID of the student whose grades are retrieved.
        skip: Number of grade records to skip for pagination.
        limit: Maximum number of grade records to return (1-100).
        db: Database session provided by the get_db dependency.

    Returns:
        list[GradesOut]: A list of grades belonging to the student.

    Raises:
        HTTPException: 404 if the student does not exist.
        HTTPException: 422 if the query parameters are invalid.
    """
    
    student= db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code= 404,
            detail= "student not found"
        )
    grades= db.query(Grade).filter(
        Grade.student_id == student_id
    ).offset(skip).limit(limit).all()

    return grades


#create new Grade
@app.post("/grades", response_model=GradesOut, 
          status_code= 201,
          description="Record a grade for a student in a course.")
def create_grade(payload: GradeCreate,
                 db: Session= Depends(get_db)):
    """
    Create a grade record for a student in a course.

    Args:
        payload: Student ID, course ID, and grade value.
        db: Database session provided by the get_db dependency.

    Returns:
        GradesOut: The newly created grade record.

    Raises:
        HTTPException: 400 if the student or course does not exist.
        HTTPException: 409 if the student already has a grade
            in the specified course.
        HTTPException: 422 if the request body is invalid or
            the grade is outside the allowed range.
    """

    student= db.query(Student).filter(
            Student.student_id == payload.student_id
        ).first()
    course= db.query(Course).filter(
            Course.course_id == payload.course_id 
        ).first()
    
    if student is None or course is None:
        raise HTTPException(
            status_code= 400,
            detail="Unknown student_id or course_id"
        )
    
    existing_grade = db.query(Grade).filter(
        Grade.student_id == payload.student_id,
        Grade.course_id == payload.course_id
    ).first()

    if existing_grade is not None:
        raise HTTPException(
            status_code=409,
            detail="Student already has a grade in this course"
        )
    
    new_grade=Grade(**payload.model_dump())
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return new_grade

# Update grade
@app.patch("/grades/{grade_id}", response_model=GradesOut,
           description="Update the grade value of an existing grade record.")
def update_grade(grade_id:int,
                 payload: GradeUpdate,
                 db: Session= Depends(get_db)):
    """
    Partially update an existing grade record.

    Args:
        grade_id: Unique ID of the grade record to update.
        payload: Grade information to update.
        db: Database session provided by the get_db dependency.

    Returns:
        GradesOut: The updated grade information.

    Raises:
        HTTPException: 404 if the grade record does not exist.
        HTTPException: 422 if the request body is invalid.
    """
    grade= db.get(Grade, grade_id)
    if grade is None:
        raise HTTPException(
            status_code= 404,
            detail="Grade not found"
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field,val in update_data.items():
        setattr(grade,field, val)
    db.commit()
    db.refresh(grade)
    return grade

#delete grade
@app.delete("/grades/{grade_id}", 
            status_code= 204,
            description="Delete a grade record by its ID.")
def delete_grade(grade_id:int,
                 db: Session= Depends(get_db)):
    """
    Delete an existing grade record.

    Args:
        grade_id: Unique ID of the grade record to delete.
        db: Database session provided by the get_db dependency.

    Returns:
        None: Returns HTTP 204 when the grade is successfully deleted.

    Raises:
        HTTPException: 404 if the grade record does not exist.
        HTTPException: 422 if the grade ID is invalid.
    """
    grade=db.get(Grade, grade_id)
    if grade is None:
        raise HTTPException(
            status_code=404,
            detail= "Grade not found"
        )
    db.delete(grade)
    db.commit()
    return Response(status_code=204)


@app.get("/reports/student-averages", response_model= list[StudentAverage],
            description="Retrieve the average grade and number of courses taken by each student.")
def student_average(db: Session= Depends(get_db)):
    """
    Retrieve the average grade and number of courses taken by each student.

    Args:
        db: Database session provided by the get_db dependency.

    Returns:
        list[StudentAverage]: A list containing each student's ID, full name,
        average grade rounded to two decimal places, and number of grades recorded.

    Notes:
        Students without any grades are excluded from the report.
        Results are ordered by student ID.
    """

    rows = (
    db.query(
        Student.student_id,
        Student.full_name,
        func.round(func.avg(Grade.grade), 2).label("average_grade"),
        func.count(Grade.grade_id).label("courses_taken"),
    )
    .join(Grade, Grade.student_id == Student.student_id)
    .group_by(Student.student_id, Student.full_name)
    .order_by(Student.student_id)
    .all()
)
    return rows

@app.get(
    "/reports/course-averages",
    response_model=list[CourseAverage],
    description="Retrieve the average grade and number of students graded for each course."
)
def get_course_averages(db: Session = Depends(get_db)):
    """
    Retrieve the average grade and number of students graded for each course.

    Args:
        db: Database session provided by the get_db dependency.

    Returns:
        list[CourseAverage]: A list containing each course's ID, course name,
        average grade rounded to two decimal places, and number of distinct
        students who received a grade.

    Notes:
        Courses without any grades are excluded from the report.
    """

    results = (
        db.query(
            Course.course_id,
            Course.course_name,
            func.round(func.avg(Grade.grade), 2).label("average_grade"),
            func.count(distinct(Grade.student_id)).label("students_graded")
        )
        .join(Grade, Course.course_id == Grade.course_id)
        .group_by(Course.course_id, Course.course_name)
        .all()
    )

    return results