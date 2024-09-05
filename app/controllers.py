import flet as ft
import threading
from .models import Pergunta, EstadoQuiz
from quiz_logic import QuizLogic
from .views import (
    exibir_tela_inicial,
    exibir_pergunta,
    exibir_resultados,
)
from automate_spreadsheet import monitor_google_docs

# URL da planilha e ID do documento.
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"
DOCUMENT_ID = "1kQU6ElV41Y73Iiu6N1lOcfAoHaaWSNTqmOnOWBhifgg"


class QuizController:
    """Controla o fluxo do quiz."""

    def __init__(self, page: ft.Page, switch_tema):
        """Inicializa o controlador do quiz."""
        self.page = page
        self.switch_tema = switch_tema
        self.som_ativado = True  # Estado inicial do som
        self.estado_quiz = EstadoQuiz()
        self.quiz_logic = QuizLogic()
        self.exibir_tela_inicial()

        # Inicia a thread de monitoramento do Google Docs
        self.iniciar_monitoramento_docs()

    def iniciar_monitoramento_docs(self):
        """Inicia a thread de monitoramento do Google Docs."""
        thread_monitoramento = threading.Thread(
            target=monitor_google_docs, args=(DOCUMENT_ID, SPREADSHEET_URL)
        )
        thread_monitoramento.daemon = True
        thread_monitoramento.start()

    def exibir_tela_inicial(self):
        """Exibe a tela inicial do quiz."""
        self.page.clean()
        exibir_tela_inicial(self.page, self)  # Passa o switch para a View
        self.page.update()

    def iniciar_quiz(self, e):
        """
        Inicia o quiz, configurando o estado e carregando a primeira pergunta.

        Args:
            e: O evento que acionou a função (ex: clique do botão).
        """
        if not self.estado_quiz.quiz_iniciado:  # Verifica se o quiz já foi iniciado
            self.estado_quiz.quiz_iniciado = True
            self.proxima_pergunta(e)

    def proxima_pergunta(self, e):
        """
        Carrega e exibe a próxima pergunta do quiz.

        Args:
            e: O evento que acionou a função.
        """
        if self.estado_quiz.pergunta_atual < len(self.quiz_logic.questions):
            # Cria uma instância de Pergunta com os dados da pergunta atual
            pergunta_atual = self.quiz_logic.questions[self.estado_quiz.pergunta_atual]
            pergunta = Pergunta(
                pergunta_atual[0], pergunta_atual[1:5], pergunta_atual[5]
            )
            exibir_pergunta(self.page, pergunta, self.estado_quiz, self)
            self.estado_quiz.pergunta_atual += 1
        else:
            self.finalizar_quiz(e)

    def verificar_resposta(self, e):
        """
        Verifica a resposta selecionada pelo usuário e atualiza a pontuação.

        Args:
            e: O evento que acionou a função, contendo informações sobre a resposta selecionada.
        """
        if not self.estado_quiz.quiz_finalizado:  # Verifica se o quiz já foi finalizado
            if (
                e.control.data
                == self.quiz_logic.questions[self.estado_quiz.pergunta_atual - 1].index(
                    self.quiz_logic.questions[self.estado_quiz.pergunta_atual - 1][5]
                )
                - 1
            ):
                self.estado_quiz.pontuacao += 1
            self.proxima_pergunta(e)

    def finalizar_quiz(self, e):
        """
        Finaliza o quiz e exibe os resultados.

        Args:
            e: O evento que acionou a função.
        """
        self.estado_quiz.quiz_finalizado = True
        self.estado_quiz.quiz_iniciado = False
        exibir_resultados(self.page, self.estado_quiz, self)

    def voltar_ao_inicio(self, e):
        """
        Volta à tela inicial do quiz, redefinindo o estado e a lógica.

        Args:
            e: O evento que acionou a função.
        """
        self.estado_quiz = EstadoQuiz()  # Reinicia o estado do quiz
        self.quiz_logic = (
            QuizLogic()
        )  # Reinicia a lógica do quiz (carrega novas perguntas)
        self.exibir_tela_inicial()

    def exibir_pergunta(self, e):
        """Carrega e exibe a próxima pergunta."""
        if self.estado_quiz.pergunta_atual < len(self.quiz_logic.questions):
            pergunta_atual = self.quiz_logic.questions[self.estado_quiz.pergunta_atual]
            pergunta = Pergunta(
                pergunta_atual[0], pergunta_atual[1:5], pergunta_atual[5]
            )
            exibir_pergunta(self.page, pergunta, self.estado_quiz, self)
            self.estado_quiz.pergunta_atual += 1

            # Armazena a referência para o ft.Text do timer
            self.texto_tempo = self.page.controls[0].controls[0]

        else:
            self.finalizar_quiz(e)
        self.page.update()

    def atualizar_texto_tempo(self):
        """Atualiza o texto do tempo na tela da pergunta."""
        if self.texto_tempo:  # Verifica se a referência existe
            horas, resto = divmod(self.estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            self.texto_tempo.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            self.page.update()
