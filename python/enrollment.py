import json
import os
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
COURSES_FILE = os.path.join(DATA_DIR, "courses.json")
TUITION_PER_CREDIT = 300.0


@dataclass
class TimeSlot:
    days: str
    start: str
    end: str

    def overlaps(self, other: "TimeSlot") -> bool:
        if not self.days or not other.days:
            return False
        if not self._share_days(self.days, other.days):
            return False
        return self._minutes(self.start) < self._minutes(other.end) and self._minutes(other.start) < self._minutes(self.end)

    @staticmethod
    def _share_days(d1: str, d2: str) -> bool:
        tokens = ["TH", "M", "T", "W", "F", "S", "U"]
        a = d1.upper()
        b = d2.upper()
        return any(token in a and token in b for token in tokens)

    @staticmethod
    def _minutes(value: str) -> int:
        try:
            hours, minutes = map(int, value.split(":"))
            return hours * 60 + minutes
        except ValueError:
            return -1

    def __str__(self) -> str:
        return f"{self.days} {self.start}-{self.end}"


@dataclass
class Course:
    code: str
    title: str
    credits: int
    capacity: int
    time_slot: TimeSlot
    prerequisites: List[str] = field(default_factory=list)
    enrolled_students: List[str] = field(default_factory=list)

    def is_full(self) -> bool:
        return len(self.enrolled_students) >= self.capacity

    def has_student(self, student_id: str) -> bool:
        return student_id in self.enrolled_students

    def enroll_student(self, student_id: str) -> bool:
        if self.is_full() or self.has_student(student_id):
            return False
        self.enrolled_students.append(student_id)
        return True

    def remove_student(self, student_id: str) -> bool:
        if student_id in self.enrolled_students:
            self.enrolled_students.remove(student_id)
            return True
        return False

    def __str__(self) -> str:
        prereqs = ", ".join(self.prerequisites) if self.prerequisites else "None"
        return (
            f"{self.code:10} {self.title:25} Credits:{self.credits:<2} "
            f"Seats:{len(self.enrolled_students)}/{self.capacity:<2} Time:{self.time_slot} "
            f"Prerequisites:{prereqs}"
        )


@dataclass
class Student:
    id: str
    name: str
    major: str
    enrolled_courses: List[str] = field(default_factory=list)
    completed_courses: List[str] = field(default_factory=list)

    def is_enrolled(self, code: str) -> bool:
        return code in self.enrolled_courses

    def enroll(self, code: str) -> bool:
        if self.is_enrolled(code):
            return False
        self.enrolled_courses.append(code)
        return True

    def drop(self, code: str) -> bool:
        if code in self.enrolled_courses:
            self.enrolled_courses.remove(code)
            return True
        return False

    def has_completed(self, code: str) -> bool:
        return code in self.completed_courses

    def __str__(self) -> str:
        enrolled = ", ".join(self.enrolled_courses) if self.enrolled_courses else "None"
        return f"{self.id} | {self.name} | {self.major} | Enrolled: {enrolled}"


class EnrollmentSystem:
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self.courses: Dict[str, Course] = {}

    def add_student(self, student: Student) -> bool:
        if student.id in self.students:
            return False
        self.students[student.id] = student
        return True

    def get_student(self, student_id: str) -> Optional[Student]:
        return self.students.get(student_id)

    def add_course(self, course: Course) -> bool:
        if course.code in self.courses:
            return False
        self.courses[course.code] = course
        return True

    def get_course(self, course_code: str) -> Optional[Course]:
        return self.courses.get(course_code)

    def get_all_courses(self) -> List[Course]:
        return list(self.courses.values())

    def get_student_schedule(self, student_id: str) -> List[Course]:
        student = self.get_student(student_id)
        if not student:
            return []
        return [self.courses[code] for code in student.enrolled_courses if code in self.courses]

    def calculate_tuition(self, student_id: str) -> float:
        schedule = self.get_student_schedule(student_id)
        return sum(course.credits for course in schedule) * TUITION_PER_CREDIT

    def register_course(self, student_id: str, course_code: str) -> (bool, str):
        student = self.get_student(student_id)
        course = self.get_course(course_code)
        if not student:
            return False, "Student not found."
        if not course:
            return False, "Course not found."
        if student.is_enrolled(course_code):
            return False, "Already enrolled in that course."
        if course.is_full():
            return False, "Course is full."
        for prereq in course.prerequisites:
            if not student.has_completed(prereq):
                return False, f"Prerequisite not met: {prereq}."
        for current_code in student.enrolled_courses:
            current = self.get_course(current_code)
            if current and current.time_slot.overlaps(course.time_slot):
                return False, f"Schedule conflict with {current_code}."
        if not course.enroll_student(student_id):
            return False, "Could not enroll in course."
        student.enroll(course_code)
        return True, f"Enrolled in {course_code}."

    def drop_course(self, student_id: str, course_code: str) -> (bool, str):
        student = self.get_student(student_id)
        course = self.get_course(course_code)
        if not student or not course:
            return False, "Student or course not found."
        if not student.is_enrolled(course_code):
            return False, "You are not enrolled in that course."
        student.drop(course_code)
        course.remove_student(student_id)
        return True, f"Dropped {course_code}."


