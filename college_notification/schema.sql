-- schema.sql

DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS notices;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  email TEXT,
  role TEXT NOT NULL,  -- 'admin', 'faculty', or 'student'
  email_notifications_enabled INTEGER DEFAULT 0, -- 0=OFF, 1=ON
  created_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE students (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER UNIQUE NOT NULL,
  roll_no TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  date_of_birth TEXT,
  phone TEXT,
  address TEXT,
  semester INTEGER DEFAULT 1,
  is_active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now','localtime')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE courses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  course_code TEXT UNIQUE NOT NULL,
  course_name TEXT NOT NULL,
  credits INTEGER,
  semester INTEGER,
  section TEXT,
  faculty_id INTEGER,
  description TEXT,
  created_at TEXT DEFAULT (datetime('now','localtime')),
  FOREIGN KEY (faculty_id) REFERENCES users(id)
);

CREATE TABLE enrollments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  enrolled_date TEXT DEFAULT (datetime('now','localtime')),
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  UNIQUE(student_id, course_id)
);

CREATE TABLE attendance (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  attendance_date TEXT NOT NULL,
  status TEXT CHECK(status IN ('Present', 'Absent', 'Leave')),
  created_at TEXT DEFAULT (datetime('now','localtime')),
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE grades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  marks_obtained REAL,
  total_marks REAL DEFAULT 100,
  grade TEXT,
  created_at TEXT DEFAULT (datetime('now','localtime')),
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  UNIQUE(student_id, course_id)
);

CREATE TABLE sessional_marks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  section TEXT NOT NULL,
  quiz_marks REAL DEFAULT 0,
  assignment_marks REAL DEFAULT 0,
  presentation_marks REAL DEFAULT 0,
  total_sessional REAL DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now','localtime')),
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  UNIQUE(student_id, course_id)
);

CREATE TABLE pre_test_marks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  section TEXT NOT NULL,
  pre_test_marks REAL DEFAULT 0,
  total_pre_test REAL DEFAULT 10,
  remarks TEXT,
  created_at TEXT DEFAULT (datetime('now','localtime')),
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  UNIQUE(student_id, course_id)
);

CREATE TABLE notices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT,
  created_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  date TEXT NOT NULL,
  location TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE exams (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  exam_name TEXT NOT NULL,
  course_id INTEGER NOT NULL,
  faculty_id INTEGER NOT NULL,
  max_marks REAL DEFAULT 100,
  description TEXT,
  created_at TEXT DEFAULT (datetime('now','localtime')),
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  FOREIGN KEY (faculty_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE exam_marks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  exam_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  marks_obtained REAL DEFAULT 0,
  percentage REAL DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now','localtime')),
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  UNIQUE(student_id, exam_id)
);

-- Insert demo users
INSERT INTO users (username, password, email, role) VALUES ('admin', 'admin123', 'admin@college.edu', 'admin');
INSERT INTO users (username, password, email, role) VALUES ('faculty1', 'faculty123', 'faculty1@college.edu', 'faculty');
INSERT INTO users (username, password, email, role) VALUES ('student1', 'student123', 'student1@college.edu', 'student');

-- Insert demo student
INSERT INTO students (user_id, roll_no, full_name, date_of_birth, phone, semester) 
VALUES (3, 'CS2024001', 'John Doe', '2004-01-15', '9876543210', 2);

-- Insert demo courses
INSERT INTO courses (course_code, course_name, credits, semester, section, faculty_id, description)
VALUES ('CS101', 'Data Structures', 4, 2, 'A', 2, 'Fundamentals of Data Structures');
INSERT INTO courses (course_code, course_name, credits, semester, section, faculty_id, description)
VALUES ('CS102', 'Database Management', 4, 2, 'A', 2, 'Introduction to Databases');

-- Insert demo enrollment
INSERT INTO enrollments (student_id, course_id) VALUES (1, 1);
INSERT INTO enrollments (student_id, course_id) VALUES (1, 2);

-- Insert demo grades
INSERT INTO grades (student_id, course_id, marks_obtained, total_marks, grade)
VALUES (1, 1, 85, 100, 'A');
INSERT INTO grades (student_id, course_id, marks_obtained, total_marks, grade)
VALUES (1, 2, 92, 100, 'A');
