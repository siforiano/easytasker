import customtkinter as ctk
import json
import os
import time
import threading
import csv
from datetime import datetime, timedelta
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox

try:
    import winsound
    import plyer
except ImportError:
    winsound = None
    plyer = None

TASKS_FILE = "tasks.json"
BACKUP_FILE = "tasks_backup.json"

LANGUAGES = {
    "es": {
        "app_title": "EasyTasker - Gestor de Tareas",
        "add_task": "Agregar",
        "delete_task": "Eliminar Tarea",
        "complete_task": "Marcar Completada",
        "refresh": "Refrescar",
        "theme": "Tema:",
        "priority": "Prioridad:",
        "category": "Categoría:",
        "title": "Título:",
        "search": "Buscar...",
        "export_csv": "Exportar CSV",
        "export_pdf": "Exportar PDF",
        "lang": "Idioma:",
        "error_empty_title": "El título no puede estar vacío.",
        "error_select_task": "Selecciona una tarea primero.",
        "error_date_format": "Formato de fecha incorrecto.",
        "task_completed": "Tarea completada",
        "task_deleted": "Tarea eliminada",
        "backup_created": "Backup creado automáticamente.",
        "backup_restored": "Backup restaurado.",
        "notification_tasks": "Tareas próximas:",
    },
    "en": {
        "app_title": "EasyTasker - Task Manager",
        "add_task": "Add",
        "delete_task": "Delete Task",
        "complete_task": "Mark Completed",
        "refresh": "Refresh",
        "theme": "Theme:",
        "priority": "Priority:",
        "category": "Category:",
        "title": "Title:",
        "search": "Search...",
        "export_csv": "Export CSV",
        "export_pdf": "Export PDF",
        "lang": "Language:",
        "error_empty_title": "Title cannot be empty.",
        "error_select_task": "Please select a task first.",
        "error_date_format": "Wrong date format.",
        "task_completed": "Task Completed",
        "task_deleted": "Task Deleted",
        "backup_created": "Backup auto-created.",
        "backup_restored": "Backup restored.",
        "notification_tasks": "Upcoming tasks:",
    }
}

class EasyTaskerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_lang_code = 'es'
        self.lang = LANGUAGES[self.current_lang_code]
        self.title(self.lang["app_title"])
        self.geometry("750x630")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.tasks = []
        self.selected_task_index = None

        # Barra de título visual (solo muestra nombre app, no editable)
        self.title_bar = ctk.CTkFrame(self, height=40, fg_color="#2a2a2a")
        self.title_bar.pack(fill="x")
        self.title_label = ctk.CTkLabel(self.title_bar,
            text=self.lang["app_title"],
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#2a2a2a",
            text_color="white")
        self.title_label.pack(padx=20, pady=5)

        self.load_backup()
        self.load_tasks()
        self.setup_ui()
        self.start_backup()

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []

    def save_tasks(self):
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2)

    def load_backup(self):
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                self.backup_tasks = json.load(f)

    def start_backup(self):
        def backup_loop():
            while True:
                time.sleep(3600)
                with open(BACKUP_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.tasks, f, indent=2)
        threading.Thread(target=backup_loop, daemon=True).start()

    def setup_ui(self):
        # Selector de Tema e Idioma
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(top_frame, text=self.lang["theme"]).pack(side="left", padx=4)
        self.theme_var = ctk.StringVar(value="System")
        ctk.CTkOptionMenu(top_frame,
            values=["System", "Dark", "Light"],
            variable=self.theme_var,
            command=self.change_theme
        ).pack(side="left", padx=4)
        ctk.CTkLabel(top_frame, text=self.lang["lang"]).pack(side="left", padx=10)
        self.lang_var = ctk.StringVar(value=self.current_lang_code)
        ctk.CTkOptionMenu(top_frame,
            values=list(LANGUAGES.keys()),
            variable=self.lang_var,
            command=self.change_language
        ).pack(side="left", padx=4)

        # Buscador (AHORA ARRIBA)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self, placeholder_text=self.lang["search"], textvariable=self.search_var)
        self.search_entry.pack(fill="x", padx=10, pady=(0, 6))
        self.search_var.trace_add("write", self.filter_tasks)

        # Lista de tareas scrollable
        self.task_listbox = ctk.CTkScrollableFrame(self, height=320, corner_radius=10)
        self.task_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        # Formulario de tarea (debajo de la lista)
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=10, pady=8)

        # CAMPO DE TITULO CON ETIQUETA CLARA
        ctk.CTkLabel(input_frame, text=self.lang["title"]).grid(row=0, column=0, sticky="w", padx=5)
        self.entry_title = ctk.CTkEntry(input_frame, placeholder_text=self.lang["title"])
        self.entry_title.grid(row=0, column=1, sticky="ew", padx=5, pady=3)

        # Etiqueta y selector para prioridad (separado visualmente)
        ctk.CTkLabel(input_frame, text=self.lang["priority"]).grid(row=1, column=0, sticky="w", padx=5)
        self.priority_var = ctk.StringVar(value="Normal")
        ctk.CTkOptionMenu(input_frame,
            values=["Alta", "Normal", "Baja"],
            variable=self.priority_var
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        ctk.CTkLabel(input_frame, text=self.lang["category"]).grid(row=2, column=0, sticky="w", padx=5)
        self.entry_category = ctk.CTkEntry(input_frame)
        self.entry_category.grid(row=2, column=1, sticky="ew", padx=5, pady=3)

        ctk.CTkLabel(input_frame, text="Fecha límite (YYYY-MM-DD HH:MM)").grid(row=3, column=0, sticky="w", padx=5)
        self.entry_deadline = ctk.CTkEntry(input_frame)
        self.entry_deadline.grid(row=3, column=1, sticky="ew", padx=5, pady=3)

        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=3)

        # Botones principales
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=8)
        self.btn_add = ctk.CTkButton(btn_frame, text=self.lang["add_task"], command=self.add_task)
        self.btn_add.pack(side="left", padx=5)
        self.btn_complete = ctk.CTkButton(btn_frame, text=self.lang["complete_task"], command=self.mark_completed)
        self.btn_complete.pack(side="left", padx=5)
        self.btn_delete = ctk.CTkButton(btn_frame, text=self.lang["delete_task"], command=self.delete_task, fg_color="#d32f2f")
        self.btn_delete.pack(side="left", padx=5)
        self.btn_refresh = ctk.CTkButton(btn_frame, text=self.lang["refresh"], command=self.populate_tasks)
        self.btn_refresh.pack(side="left", padx=5)
        self.btn_export_csv = ctk.CTkButton(btn_frame, text=self.lang["export_csv"], command=self.export_csv)
        self.btn_export_csv.pack(side="right", padx=5)
        self.btn_export_pdf = ctk.CTkButton(btn_frame, text=self.lang["export_pdf"], command=self.export_pdf)
        self.btn_export_pdf.pack(side="right", padx=5)

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)

        self.notification_label = ctk.CTkLabel(self, text="")
        self.notification_label.pack(fill="x", padx=10, pady=2)

        self.populate_tasks()

    def change_theme(self, mode):
        ctk.set_appearance_mode(mode)
        self.populate_tasks()

    def change_language(self, lang):
        if lang not in LANGUAGES:
            return
        self.current_lang_code = lang
        self.lang = LANGUAGES[lang]
        self.title(self.lang["app_title"])
        self.title_label.configure(text=self.lang["app_title"])
        self.search_entry.configure(placeholder_text=self.lang["search"])
        self.btn_add.configure(text=self.lang["add_task"])
        self.btn_complete.configure(text=self.lang["complete_task"])
        self.btn_delete.configure(text=self.lang["delete_task"])
        self.btn_refresh.configure(text=self.lang["refresh"])
        self.btn_export_csv.configure(text=self.lang["export_csv"])
        self.btn_export_pdf.configure(text=self.lang["export_pdf"])
        self.populate_tasks()

    def filter_tasks(self, *args):
        query = self.search_var.get().lower()
        filtered = [t for t in self.tasks if query in t['title'].lower() or
                    query in (t.get('category') or '').lower() or
                    query in (t.get('priority') or '').lower()]
        self.populate_tasks(filtered)

    def populate_tasks(self, task_list=None):
        if task_list is None:
            task_list = self.tasks
        for widget in self.task_listbox.winfo_children():
            widget.destroy()
        mode = ctk.get_appearance_mode()
        for idx, task in enumerate(task_list):
            bg_color = "#2e3c26" if mode == "Dark" and task["completed"] else \
                       "#383e47" if mode == "Dark" else \
                       "#d0f0c0" if task["completed"] else "#f0f0f0"
            fg_color = "#a1d99b" if mode == "Dark" and task["completed"] else \
                       "#e1e8f0" if mode == "Dark" else \
                       "#228B22" if task["completed"] else "#000000"
            frame = ctk.CTkFrame(self.task_listbox, height=40, corner_radius=8, fg_color=bg_color)
            frame.pack(fill="x", pady=2, padx=2)
            status = "✓" if task["completed"] else "✗"
            deadline = task["deadline"] if task["deadline"] else "Sin fecha"
            label_text = f"[{status}] {task['title']} ({task['priority']}, {task['category']}) - {deadline}"
            label = ctk.CTkLabel(frame, text=label_text,
                                 font=ctk.CTkFont(size=14), text_color=fg_color)
            label.pack(side="left", padx=10)
            label.bind("<Button-1>", lambda e, i=idx: self.select_task(i))
        self.update_progress_bar()

    def select_task(self, index):
        self.selected_task_index = index
        mode = ctk.get_appearance_mode()
        selected_color = "#00ff00" if mode == "Dark" else "#228B22"
        default_color = "#e1e8f0" if mode == "Dark" else "#000000"
        for i, child in enumerate(self.task_listbox.winfo_children()):
            lbl = child.winfo_children()[0]
            lbl.configure(text_color=selected_color if i == index else default_color)

    def add_task(self):
        title = self.entry_title.get().strip()
        if not title:
            CTkMessagebox(title="Error", message=self.lang["error_empty_title"], icon="warning")
            return
        deadline_str = self.entry_deadline.get().strip()
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M").isoformat()
            except:
                CTkMessagebox(title="Error", message=self.lang["error_date_format"], icon="warning")
                return
        priority = self.priority_var.get()
        category = self.entry_category.get().strip()
        task = {
            "id": int(time.time() * 1000),
            "title": title,
            "created": datetime.now().isoformat(),
            "deadline": deadline,
            "priority": priority,
            "category": category,
            "completed": False,
            "recurrent": None
        }
        self.tasks.append(task)
        self.save_tasks()
        self.entry_title.delete(0, "end")
        self.entry_deadline.delete(0, "end")
        self.entry_category.delete(0, "end")
        self.populate_tasks()
        self.check_notifications()

    def mark_completed(self):
        if self.selected_task_index is None:
            CTkMessagebox(title="Error", message=self.lang["error_select_task"], icon="warning")
            return
        self.tasks[self.selected_task_index]["completed"] = True
        self.save_tasks()
        self.populate_tasks()
        self.check_notifications()

    def delete_task(self):
        if self.selected_task_index is None:
            CTkMessagebox(title="Error", message=self.lang["error_select_task"], icon="warning")
            return
        deleted = self.tasks.pop(self.selected_task_index)
        self.save_tasks()
        self.populate_tasks()
        self.check_notifications()
        CTkMessagebox(title=self.lang["task_deleted"], message=deleted["title"], icon="check")
        self.selected_task_index = None

    def update_progress_bar(self):
        total = len(self.tasks)
        if total == 0:
            self.progress_bar.set(0)
        else:
            completed = sum(1 for t in self.tasks if t["completed"])
            self.progress_bar.set(completed / total)

    def check_notifications(self):
        now = datetime.now()
        soon = now + timedelta(hours=1)
        alerts = [t for t in self.tasks if t["deadline"] and not t["completed"] and now <= datetime.fromisoformat(t["deadline"]) <= soon]
        if alerts:
            msg = self.lang["notification_tasks"] + " " + ", ".join(
                f"{t['title']} (en {int((datetime.fromisoformat(t['deadline'])-now).total_seconds()/60)} min)" for t in alerts)
            self.notification_label.configure(text=msg)
            if winsound:
                threading.Thread(target=winsound.MessageBeep).start()
            if plyer is not None:
                plyer.notification.notify(title="EasyTasker", message=msg)
        else:
            self.notification_label.configure(text="")

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", ".csv")])
        if not filepath:
            return
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Título", "Creado", "Límite", "Prioridad", "Categoría", "Completada"])
                for t in self.tasks:
                    writer.writerow([t["id"], t["title"], t["created"], t["deadline"], t["priority"], t["category"], t["completed"]])
            CTkMessagebox(title="Exportación CSV", message=f"Exportado a: {filepath}", icon="check")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"No se pudo exportar CSV: {e}", icon="cancel")

    def export_pdf(self):
        CTkMessagebox(title="Funcionalidad", message="Exportar PDF aún no implementado.", icon="info")

if __name__ == "__main__":
    app = EasyTaskerApp()
    app.mainloop()