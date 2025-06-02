import sqlite3

# اتصال به پایگاه داده یا ایجاد آن
conn = sqlite3.connect('university_system.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS Course')




# ایجاد جدول‌ها
cursor.execute('''
CREATE TABLE IF NOT EXISTS Professor (
    professor_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL UNIQUE,
    hire_date TEXT NOT NULL,
    department TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Student (
    student_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL UNIQUE,
    enrollment_year INTEGER NOT NULL,
    major TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Course (
    course_id INTEGER PRIMARY KEY,
    course_name TEXT NOT NULL,
    credits INTEGER NOT NULL,
    professor_id INTEGER NOT NULL,
    schedule TEXT NOT NULL,  -- این ستون به درستی تعریف شده است
    location TEXT NOT NULL,
    prerequisite_name TEXT DEFAULT NULL,
    FOREIGN KEY (professor_id) REFERENCES Professor(professor_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Enrollment (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL,
    grade REAL NOT NULL,
    FOREIGN KEY (enrollment_id) REFERENCES Enrollment(enrollment_id)
)
''')

conn.commit()

# عملیات‌ها
def add_student():
    student_id = int(input("Enter Student ID: "))
    first_name = input("Enter the first name: ")
    last_name = input("Enter the last name: ")
    date_of_birth = input("Enter the date of birth (YYYY-MM-DD): ")
    email = input("Enter the email: ")
    phone = input("Enter the phone number: ")
    enrollment_year = int(input("Enter the enrollment year: "))
    major = input("Enter the major: ")
    cursor.execute('''
        INSERT INTO Student (student_id, first_name, last_name, date_of_birth, email, phone, enrollment_year, major)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, first_name, last_name, date_of_birth, email, phone, enrollment_year, major))
    conn.commit()
    print("Student added successfully!")

def add_professor():
    professor_id = int(input("Enter Professor ID: "))
    first_name = input("Enter the first name: ")
    last_name = input("Enter the last name: ")
    date_of_birth = input("Enter the date of birth (YYYY-MM-DD): ")
    email = input("Enter the email: ")
    phone = input("Enter the phone number: ")
    hire_date = input("Enter the hire date (YYYY-MM-DD): ")
    department = input("Enter the department: ")
    cursor.execute('''
        INSERT INTO Professor (professor_id, first_name, last_name, date_of_birth, email, phone, hire_date, department)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (professor_id, first_name, last_name, date_of_birth, email, phone, hire_date, department))
    conn.commit()
    print("Professor added successfully!")

