import flet as ft
import time
from flet import (
    Column,
    Text,
    ElevatedButton,
    Row,
    TextField,
    TextButton,
    AlertDialog,
    IconButton,
    icons,
    Page,
    Image,
    SnackBar,
)


class QuizUI:
    """
    Gerencia a interface do usuário do aplicativo de quiz, incluindo a tela inicial,
    a tela do quiz e os resultados.
    """

    def __init__(self, page: ft.Page, quiz_logic):
        """Inicializa a interface do usuário do quiz."""

        self.page = page  # Referência à página principal do aplicativo Flet
        self.quiz_logic = quiz_logic  # Instância da classe QuizLogic

        # Define os elementos da interface do usuário
        self.question_text = Text(size=20, visible=False)
        self.answer_buttons = []
        for _ in range(4):
            button = ElevatedButton(on_click=self.check_answer, visible=False)
            self.answer_buttons.append(button)
        self.feedback_text = Text("", visible=False)
        self.score_text = Text(f"Tempo restante: 1:00:00", size=16, visible=False)
        self.time_remaining = 3600  # Tempo restante em segundos

        # Constrói a interface inicial do aplicativo
        self.build_initial_ui()

        # Inicia a atualização do timer quando a página é montada
        self.page.on_mount = self.on_mount

    def build_initial_ui(self):
        """Cria a interface da tela inicial."""
        scrum_icon = Image(
            src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Scrum_logo.svg/2560px-Scrum_logo.svg.png",
            width=100,
            height=100,
        )
        button_start = ElevatedButton("Iniciar Quiz", on_click=self.start_quiz)
        button_close = ElevatedButton("Fechar", on_click=lambda _: self.page.window_close())
        self.page.add(
            Column(
                [
                    scrum_icon,
                    button_start,
                    button_close,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    def start_quiz(self, e):
        """Inicia o quiz."""
        if not self.quiz_logic.check_internet_connection():
            self.page.snack_bar = SnackBar(
                ft.Text("Sem conexão com a internet. Carregando perguntas do cache.")
            )
            self.page.snack_bar.open = True
            self.page.update()

        self.page.clean()
        self.page.add(
            Column(
                [
                    self.score_text,
                    self.question_text,
                    *self.answer_buttons,
                    self.feedback_text,
                    ElevatedButton("Voltar ao Início", on_click=self.return_to_home),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        self.quiz_logic.start_timer()
        self.load_question()
        self.question_text.visible = True
        self.feedback_text.visible = True
        self.score_text.visible = True
        for button in self.answer_buttons:
            button.visible = True
        self.page.update()

    def load_question(self):
        """Carrega a próxima pergunta do quiz."""
        question_text, options, correct_answer = self.quiz_logic.load_question()
        if question_text:
            self.question_text.value = question_text
            for i in range(4):
                self.answer_buttons[i].text = options[i]
                self.answer_buttons[i].data = i == correct_answer
                self.answer_buttons[i].disabled = False
        else:
            self.end_quiz()
        self.page.update()

    def check_answer(self, e):
        """Verifica a resposta selecionada pelo usuário."""
        self.feedback_text.value = self.quiz_logic.check_answer(e.control.data)
        self.quiz_logic.current_question += 1
        self.page.update()
        time.sleep(0.5)
        self.feedback_text.value = ""
        self.load_question()

    def update_timer(self):
        """Atualiza o cronômetro do quiz a cada segundo."""
        if self.quiz_logic.timer_running:
            self.time_remaining -= 1
            if self.time_remaining == 0:
                self.end_quiz()
            else:
                minutes, seconds = divmod(self.time_remaining, 60)
                self.score_text.value = f"Tempo restante: {minutes:02d}:{seconds:02d}"
                self.page.update()
                time.sleep(1)
                self.page.on_idle = self.update_timer

    def end_quiz(self):
        """Encerra o quiz."""
        for button in self.answer_buttons:
            button.disabled = True
        self.quiz_logic.stop_timer()
        self.show_results()

    def show_results(self):
        """Exibe os resultados do quiz."""
        def close_dlg(e):
            dlg_modal.open = False
            self.page.update()

        dlg_modal = AlertDialog(
            modal=True,
            title=Text("Fim do Quiz!"),
            content=Text(self.quiz_logic.get_final_results()),
            actions=[
                TextButton("Fechar", on_click=close_dlg),
            ],
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = dlg_modal
        dlg_modal.open = True
        self.page.update()

    def return_to_home(self, e):
        """Retorna à tela inicial."""
        self.quiz_logic.timer_running = False
        self.build_initial_ui()
        self.page.update()

    def on_mount(self, e):
        """Inicia a atualização do timer quando a página é montada."""
        self.page.on_idle = self.update_timer
