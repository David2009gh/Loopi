#This app was created by David Ghazaryan

import flet as ft
import time
from threading import Thread
import wikipedia

class Task(ft.Column):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit Task",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete Task",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Update Task",
                    on_click=self.save_clicked,
                ),
            ],
        )
        self.controls = [self.display_view, self.edit_view]

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_status_change(self)

    def delete_clicked(self, e):
        self.task_delete(self)

class TodoApp:
    
    def __init__(self):
        self.timer_running = False
        self.timer_thread = None
        self.timer_remaining = 15 * 60  # 15 minutes in seconds
        self.current_language = "hy"
        self.languages = {
            "en": "English", "es": "Español", "fr": "Français", "de": "Deutsch",
            "it": "Italiano", "ja": "日本語", "ru": "Русский", "zh": "中文","hy": "Հայերեն"
        }

        wikipedia.set_lang(self.current_language)
        self.page = None



        # Quiz data
        self.quiz_questions = [
    {
        "question": "Ո՞րն է ճիշտ ֆայլի ընդլայնումը Python ֆայլերի համար։",
        "options": [".pyth", ".pt", ".py", ".pyt"],
        "answer": ".py"
    },
    {
        "question": "Ո՞ր տվյալների տիպն է փոփոխման ոչ ենթակա (immutable) Python-ում։",
        "options": ["List", "Dictionary", "Tuple", "Set"],
        "answer": "Tuple"
    },
    {
        "question": "Ինչ կարտահայտի print(10 // 3)? հրամանը։",
        "options": ["3.33", "3", "4", "3.0"],
        "answer": "3"
    },
    {
        "question": "Ո՞ր տարբերակն է թույլատրելի փոփոխականի անուն։",
        "options": ["2name", "user-name", "user_name", "user name"],
        "answer": "user_name"
    },
    {
        "question": "Ինչպես են գրառում մեկնաբանությունները Python-ում։",
        "options": ["/* մեկնաբանություն */", "# մեկնաբանություն", "// մեկնաբանություն", "<!-- մեկնաբանություն -->"],
        "answer": "# մեկնաբանություն"
    },
    {
        "question": "Ո՞ր ներկառուցված ֆունկցիան է վերադարձնում առավելագույն արժեքը։",
        "options": ["maximum()", "top()", "max()", "largest()"],
        "answer": "max()"
    },
    {
        "question": "'append()' մեթոդը ինչպե՞ս է աշխատում։",
        "options": ["Ավելացնում է տարր ցուցակի վերջում", "Ավելացնում է երկու թիվ", "Ջնջում է տարրը", "Տեսակավորում է ցուցակը"],
        "answer": "Ավելացնում է տարր ցուցակի վերջում"
    },
    {
        "question": "Ո՞րը է օգտագործվում բացառություններ (exceptions) կառավարելու համար։",
        "options": ["try/except", "do/while", "for/else", "loop/end"],
        "answer": "try/except"
    },
    {
        "question": "Ինչ կվերադարձնի bool(0)? հրամանը։",
        "options": ["True", "False", "None", "0"],
        "answer": "False"
    },
    {
        "question": "Ինչ կստացվի 3 * 'ab' արտահայտությունից։",
        "options": ["'ababab'", "'ab3'", "Սխալ (SyntaxError)", "'ab ab ab'"],
        "answer": "'ababab'"
    },
]

        self.current_question_index = 0

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Loopie App - coded by D.Ghazaryan"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.window_width = 600
        page.window_height = 900
        page.scroll = ft.ScrollMode.ADAPTIVE

        # Timer components
        self.timer_display = ft.Text(
            value=self.format_time(self.timer_remaining),
            size=30,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        self.minutes_input = ft.TextField(
            value="15", width=100, text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER, label="Minutes",
        )
        self.start_button = ft.ElevatedButton(text="Start", on_click=self.start_timer)
        self.pause_button = ft.ElevatedButton(text="Pause", on_click=self.pause_timer, disabled=True)
        self.reset_button = ft.ElevatedButton(text="Reset", on_click=self.reset_timer)

        # Task components
        self.new_task = ft.TextField(hint_text="What needs to be done?", expand=True, on_submit=self.add_clicked)
        self.tasks = ft.Column()
        self.filter = ft.Tabs(
            selected_index=0, on_change=self.tabs_changed,
            tabs=[ft.Tab(text="all"), ft.Tab(text="active"), ft.Tab(text="completed")],
        )
        self.items_left = ft.Text("0 items left")

        # Wikipedia components
        self.wiki_search_input = ft.TextField(hint_text="Search Wikipedia...", expand=True, on_submit=self.search_wikipedia)
        self.wiki_result = ft.Container(
            content=ft.Column([ft.Text("Search results will appear here...", italic=True)]),
            padding=10, border_radius=5, border=ft.border.all(1, ft.colors.BLACK12), height=150,
        )
        self.language_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(key=k, text=v) for k, v in self.languages.items()],
            value=self.current_language, width=150, label="Language", on_change=self.change_language,
        )

        # Quiz UI components
        self.quiz_question_text = ft.Text(size=20, weight=ft.FontWeight.BOLD)
        
        # Create the options container first
        self.quiz_options = ft.Column()
        
        # Then pass it to RadioGroup constructor
        self.quiz_options_group = ft.RadioGroup(
            content=self.quiz_options,  # Provide the content parameter
            on_change=self.check_answer
        )
        
        self.quiz_feedback = ft.Text()
        self.quiz_next_button = ft.ElevatedButton(text="Next", on_click=self.next_question)
        self.quiz_container = ft.Container(
            content=ft.Column([
                ft.Text("Quiz Time!", size=26, weight=ft.FontWeight.BOLD),
                self.quiz_question_text,
                self.quiz_options_group,
                self.quiz_feedback,
                self.quiz_next_button,
            ]),
            padding=20,
            border_radius=10,
            bgcolor=ft.colors.YELLOW_100,
        )

        page.add(
            ft.Column([
                ft.Text("Enhanced To-Do App", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),

                ft.Container(
                    content=ft.Column([
                        self.timer_display,
                        ft.Row([self.minutes_input, self.start_button, self.pause_button, self.reset_button], alignment=ft.MainAxisAlignment.CENTER),
                    ]),
                    padding=20, border_radius=10, bgcolor=ft.colors.BLUE_50,
                ),

                ft.Container(
                    content=ft.Column([
                        ft.Row([self.new_task, ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked)]),
                        self.filter,
                        self.tasks,
                        ft.Row([self.items_left, ft.OutlinedButton(text="Clear completed", on_click=self.clear_clicked)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ]),
                    padding=20, border_radius=10, bgcolor=ft.colors.GREEN_50,
                ),

                ft.Container(
                    content=ft.Column([
                        self.language_dropdown,
                        ft.Row([self.wiki_search_input, ft.ElevatedButton(text="Search", on_click=self.search_wikipedia)]),
                        self.wiki_result,
                    ]),
                    padding=20, border_radius=10, bgcolor=ft.colors.PURPLE_50,
                ),

                self.quiz_container,
            ])
        )

        self.show_question()
        self.update()  # Initial update to display tasks correctly

    def show_question(self):
        question_data = self.quiz_questions[self.current_question_index]
        self.quiz_question_text.value = question_data["question"]
        
        # Clear previous options
        self.quiz_options.controls = [
            ft.Radio(value=opt, label=opt) for opt in question_data["options"]
        ]
        
        self.quiz_options_group.value = None
        self.quiz_feedback.value = ""
        self.page.update()

    def check_answer(self, e):
        if not self.quiz_options_group.value:
            return
            
        selected = self.quiz_options_group.value
        correct = self.quiz_questions[self.current_question_index]["answer"]
        if selected == correct:
            self.quiz_feedback.value = "✅ Correct!"
            self.quiz_feedback.color = ft.colors.GREEN
        else:
            self.quiz_feedback.value = f"❌ Incorrect. Correct: {correct}"
            self.quiz_feedback.color = ft.colors.RED
        self.page.update()

    def next_question(self, e):
        self.current_question_index = (self.current_question_index + 1) % len(self.quiz_questions)
        self.show_question()

    # Timer Methods
    def start_timer(self, e):
        try:
            minutes = int(self.minutes_input.value)
            self.timer_remaining = max(1, min(60, minutes)) * 60
            self.timer_display.value = self.format_time(self.timer_remaining)
        except ValueError:
            # Handle invalid input gracefully
            self.minutes_input.value = "15"
            self.timer_remaining = 15 * 60
            self.timer_display.value = self.format_time(self.timer_remaining)
            
        if not self.timer_running:
            self.timer_running = True
            self.start_button.disabled = True
            self.pause_button.disabled = False
            self.timer_thread = Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            self.page.update()

    def pause_timer(self, e):
        self.timer_running = False
        self.start_button.disabled = False
        self.pause_button.disabled = True
        self.page.update()

    def reset_timer(self, e):
        self.timer_running = False
        try:
            minutes = int(self.minutes_input.value)
            self.timer_remaining = max(1, min(60, minutes)) * 60
        except ValueError:
            self.timer_remaining = 15 * 60
            self.minutes_input.value = "15"
        self.timer_display.value = self.format_time(self.timer_remaining)
        self.start_button.disabled = False
        self.pause_button.disabled = True
        self.page.update()

    def run_timer(self):
        while self.timer_running and self.timer_remaining > 0:
            time.sleep(1)
            if self.timer_running:
                self.timer_remaining -= 1
                self.timer_display.value = self.format_time(self.timer_remaining)
                self.page.update()
                if self.timer_remaining <= 0:
                    self.timer_running = False
                    self.start_button.disabled = False
                    self.pause_button.disabled = True
                    self.page.update()

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    # Task Methods
    def add_clicked(self, e):
        task_text = self.new_task.value.strip()
        if task_text:
            task = Task(task_text, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.update()

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        tasks_to_remove = [task for task in self.tasks.controls if task.completed]
        for task in tasks_to_remove:
            self.tasks.controls.remove(task)
        self.update()

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = sum(1 for task in self.tasks.controls if not task.completed)
        for task in self.tasks.controls:
            task.visible = (
                status == "all" or
                (status == "active" and not task.completed) or
                (status == "completed" and task.completed)
            )
        self.items_left.value = f"{count} active item(s) left"
        self.page.update()

    # Wikipedia Methods
    def search_wikipedia(self, e):
        query = self.wiki_search_input.value.strip()
        if query:
            self.wiki_result.content = ft.Column([ft.Text("Searching...", italic=True)])
            self.page.update()  # Update UI immediately to show searching state
            Thread(target=self._perform_wiki_search, args=(query,), daemon=True).start()

    def _perform_wiki_search(self, query):
        try:
            try:
                summary = wikipedia.summary(query, sentences=2)
                self.wiki_result.content = ft.Column([ft.Text(summary)])
            except wikipedia.exceptions.DisambiguationError as e:
                options = e.options[:5]  # Show first 5 options
                content = [
                    ft.Text("Please clarify, there are multiple results:"),
                    ft.Text(", ".join(options), italic=True)
                ]
                self.wiki_result.content = ft.Column(content)
            except wikipedia.exceptions.PageError:
                self.wiki_result.content = ft.Column([ft.Text("No results found. Try a different search term.")])
            except wikipedia.exceptions.HTTPTimeoutError:
                self.wiki_result.content = ft.Column([ft.Text("Wikipedia is taking too long to respond.")])
        except Exception as e:
            self.wiki_result.content = ft.Column([ft.Text(f"Error: {str(e)}")])
        self.page.update()

    # Language Methods
    def change_language(self, e):
        self.current_language = e.control.value
        wikipedia.set_lang(self.current_language)
        self.page.update()

def main():
    app = TodoApp()
    ft.app(target=app.main)

if __name__ == "__main__":
    main()