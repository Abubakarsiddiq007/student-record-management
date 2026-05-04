import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
GRADE_POINTS = {
    "A+": 4.3,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D": 1.0,
    "E": 0.5,
    "F": 0.0,
}
MAX_GRADE_POINTS = max(GRADE_POINTS.values())


def normalize_grade(grade: str) -> str:
    return grade.strip().upper()


def get_grade_points(grade: str) -> float:
    return GRADE_POINTS.get(normalize_grade(grade), 2.5)


def get_student_status(attendance: float, grade: str) -> str:
    points = get_grade_points(grade)
    if attendance >= 92 and points >= 3.7:
        return "Honor Roll"
    if attendance >= 80 and points >= 3.0:
        return "Consistent"
    if attendance < 60 or points <= 1.0:
        return "Critical"
    return "Needs Attention"


def get_student_score(attendance: float, grade: str) -> float:
    grade_score = (get_grade_points(grade) / MAX_GRADE_POINTS) * 100
    return round((attendance * 0.65) + (grade_score * 0.35), 2)


@dataclass
class Student:
    student_id: str
    name: str
    age: int
    grade: str
    course: str
    email: str
    phone: str
    attendance: float
    created_at: str
    updated_at: str

    @classmethod
    def create(
        cls,
        student_id: str,
        name: str,
        age: int,
        grade: str,
        course: str,
        email: str,
        phone: str,
        attendance: float,
    ) -> "Student":
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        return cls(
            student_id=student_id,
            name=name,
            age=age,
            grade=grade,
            course=course,
            email=email,
            phone=phone,
            attendance=attendance,
            created_at=timestamp,
            updated_at=timestamp,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        return cls(
            student_id=str(data["student_id"]),
            name=str(data["name"]),
            age=int(data["age"]),
            grade=str(data["grade"]),
            course=str(data["course"]),
            email=str(data["email"]),
            phone=str(data["phone"]),
            attendance=float(data["attendance"]),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def normalized_grade(self) -> str:
        return normalize_grade(self.grade)

    @property
    def performance_status(self) -> str:
        return get_student_status(self.attendance, self.grade)

    @property
    def performance_score(self) -> float:
        return get_student_score(self.attendance, self.grade)


class StudentRecordManager:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self.db_path.write_text("[]", encoding="utf-8")

    def _load_students(self) -> list[Student]:
        try:
            raw_data = json.loads(self.db_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Could not read student database because the JSON is invalid: {exc}"
            ) from exc

        if not isinstance(raw_data, list):
            raise ValueError("Student database must contain a list of records.")

        students = [Student.from_dict(item) for item in raw_data]
        return sorted(students, key=lambda student: student.student_id.lower())

    def _save_students(self, students: list[Student]) -> None:
        serialized = [student.to_dict() for student in students]
        self.db_path.write_text(
            json.dumps(serialized, indent=4),
            encoding="utf-8",
        )

    def list_students(self) -> list[Student]:
        return self._load_students()

    def get_student(self, student_id: str) -> Student | None:
        for student in self._load_students():
            if student.student_id.lower() == student_id.lower():
                return student
        return None

    def add_student(self, student: Student) -> None:
        students = self._load_students()
        if any(
            existing.student_id.lower() == student.student_id.lower()
            for existing in students
        ):
            raise ValueError("A student with this ID already exists.")

        students.append(student)
        self._save_students(students)

    def update_student(self, student_id: str, updates: dict) -> Student:
        students = self._load_students()
        for index, student in enumerate(students):
            if student.student_id.lower() == student_id.lower():
                student.name = updates.get("name", student.name)
                student.age = updates.get("age", student.age)
                student.grade = updates.get("grade", student.grade)
                student.course = updates.get("course", student.course)
                student.email = updates.get("email", student.email)
                student.phone = updates.get("phone", student.phone)
                student.attendance = updates.get("attendance", student.attendance)
                student.updated_at = datetime.now().strftime(TIMESTAMP_FORMAT)
                students[index] = student
                self._save_students(students)
                return student

        raise ValueError("Student ID not found.")

    def delete_student(self, student_id: str) -> Student:
        students = self._load_students()
        filtered_students = [
            student
            for student in students
            if student.student_id.lower() != student_id.lower()
        ]

        if len(filtered_students) == len(students):
            raise ValueError("Student ID not found.")

        deleted_student = next(
            student
            for student in students
            if student.student_id.lower() == student_id.lower()
        )
        self._save_students(filtered_students)
        return deleted_student

    def search_students(self, keyword: str) -> list[Student]:
        normalized_keyword = keyword.strip().lower()
        return [
            student
            for student in self._load_students()
            if normalized_keyword in student.student_id.lower()
            or normalized_keyword in student.name.lower()
            or normalized_keyword in student.course.lower()
            or normalized_keyword in student.grade.lower()
        ]

    def get_summary(self) -> dict:
        students = self._load_students()
        total_students = len(students)
        average_attendance = (
            sum(student.attendance for student in students) / total_students
            if total_students
            else 0.0
        )
        courses = sorted({student.course for student in students})
        grades = sorted({student.grade for student in students})
        honor_roll_students = [
            student for student in students if student.performance_status == "Honor Roll"
        ]
        attention_students = [
            student
            for student in students
            if student.performance_status in {"Needs Attention", "Critical"}
        ]
        top_student = (
            max(students, key=lambda student: student.performance_score)
            if students
            else None
        )

        return {
            "total_students": total_students,
            "average_attendance": round(average_attendance, 2),
            "courses": courses,
            "grades": grades,
            "honor_roll_count": len(honor_roll_students),
            "attention_count": len(attention_students),
            "top_student": {
                "name": top_student.name,
                "student_id": top_student.student_id,
                "course": top_student.course,
                "status": top_student.performance_status,
                "score": top_student.performance_score,
            }
            if top_student
            else None,
            "attention_students": [
                {
                    "name": student.name,
                    "student_id": student.student_id,
                    "status": student.performance_status,
                    "attendance": student.attendance,
                }
                for student in attention_students[:5]
            ],
        }

    def export_to_csv(self, csv_path: Path) -> Path:
        students = self._load_students()
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                [
                    "Student ID",
                    "Name",
                    "Age",
                    "Grade",
                    "Course",
                    "Email",
                    "Phone",
                    "Attendance",
                    "Status",
                    "Performance Score",
                    "Created At",
                    "Updated At",
                ]
            )
            for student in students:
                writer.writerow(
                    [
                        student.student_id,
                        student.name,
                        student.age,
                        student.normalized_grade,
                        student.course,
                        student.email,
                        student.phone,
                        f"{student.attendance:.2f}",
                        student.performance_status,
                        f"{student.performance_score:.2f}",
                        student.created_at,
                        student.updated_at,
                    ]
                )

        return csv_path
