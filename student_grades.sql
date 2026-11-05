--students table

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birth_date DATE,
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE
);

-- courses table

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    course_name TEXT NOT NULL,
    instructor TEXT NOT NULL,
    credits INTEGER NOT NULL CHECK ( credits > 0)
);    


-- grades table

CREATE TABLE grades (
    grade_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    grade NUMERIC NOT NULL CHECK (grade BETWEEN 0 AND 100),
    UNIQUE(student_id, course_id)
);


--insert into values students

INSERT INTO students (full_name, email, birth_date)
VALUES ('Alice Lim', 'Alice@gamil.com','2002-07-09'),
       ('Sam Josh', 'samemial@gmail.com','2001-08-20'),
       ('Fyn Kyle', 'Fnynn@gmail.com',NULL);


--insert into values courses tables

INSERT INTO courses (course_name,instructor, credits)
VALUES ('History', 'James',4),
       ('Statistics', 'Avi', 4),
       ('Algorithms', 'Kay', 3);


--insert into values grades table

INSERT INTO grades (student_id, course_id, grade)
VALUES (1, 1, 89),
       (2,2,90),
       (3,3,78),
       (2,1,80);


