from pathlib import Path

from storage import Student, StudentRecordManager


DATA_FILE = Path(__file__).parent / "data" / "students.json"


def print_header() -> None:
    print("\n" + "=" * 72)
    print("STUDENT RECORD MANAGEMENT SYSTEM")
    print("=" * 72)


def print_menu() -> None:
    print("\nSelect an option:")
    print("1. Add student")
    print("2. View all students")
    print("3. Search student")
    print("4. Update student")
    print("5. Delete student")
    print("6. View summary report")
    print("7. Exit")


def prompt_required(label: str, default: str | None = None) -> str:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        value = input(f"{label}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        print("This field is required.")


def prompt_int(label: str, min_value: int, max_value: int, default: int | None = None) -> int:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        raw_value = input(f"{label}{suffix}: ").strip()
        if not raw_value and default is not None:
            return default
        try:
            value = int(raw_value)
        except ValueError:
            print("Enter a valid number.")
            continue
        if min_value <= value <= max_value:
            return value
        print(f"Enter a value between {min_value} and {max_value}.")


def prompt_float(
    label: str,
    min_value: float,
    max_value: float,
    default: float | None = None,
) -> float:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        raw_value = input(f"{label}{suffix}: ").strip()
        if not raw_value and default is not None:
            return default
        try:
            value = float(raw_value)
        except ValueError:
            print("Enter a valid decimal number.")
            continue
        if min_value <= value <= max_value:
            return value
        print(f"Enter a value between {min_value} and {max_value}.")


def prompt_email(label: str, default: str | None = None) -> str:
    while True:
        email = prompt_required(label, default)
        if "@" in email and "." in email.split("@")[-1]:
            return email
        print("Enter a valid email address.")


def show_students(students: list[Student]) -> None:
    if not students:
        print("\nNo student records found.")
        return

    headers = [
        ("ID", 10),
        ("Name", 18),
        ("Age", 5),
        ("Grade", 10),
        ("Course", 15),
        ("Attendance", 12),
        ("Status", 18),
    ]

    print()
    print(" | ".join(title.ljust(width) for title, width in headers))
    print("-" * 104)
    for student in students:
        row = [
            student.student_id[:10].ljust(10),
            student.name[:18].ljust(18),
            str(student.age).ljust(5),
            student.normalized_grade[:10].ljust(10),
            student.course[:15].ljust(15),
            f"{student.attendance:.1f}%".ljust(12),
            student.performance_status[:18].ljust(18),
        ]
        print(" | ".join(row))


def collect_student_data(existing: Student | None = None) -> dict:
    updates = {}
    if existing is None:
        updates["student_id"] = prompt_required("Student ID")

    updates["name"] = prompt_required("Name", existing.name if existing else None)
    updates["age"] = prompt_int("Age", 5, 100, existing.age if existing else None)
    updates["grade"] = prompt_required("Grade", existing.grade if existing else None)
    updates["course"] = prompt_required("Course", existing.course if existing else None)
    updates["email"] = prompt_email("Email", existing.email if existing else None)
    updates["phone"] = prompt_required("Phone", existing.phone if existing else None)
    updates["attendance"] = prompt_float(
        "Attendance (%)",
        0,
        100,
        existing.attendance if existing else None,
    )
    return updates


def add_student(manager: StudentRecordManager) -> None:
    student_data = collect_student_data()
    student = Student.create(**student_data)
    manager.add_student(student)
    print(f"\nStudent '{student.name}' added successfully.")


def view_students(manager: StudentRecordManager) -> None:
    show_students(manager.list_students())


def search_student(manager: StudentRecordManager) -> None:
    keyword = prompt_required("Enter ID, name, grade, or course to search")
    results = manager.search_students(keyword)
    if not results:
        print("\nNo matching student found.")
        return
    show_students(results)


def update_student(manager: StudentRecordManager) -> None:
    student_id = prompt_required("Enter student ID to update")
    student = manager.get_student(student_id)
    if student is None:
        print("\nStudent ID not found.")
        return

    print("\nPress Enter to keep the current value.")
    updates = collect_student_data(existing=student)
    updated_student = manager.update_student(student_id, updates)
    print(f"\nStudent '{updated_student.name}' updated successfully.")


def delete_student(manager: StudentRecordManager) -> None:
    student_id = prompt_required("Enter student ID to delete")
    student = manager.get_student(student_id)
    if student is None:
        print("\nStudent ID not found.")
        return

    confirmation = input(f"Delete record for {student.name}? (y/n): ").strip().lower()
    if confirmation != "y":
        print("\nDelete operation cancelled.")
        return

    manager.delete_student(student_id)
    print(f"\nStudent '{student.name}' deleted successfully.")


def show_summary(manager: StudentRecordManager) -> None:
    summary = manager.get_summary()
    print("\nSUMMARY REPORT")
    print("-" * 72)
    print(f"Total Students      : {summary['total_students']}")
    print(f"Average Attendance  : {summary['average_attendance']}%")
    print(f"Honor Roll Count    : {summary['honor_roll_count']}")
    print(f"Needs Attention     : {summary['attention_count']}")
    print(
        f"Courses Covered     : {', '.join(summary['courses']) if summary['courses'] else 'N/A'}"
    )
    print(f"Grades Available    : {', '.join(summary['grades']) if summary['grades'] else 'N/A'}")
    top_student = summary["top_student"]
    if top_student:
        print(
            "Top Momentum Student: "
            f"{top_student['name']} ({top_student['student_id']}) - {top_student['status']}"
        )


def main() -> None:
    manager = StudentRecordManager(DATA_FILE)
    actions = {
        "1": add_student,
        "2": view_students,
        "3": search_student,
        "4": update_student,
        "5": delete_student,
        "6": show_summary,
    }

    while True:
        print_header()
        print_menu()
        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == "7":
            print("\nThank you for using Student Record Management System.")
            break

        action = actions.get(choice)
        if action is None:
            print("\nInvalid choice. Please select a valid option.")
            continue

        try:
            action(manager)
        except ValueError as exc:
            print(f"\nError: {exc}")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
