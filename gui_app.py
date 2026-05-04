from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from storage import Student, StudentRecordManager


DATA_FILE = Path(__file__).parent / "data" / "students.json"
STATUS_OPTIONS = [
    "All Statuses",
    "Honor Roll",
    "Consistent",
    "Needs Attention",
    "Critical",
]


class StudentRecordGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.manager = StudentRecordManager(DATA_FILE)
        self.selected_student_id: str | None = None

        self.root.title("Student Success Studio")
        self.root.geometry("1320x780")
        self.root.minsize(1160, 700)
        self.root.configure(bg="#f1ecdf")

        self._create_styles()
        self._build_layout()
        self.refresh_students()

    def _create_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f1ecdf")
        style.configure("Panel.TFrame", background="#fbf7ef", relief="flat")
        style.configure(
            "Hero.TLabel",
            background="#f1ecdf",
            foreground="#16232a",
            font=("Georgia", 24, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#f1ecdf",
            foreground="#526168",
            font=("Segoe UI", 10),
        )
        style.configure(
            "PanelTitle.TLabel",
            background="#fbf7ef",
            foreground="#16232a",
            font=("Segoe UI Semibold", 12),
        )
        style.configure(
            "Field.TLabel",
            background="#fbf7ef",
            foreground="#24333a",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Primary.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(14, 10),
        )
        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=(12, 9),
        )
        style.configure(
            "Treeview",
            rowheight=30,
            font=("Segoe UI", 10),
            background="#ffffff",
            fieldbackground="#ffffff",
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI Semibold", 10),
            background="#d7e3dd",
            foreground="#16232a",
        )

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, style="App.TFrame", padding=(26, 24, 26, 12))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="Student Success Studio", style="Hero.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text=(
                "A smarter student record dashboard with performance bands, attention alerts, "
                "and CSV export for desktop workflow demos."
            ),
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        content = ttk.Frame(self.root, style="App.TFrame", padding=(26, 8, 26, 26))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        self._build_form_panel(content)
        self._build_dashboard_panel(content)

    def _build_form_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=20)
        panel.grid(row=0, column=0, sticky="nsw", padx=(0, 16))

        ttk.Label(panel, text="Student Command Form", style="PanelTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            panel,
            text="Create and update records from one place.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 14))

        self.form_vars = {
            "student_id": tk.StringVar(),
            "name": tk.StringVar(),
            "age": tk.StringVar(),
            "grade": tk.StringVar(),
            "course": tk.StringVar(),
            "email": tk.StringVar(),
            "phone": tk.StringVar(),
            "attendance": tk.StringVar(),
        }

        fields = [
            ("Student ID", "student_id"),
            ("Name", "name"),
            ("Age", "age"),
            ("Grade", "grade"),
            ("Course", "course"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Attendance %", "attendance"),
        ]

        for row_index, (label, key) in enumerate(fields, start=2):
            ttk.Label(panel, text=label, style="Field.TLabel").grid(
                row=row_index,
                column=0,
                sticky="w",
                pady=6,
            )
            ttk.Entry(
                panel,
                textvariable=self.form_vars[key],
                width=30,
                font=("Segoe UI", 10),
            ).grid(row=row_index, column=1, sticky="ew", pady=6, padx=(12, 0))

        button_frame = ttk.Frame(panel, style="Panel.TFrame")
        button_frame.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        for column in range(2):
            button_frame.columnconfigure(column, weight=1)

        ttk.Button(
            button_frame,
            text="Add Student",
            style="Primary.TButton",
            command=self.add_student,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(
            button_frame,
            text="Update Student",
            style="Primary.TButton",
            command=self.update_student,
        ).grid(row=0, column=1, sticky="ew")
        ttk.Button(
            button_frame,
            text="Delete Selected",
            style="Secondary.TButton",
            command=self.delete_student,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(8, 0))
        ttk.Button(
            button_frame,
            text="Clear Form",
            style="Secondary.TButton",
            command=self.clear_form,
        ).grid(row=1, column=1, sticky="ew", pady=(8, 0))

        self.form_hint = tk.StringVar(
            value="Select a student from the table to load details into the form."
        )
        ttk.Label(
            panel,
            textvariable=self.form_hint,
            style="Subtitle.TLabel",
            wraplength=320,
            justify="left",
        ).grid(row=11, column=0, columnspan=2, sticky="w", pady=(18, 0))

        panel.columnconfigure(1, weight=1)

    def _build_dashboard_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=20)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(3, weight=1)

        ttk.Label(panel, text="Live Student Insights", style="PanelTitle.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
        )

        summary_frame = ttk.Frame(panel, style="Panel.TFrame")
        summary_frame.grid(row=1, column=0, sticky="ew", pady=(16, 14))
        for column in range(4):
            summary_frame.columnconfigure(column, weight=1)

        self.total_label = self._create_summary_card(summary_frame, 0, "Total Students", "0")
        self.attendance_label = self._create_summary_card(
            summary_frame, 1, "Avg Attendance", "0%"
        )
        self.honor_label = self._create_summary_card(summary_frame, 2, "Honor Roll", "0")
        self.alert_label = self._create_summary_card(summary_frame, 3, "Attention Needed", "0")

        toolbar = ttk.Frame(panel, style="Panel.TFrame")
        toolbar.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        toolbar.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value=STATUS_OPTIONS[0])

        ttk.Entry(toolbar, textvariable=self.search_var, font=("Segoe UI", 10)).grid(
            row=0,
            column=0,
            sticky="ew",
        )
        ttk.Combobox(
            toolbar,
            textvariable=self.status_var,
            values=STATUS_OPTIONS,
            state="readonly",
            width=18,
            font=("Segoe UI", 10),
        ).grid(row=0, column=1, padx=(10, 0))
        ttk.Button(
            toolbar,
            text="Apply",
            style="Secondary.TButton",
            command=self.apply_filters,
        ).grid(row=0, column=2, padx=(10, 0))
        ttk.Button(
            toolbar,
            text="Refresh",
            style="Secondary.TButton",
            command=self.refresh_students,
        ).grid(row=0, column=3, padx=(10, 0))
        ttk.Button(
            toolbar,
            text="Export CSV",
            style="Primary.TButton",
            command=self.export_students,
        ).grid(row=0, column=4, padx=(10, 0))

        columns = (
            "student_id",
            "name",
            "grade",
            "course",
            "attendance",
            "status",
            "score",
        )
        self.tree = ttk.Treeview(panel, columns=columns, show="headings")
        headings = {
            "student_id": "Student ID",
            "name": "Name",
            "grade": "Grade",
            "course": "Course",
            "attendance": "Attendance",
            "status": "Status",
            "score": "Score",
        }
        widths = {
            "student_id": 110,
            "name": 180,
            "grade": 80,
            "course": 180,
            "attendance": 110,
            "status": 150,
            "score": 90,
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center")

        self.tree.grid(row=3, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        insights = ttk.Frame(panel, style="Panel.TFrame")
        insights.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        insights.columnconfigure(0, weight=1)
        insights.columnconfigure(1, weight=1)

        spotlight = ttk.Frame(insights, style="Panel.TFrame", padding=16)
        spotlight.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Label(spotlight, text="Spotlight Student", style="PanelTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.spotlight_var = tk.StringVar(value="No records yet.")
        ttk.Label(
            spotlight,
            textvariable=self.spotlight_var,
            style="Subtitle.TLabel",
            wraplength=340,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        watchlist = ttk.Frame(insights, style="Panel.TFrame", padding=16)
        watchlist.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ttk.Label(watchlist, text="Attention Watchlist", style="PanelTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.watchlist_var = tk.StringVar(value="Everyone is on track.")
        ttk.Label(
            watchlist,
            textvariable=self.watchlist_var,
            style="Subtitle.TLabel",
            wraplength=340,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

    def _create_summary_card(
        self,
        parent: ttk.Frame,
        column: int,
        label_text: str,
        value_text: str,
    ) -> ttk.Label:
        card = ttk.Frame(parent, style="Panel.TFrame", padding=14)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 10, 0))
        ttk.Label(card, text=label_text, style="Subtitle.TLabel").grid(row=0, column=0, sticky="w")
        value = ttk.Label(
            card,
            text=value_text,
            style="PanelTitle.TLabel",
            font=("Segoe UI Semibold", 18),
        )
        value.grid(row=1, column=0, sticky="w", pady=(8, 0))
        return value

    def validate_form(self, include_id: bool) -> dict:
        payload = {key: var.get().strip() for key, var in self.form_vars.items()}

        required_fields = ["name", "age", "grade", "course", "email", "phone", "attendance"]
        if include_id:
            required_fields.insert(0, "student_id")

        missing_fields = [
            field.replace("_", " ").title() for field in required_fields if not payload[field]
        ]
        if missing_fields:
            raise ValueError(f"Please fill in: {', '.join(missing_fields)}.")

        if "@" not in payload["email"] or "." not in payload["email"].split("@")[-1]:
            raise ValueError("Please enter a valid email address.")

        try:
            payload["age"] = int(payload["age"])
        except ValueError as exc:
            raise ValueError("Age must be a whole number.") from exc

        if not 5 <= payload["age"] <= 100:
            raise ValueError("Age must be between 5 and 100.")

        try:
            payload["attendance"] = float(payload["attendance"])
        except ValueError as exc:
            raise ValueError("Attendance must be a number.") from exc

        if not 0 <= payload["attendance"] <= 100:
            raise ValueError("Attendance must be between 0 and 100.")

        payload["name"] = payload["name"].title()
        payload["course"] = payload["course"].title()
        payload["grade"] = payload["grade"].upper()
        return payload

    def add_student(self) -> None:
        try:
            payload = self.validate_form(include_id=True)
            student = Student.create(**payload)
            self.manager.add_student(student)
        except ValueError as exc:
            messagebox.showerror("Validation Error", str(exc))
            return

        messagebox.showinfo("Success", f"Student '{student.name}' added successfully.")
        self.clear_form()
        self.refresh_students()

    def update_student(self) -> None:
        if self.selected_student_id is None:
            messagebox.showwarning("No Selection", "Select a student from the table first.")
            return

        try:
            payload = self.validate_form(include_id=False)
            updated_student = self.manager.update_student(self.selected_student_id, payload)
        except ValueError as exc:
            messagebox.showerror("Validation Error", str(exc))
            return

        messagebox.showinfo("Success", f"Student '{updated_student.name}' updated successfully.")
        self.clear_form()
        self.refresh_students()

    def delete_student(self) -> None:
        if self.selected_student_id is None:
            messagebox.showwarning("No Selection", "Select a student from the table first.")
            return

        student = self.manager.get_student(self.selected_student_id)
        if student is None:
            messagebox.showerror("Error", "The selected student record no longer exists.")
            self.refresh_students()
            return

        confirmed = messagebox.askyesno(
            "Delete Student",
            f"Delete the record for {student.name}?",
        )
        if not confirmed:
            return

        self.manager.delete_student(self.selected_student_id)
        messagebox.showinfo("Deleted", f"Student '{student.name}' deleted successfully.")
        self.clear_form()
        self.refresh_students()

    def export_students(self) -> None:
        save_path = filedialog.asksaveasfilename(
            title="Export Student Records",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="student_records_export.csv",
        )
        if not save_path:
            return

        exported_path = self.manager.export_to_csv(Path(save_path))
        messagebox.showinfo("Export Complete", f"Records exported to:\n{exported_path}")

    def clear_form(self) -> None:
        for variable in self.form_vars.values():
            variable.set("")
        self.selected_student_id = None
        self.form_hint.set("Select a student from the table to load details into the form.")
        self.tree.selection_remove(self.tree.selection())

    def get_filtered_students(self) -> list[Student]:
        keyword = self.search_var.get().strip()
        students = self.manager.search_students(keyword) if keyword else self.manager.list_students()

        status = self.status_var.get()
        if status != "All Statuses":
            students = [
                student for student in students if student.performance_status == status
            ]
        return students

    def apply_filters(self) -> None:
        self.populate_tree(self.get_filtered_students())

    def refresh_students(self) -> None:
        self.populate_tree(self.get_filtered_students())
        self.update_summary()

    def populate_tree(self, students: list[Student]) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for student in students:
            self.tree.insert(
                "",
                "end",
                iid=student.student_id,
                values=(
                    student.student_id,
                    student.name,
                    student.normalized_grade,
                    student.course,
                    f"{student.attendance:.1f}%",
                    student.performance_status,
                    f"{student.performance_score:.1f}",
                ),
            )

    def update_summary(self) -> None:
        summary = self.manager.get_summary()
        self.total_label.config(text=str(summary["total_students"]))
        self.attendance_label.config(text=f"{summary['average_attendance']}%")
        self.honor_label.config(text=str(summary["honor_roll_count"]))
        self.alert_label.config(text=str(summary["attention_count"]))

        top_student = summary["top_student"]
        if top_student:
            self.spotlight_var.set(
                f"{top_student['name']} ({top_student['student_id']}) is leading in "
                f"{top_student['course']} with a {top_student['status']} profile and "
                f"score of {top_student['score']}."
            )
        else:
            self.spotlight_var.set("No records yet.")

        watchlist = summary["attention_students"]
        if watchlist:
            lines = [
                f"{student['student_id']} - {student['name']} ({student['status']}, {student['attendance']}%)"
                for student in watchlist
            ]
            self.watchlist_var.set("\n".join(lines))
        else:
            self.watchlist_var.set("Everyone is on track.")

    def on_row_selected(self, _event: object) -> None:
        selection = self.tree.selection()
        if not selection:
            return

        student_id = selection[0]
        student = self.manager.get_student(student_id)
        if student is None:
            return

        self.selected_student_id = student.student_id
        self.form_vars["student_id"].set(student.student_id)
        self.form_vars["name"].set(student.name)
        self.form_vars["age"].set(str(student.age))
        self.form_vars["grade"].set(student.normalized_grade)
        self.form_vars["course"].set(student.course)
        self.form_vars["email"].set(student.email)
        self.form_vars["phone"].set(student.phone)
        self.form_vars["attendance"].set(str(student.attendance))
        self.form_hint.set(
            f"Editing {student.name} ({student.performance_status}). Student ID stays fixed during updates."
        )


def main() -> None:
    root = tk.Tk()
    StudentRecordGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
