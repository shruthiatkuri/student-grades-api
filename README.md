# Student Management Database API

## 1. Clone the Project

Clone the repository and navigate into the project folder:

```bash
git clone https://github.com/shruthiatkuri/student-grades-api
cd student-grades-api
```

## 2. Create the School Database and Load the Data

Make sure your PostgreSQL Docker container is running:

```bash
docker start <your-container-name>
```

Create a database named `school` inside the running PostgreSQL container:

```bash
docker exec <container-name> psql -U <postgres-username> -c "CREATE DATABASE school;"
```

Load the database schema and seed data from `student_grades.sql`, located in the project root directory:

## Linux / macOS (Bash):
```bash
docker exec -i <container-name> psql -U <postgres-username> -d <database-name> < student_grades.sql
```
## Windows (PowerShell):

```bash
cmd /c "docker exec -i <container-name> psql -U <postgres-username> -d <database-name> < student_grades.sql"
```

This command executes the SQL statements in the file to create the required tables and populate them with the initial data.

**Note:** Replace `<container-name>` and `<postgres-username>` with your actual PostgreSQL container and postgreSQL username. 

## 3. Configure Environment Variables

Create a `.env` file in the project root directory.

Refer to `.env.example` for the required variable names and add your database connection details.

Example:

```env
DATABASE_URL=postgresql://postgres_username:your_password@localhost:5432/school
```

Replace `postgres_username` and `your_password` with your PostgreSQL credentials.


## 4. Install Dependencies

Create a virtual environment from the project root:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

## 5. Run the FastAPI Server

From the project root directory, start the development server:

```bash
fastapi dev app/main.py
```

Once the server starts, open the interactive API documentation:

- Swagger UI: http://127.0.0.1:8000/docs

Use Swagger UI to explore and test the available endpoints.

## 6. Run the Tests

The project includes 36 automated test cases written using pytest.

From the project root directory, run:

```bash
pytest tests/test_grades_api.py -v
```

Alternatively, navigate into the `tests` directory:

```bash
cd tests
pytest -v
```

The `-v` option displays the individual test names and their results.

A successful test run should report **36 passed** with no failures.

## 7. Student vs. Course Deletion — Section 3.5

The deletion rules are different for students and courses because they represent different data relationships.

**Deleting a student:**

When a student is deleted, their associated grade records should also be deleted.

A grade record belongs to a particular student. Once that student no longer exists, retaining their grades would leave unnecessary or invalid dependent records. Therefore, the API deletes the student's associated grades before deleting the student.

**Deleting a course:**

When a course has associated grade records, the API should prevent its deletion and return:

```json
{
  "detail": "Course has grades; delete them first"
}
```

The user must delete the associated grade records before deleting the course.

This approach protects important academic records. If a course is selected for deletion by mistake, the existing grades provide an opportunity to review the records and make an informed decision before permanently removing them.

- Student deletion: Automatically delete the student's associated grades.
- Course deletion: Prevent deletion while associated grades exist; require the grades to be deleted first.

This ensures that dependent records are handled appropriately and prevents accidental loss of course-related academic data.