# ui.py

import flet as ft
import time
from flet import (
    Column,
    Text,
    TextButton,
    ElevatedButton,
    Row,
    TextField,
    AlertDialog,
    IconButton,
    icons,
    Page,
    Image,
    SnackBar,# Importação necessária para usar imagens
)

class QuizUI:
    def __init__(self, page: Page, quiz_logic):
        # Inicializa a página do aplicativo e a lógica do quiz
        self.page = page
        self.quiz_logic = quiz_logic

        # Define os elementos da interface do usuário
        self.question_text = Text(size=20, visible=False)  # Texto da pergunta, inicialmente invisível
        self.answer_buttons = []  # Lista para armazenar os botões de resposta
        for _ in range(4):
            button = ElevatedButton(on_click=self.check_answer, visible=False)  # Botões de resposta, inicialmente invisíveis
            self.answer_buttons.append(button)
        self.feedback_text = Text("", visible=False)  # Feedback da resposta, inicialmente invisível
        self.score_text = Text(f"Tempo restante: 1:00:00", size=16, visible=False)  # Texto do cronômetro, inicialmente invisível
        self.timer = ft.Timer(1, on_timeout=self.update_timer)  # Cria o cronômetro com intervalo de 1 segundo

        # Constrói a interface inicial
        self.build_initial_ui()  

    def build_initial_ui(self):
        """Cria a interface da tela inicial com o ícone do Scrum, botão Iniciar e botão Fechar."""
        
        # Ícone do Scrum
        scrum_icon = Image(
            src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Scrum_logo.svg/2560px-Scrum_logo.svg.png",
            width=100,
            height=100,
        )

        # Botão Iniciar Quiz
        button_start = ElevatedButton("Iniciar Quiz", on_click=self.start_quiz)  # Chama a função start_quiz ao clicar

        # Botão Fechar Aplicação
        button_close = ElevatedButton("Fechar", on_click=lambda _: self.page.window_close()) # Fecha a janela ao clicar

        # Adiciona os elementos à página
        self.page.add(
            Column(
                [
                    scrum_icon,
                    button_start,
                    button_close,
                ],
                alignment=ft.MainAxisAlignment.CENTER,  # Centraliza verticalmente
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centraliza horizontalmente
            )
        )

    def start_quiz(self, e):
        """Inicia o quiz, limpando a tela inicial e exibindo a primeira pergunta."""

        """Inicia o quiz, exibindo uma mensagem se estiver offline."""
        if not self.quiz_logic.check_internet_connection():
            self.page.snack_bar = SnackBar(ft.Text("Sem conexão com a internet. Carregando perguntas do cache."))
            self.page.snack_bar.open = True
            self.page.update()
        
        self.page.clean() # Limpa os widgets da tela inicial
        self.page.add(
            Column(
                [
                    self.score_text,
                    self.question_text,
                    *self.answer_buttons,  # Desempacota os botões de resposta na coluna
                    self.feedback_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        self.quiz_logic.start_timer()  # Inicia a lógica do cronômetro
        self.load_question()  # Carrega a primeira pergunta
        self.timer.start()  # Inicia o cronômetro
        self.question_text.visible = True  # Torna a pergunta visível
        self.feedback_text.visible = True  # Torna o feedback da resposta visível
        self.score_text.visible = True  # Torna o cronômetro visível
        for button in self.answer_buttons:
            button.visible = True  # Torna os botões de resposta visíveis
        self.page.update()  # Atualiza a interface

    def load_question(self):
        """Carrega a próxima pergunta do quiz."""
        (
            question_text,
            options,
            correct_answer,
        ) = self.quiz_logic.load_question()  # Obtém a pergunta, opções e resposta correta da lógica do quiz
        if question_text:
            self.question_text.value = question_text  # Define o texto da pergunta
            for i in range(4):
                self.answer_buttons[i].text = options[i]  # Define o texto dos botões de resposta
                self.answer_buttons[i].data = i == correct_answer  # Define qual botão corresponde à resposta correta
                self.answer_buttons[i].disabled = False  # Habilita os botões de resposta
        else:
            self.end_quiz()  # Se não houver mais perguntas, encerra o quiz
        self.page.update()  # Atualiza a interface

    def check_answer(self, e):
        """Verifica a resposta selecionada pelo usuário."""
        self.feedback_text.value = self.quiz_logic.check_answer(
            e.control.data
        )  # Obtém o feedback da resposta da lógica do quiz
        self.quiz_logic.current_question += 1  # Avança para a próxima pergunta
        self.page.update()  # Atualiza a interface
        time.sleep(0.5)  # Aguarda meio segundo para exibir o feedback
        self.feedback_text.value = ""  # Limpa o feedback da resposta
        self.load_question()  # Carrega a próxima pergunta

    def update_timer(self, e):
        """Atualiza o cronômetro do quiz."""
        time_limit = self.quiz_logic.get_time_remaining()  # Obtém o tempo restante da lógica do quiz
        if time_limit == 0:
            self.end_quiz()  # Se o tempo acabar, encerra o quiz
        else:
            # Formata o tempo restante (HH:MM:SS) e atualiza o texto do cronômetro
            self.score_text.value = f"Tempo restante: {time_limit//3600:02d}:{(time_limit%3600)//60:02d}:{time_limit%60:02d}" 
            self.page.update()  # Atualiza a interface

    def end_quiz(self):
        """Encerra o quiz, desabilitando os botões e exibindo os resultados."""
        for button in self.answer_buttons:
            button.disabled = True  # Desabilita os botões de resposta
        self.timer.stop()  # Para o cronômetro
        self.show_results()  # Exibe os resultados

    def show_results(self):
        """Exibe os resultados do quiz em um diálogo modal."""

        def close_dlg(e):
            """Fecha o diálogo modal."""
            dlg_modal.open = False
            self.page.update()

        # Cria o diálogo modal com os resultados
        dlg_modal = AlertDialog(
            modal=True,
            title=Text("Fim do Quiz!"),
            content=Text(self.quiz_logic.get_final_results()),  # Obtém os resultados da lógica do quiz
            actions=[
                TextButton("Fechar", on_click=close_dlg),  # Botão para fechar o diálogo
            ],
            on_dismiss=lambda e: print("Modal dialog dismissed!"),  # Ação ao fechar o diálogo
        )
        self.page.dialog = dlg_modal  # Define o diálogo na página
        dlg_modal.open = True  # Exibe o diálogo
        self.page.update()  # Atualiza a interface