class DataManager:
    @staticmethod
    def ensure_data_dir():
        os.makedirs(DATA_DIR, exist_ok=True)

    @staticmethod
    def save(system: EnrollmentSystem):
        DataManager.ensure_data_dir()
        with open(STUDENTS_FILE, "w", encoding="utf-8") as out:
            json.dump([asdict(student) for student in system.students.values()], out, indent=2)
        with open(COURSES_FILE, "w", encoding="utf-8") as out:
            courses = []
            for course in system.courses.values():
                course_data = asdict(course)
                course_data["time_slot"] = asdict(course.time_slot)
                courses.append(course_data)
            json.dump(courses, out, indent=2)

    @staticmethod
    def load(system: EnrollmentSystem):
        if os.path.exists(COURSES_FILE):
            with open(COURSES_FILE, "r", encoding="utf-8") as inp:
                for course_data in json.load(inp):
                    time_slot = TimeSlot(**course_data["time_slot"])
                    course = Course(
                        code=course_data["code"],
                        title=course_data["title"],
                        credits=course_data["credits"],
                        capacity=course_data["capacity"],
                        time_slot=time_slot,
                        prerequisites=course_data.get("prerequisites", []),
                        enrolled_students=course_data.get("enrolled_students", []),
                    )
                    system.courses[course.code] = course
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r", encoding="utf-8") as inp:
                for student_data in json.load(inp):
                    student = Student(**student_data)
                    system.students[student.id] = student

    @staticmethod
    def seed_defaults(system: EnrollmentSystem):
        seed_courses = [
            Course("CS101", "Intro to Programming", 3, 30, TimeSlot("MWF", "09:00", "10:00")),
            Course("CS201", "Data Structures", 3, 25, TimeSlot("MWF", "10:00", "11:00")),
            Course("CS301", "Algorithms", 3, 25, TimeSlot("TTh", "09:00", "10:30")),
            Course("MATH101", "Calculus I", 4, 35, TimeSlot("MWF", "08:00", "09:00")),
        ]
        seed_courses[1].prerequisites = ["CS101"]
        for course in seed_courses:
            system.add_course(course)
        system.add_student(Student("STU001", "Alice Johnson", "Computer Science", completed_courses=["CS101"]))
        system.add_student(Student("STU002", "Bob Smith", "Mathematics"))


def print_course_catalog(system: EnrollmentSystem):
    print("\nCourse Catalog")
    print("Code       Title                      Credits  Seats    Time              Prerequisites")
    print("-" * 80)
    for course in system.get_all_courses():
        print(course)


def student_menu(system: EnrollmentSystem, student: Student):
    while True:
        print(f"\nStudent Menu - {student.name} ({student.id})")
        print("1) View Course Catalog")
        print("2) Register for a Course")
        print("3) Drop a Course")
        print("4) View My Schedule")
        print("5) Billing Summary")
        print("6) Edit My Profile")
        print("7) Logout")
        choice = input("Select option: ").strip()
        if choice == "1":
            print_course_catalog(system)
        elif choice == "2":
            print_course_catalog(system)
            code = input("Enter course code to register: ").strip().upper()
            success, message = system.register_course(student.id, code)
            print(message)
        elif choice == "3":
            schedule = system.get_student_schedule(student.id)
            if not schedule:
                print("You are not enrolled in any courses.")
                continue
            print("Your courses:")
            for course in schedule:
                print(f"  {course.code} - {course.title}")
            code = input("Enter course code to drop: ").strip().upper()
            success, message = system.drop_course(student.id, code)
            print(message)
        elif choice == "4":
            schedule = system.get_student_schedule(student.id)
            if not schedule:
                print("You are not enrolled in any courses.")
            else:
                print("Your schedule:")
                for course in schedule:
                    print(course)
        elif choice == "5":
            tuition = system.calculate_tuition(student.id)
            print(f"Total tuition: ${tuition:.2f}")
        elif choice == "6":
            new_name = input(f"New name [{student.name}]: ").strip()
            if new_name:
                student.name = new_name
            new_major = input(f"New major [{student.major}]: ").strip()
            if new_major:
                student.major = new_major
            print("Profile updated.")
        elif choice == "7":
            DataManager.save(system)
            print("Saved and logging out.")
            break
        else:
            print("Invalid option.")


def create_student(system: EnrollmentSystem) -> Optional[Student]:
    student_id = input("Student ID: ").strip()
    if not student_id or system.get_student(student_id):
        print("Invalid or duplicate ID.")
        return None
    name = input("Full name: ").strip()
    major = input("Major: ").strip() or "Undeclared"
    student = Student(student_id, name, major)
    system.add_student(student)
    print("Student profile created.")
    return student


def main():
    system = EnrollmentSystem()
    DataManager.load(system)
    if not system.courses:
        print("Seeding default data.")
        DataManager.seed_defaults(system)
        DataManager.save(system)

    while True:
        print("\nCourse Enrollment System")
        print("1) Login as Student")
        print("2) Exit")
        choice = input("Select option: ").strip()
        if choice == "1":
            student_id = input("Enter Student ID (or type 'new'): ").strip()
            if student_id.lower() == "new":
                student = create_student(system)
                if student:
                    student_menu(system, student)
            else:
                student = system.get_student(student_id)
                if not student:
                    print("Student not found.")
                else:
                    student_menu(system, student)
        elif choice == "2":
            DataManager.save(system)
            print("Goodbye.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