def add_course():
    course_id = int(input("Enter the course ID: "))  # افزودن دستی course_id
    course_name = input("Enter the course name: ")
    credits = int(input("Enter the number of credits: "))
    cursor.execute("SELECT professor_id, first_name, last_name FROM Professor")
    professors = cursor.fetchall()
    for professor in professors:
        print(f"Professor ID: {professor[0]}, Name: {professor[1]} {professor[2]}")
    professor_id = int(input("Enter the Professor ID to assign to the course: "))
    schedule = input("Enter the schedule for the course (e.g., 'Saturday 8-10'): ")
    location = input("Enter the location for the course (e.g., 'Room 101'): ")
    
    # دریافت نام پیش‌نیاز درس
    prerequisite_name = input("Enter the prerequisite course name (or leave blank if none): ")
    if prerequisite_name.strip() == "":
        prerequisite_name = None
    
    cursor.execute('''
        INSERT INTO Course (course_id, course_name, credits, professor_id, schedule, location, prerequisite_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (course_id, course_name, credits, professor_id, schedule, location, prerequisite_name))
    conn.commit()
    print("Course added successfully!")


def enroll_student():
    # دریافت شناسه دانشجو
    student_id = int(input("Enter your Student ID: "))

    # بررسی وجود دانشجو
    cursor.execute("SELECT COUNT(*) FROM Student WHERE student_id = ?", (student_id,))
    if cursor.fetchone()[0] == 0:
        print("Student ID not found. Please enter a valid ID.")
        return

    # نمایش لیست دروس
    cursor.execute("SELECT * FROM Course")
    courses = cursor.fetchall()
    if not courses:
        print("No courses available for enrollment.")
        return

    print("\nAvailable Courses:")
    print(f"{'Course ID':<10} {'Name':<20} {'Credits':<10}")
    print("-" * 40)
    for course in courses:
        print(f"{course[0]:<10} {course[1]:<20} {course[2]:<10}")

    # دریافت شناسه درس
    course_id = int(input("\nEnter the Course ID to enroll: "))

    # بررسی وجود درس
    cursor.execute("SELECT COUNT(*) FROM Course WHERE course_id = ?", (course_id,))
    if cursor.fetchone()[0] == 0:
        print("Course ID not found. Please enter a valid ID.")
        return

    # بررسی ثبت‌نام تکراری
    cursor.execute('''
        SELECT COUNT(*) FROM Enrollment 
        WHERE student_id = ? AND course_id = ?
    ''', (student_id, course_id))
    if cursor.fetchone()[0] > 0:
        print("You are already enrolled in this course.")
        return

    # ثبت‌نام دانشجو
    cursor.execute('''
        INSERT INTO Enrollment (student_id, course_id)
        VALUES (?, ?)
    ''', (student_id, course_id))
    conn.commit()
    print("Enrollment successful!")

def assign_grade():
    professor_id = int(input("Enter your Professor ID: "))
    cursor.execute('''
        SELECT Course.course_id, Course.course_name FROM Course
        WHERE professor_id = ?
    ''', (professor_id,))
    courses = cursor.fetchall()
    for course in courses:
        print(f"Course ID: {course[0]}, Name: {course[1]}")
    course_id = int(input("Enter the Course ID to grade: "))
    cursor.execute('''
        SELECT Enrollment.enrollment_id, Student.first_name, Student.last_name
        FROM Enrollment
        JOIN Student ON Enrollment.student_id = Student.student_id
        WHERE Enrollment.course_id = ?
    ''', (course_id,))
    students = cursor.fetchall()
    for student in students:
        print(f"Enrollment ID: {student[0]}, Student: {student[1]} {student[2]}")
    enrollment_id = int(input("Enter the Enrollment ID to grade: "))
    grade = float(input("Enter the grade: "))
    cursor.execute('''
        INSERT INTO Grades (enrollment_id, grade)
        VALUES (?, ?)
    ''', (enrollment_id, grade))
    conn.commit()
    print("Grade assigned successfully!")

# منوی اصلی
# منوی اصلی
def main_menu():
    while True:
        role = input("\nEnter your role (student, professor, admin) or 'exit' to quit: ").lower()
        
        if role == "admin":
            while True:
                print("\nAdmin Menu:")
                print("1. Add Student")
                print("2. Add Professor")
                print("3. Add Course")
                print("4. View Enrolled Courses")
                print("5. View Grades")
                print("6. Back to Role Menu")
                choice = input("Enter your choice: ")
                if choice == "1":
                    add_student()
                elif choice == "2":
                    add_professor()
                elif choice == "3":
                    add_course()
                elif choice == "4":
                    view_enrolled_courses()
                elif choice == "5":
                    view_grades()
                elif choice == "6":
                    break  # بازگشت به منوی نقش‌ها
                else:
                    print("Invalid choice. Try again.")
                    
        elif role == "professor":
            while True:
                print("\nProfessor Menu:")
                print("1. Assign Grade")
                print("2. Back to Role Menu")
                choice = input("Enter your choice: ")
                if choice == "1":
                    assign_grade()
                elif choice == "2":
                    break  # بازگشت به منوی نقش‌ها
                else:
                    print("Invalid choice. Try again.")
                    
        elif role == "student":
            while True:
                print("\nStudent Menu:")
                print("1. Enroll in Course")
                print("2. Back to Role Menu")
                choice = input("Enter your choice: ")
                if choice == "1":
                    enroll_student()
                elif choice == "2":
                    break  # بازگشت به منوی نقش‌ها
                else:
                    print("Invalid choice. Try again.")
                    
        elif role == "exit":
            print("Exiting the system.")
            conn.close()
            exit()
        else:
            print("Invalid role. Please try again.")

def view_enrolled_courses():
    student_id = int(input("Enter Student ID to view enrolled courses: "))

    # بررسی وجود دانشجو
    cursor.execute('SELECT COUNT(*) FROM Student WHERE student_id = ?', (student_id,))
    student_exists = cursor.fetchone()[0]
    if student_exists == 0:
        print("Student ID not found.")
        return

    # بررسی وجود ثبت‌نام
    cursor.execute('SELECT COUNT(*) FROM Enrollment WHERE student_id = ?', (student_id,))
    enrollment_exists = cursor.fetchone()[0]
    if enrollment_exists == 0:
        print("No courses enrolled.")
        return

    # واکشی دروس ثبت‌نام‌شده
    cursor.execute('''
        SELECT Course.course_id, Course.course_name, Course.schedule, Course.location
        FROM Course 
        JOIN Enrollment ON Course.course_id = Enrollment.course_id
        WHERE Enrollment.student_id = ?
    ''', (student_id,))
    courses = cursor.fetchall()

    # نمایش دروس
    if courses:
        print("\nEnrolled Courses:")
        print(f"{'Course ID':<10} {'Course Name':<20} {'Schedule':<20} {'Location':<10}")
        print("-" * 60)
        for course in courses:
            print(f"{course[0]:<10} {course[1]:<20} {course[2]:<20} {course[3]:<10}")
    else:
        print("No courses enrolled.")


def view_grades():
    professor_id = int(input("Enter Professor ID to view grades: "))
    
    # بررسی صحت professor_id
    cursor.execute(''' 
        SELECT COUNT(*) FROM Professor WHERE professor_id = ?
    ''', (professor_id,))
    professor_exists = cursor.fetchone()[0]
    
    if professor_exists == 0:
        print("Professor ID not found.")
        return
    
    cursor.execute(''' 
        SELECT Course.course_name, Student.first_name, Student.last_name, Grades.grade
        FROM Grades
        JOIN Enrollment ON Grades.enrollment_id = Enrollment.enrollment_id
        JOIN Student ON Enrollment.student_id = Student.student_id
        JOIN Course ON Enrollment.course_id = Course.course_id
        WHERE Course.professor_id = ?
    ''', (professor_id,))
    
    grades = cursor.fetchall()
    if grades:
        print("Grades:")
        for grade in grades:
            print(f"Course: {grade[0]}, Student: {grade[1]} {grade[2]}, Grade: {grade[3]}")
    else:
        print("No grades found.")

# اجرای منوی اصلی
main_menu()

# بستن اتصال به پایگاه داده
conn.close()                        