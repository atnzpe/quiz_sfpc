import flet as ft
import threading
from .models import Pergunta, EstadoQuiz
from quiz_logic import QuizLogic
from .views import (
    exibir_tela_inicial,
    exibir_pergunta,
    exibir_resultados,
    reproduzir_audio,  # Importe a função reproduzir_audio
)


class QuizController:
    def __init__(self, page: ft.Page, switch_tema, som_ativado):
        self.page = page
        self.switch_tema = switch_tema
        self.som_ativado = som_ativado
        self.estado_quiz = EstadoQuiz()
        self.quiz_logic = QuizLogic()
        self.timer = None
        self.texto_tempo = None
        self.exibir_tela_inicial()

    def exibir_tela_inicial(self):
        """Exibe a tela inicial do quiz."""
        self.parar_timer()
        self.estado_quiz = EstadoQuiz()
        self.page.clean()
        exibir_tela_inicial(self.page, self)
        self.page.update()

    def iniciar_quiz(self, e):
        """Inicia o quiz."""
        if not self.estado_quiz.quiz_iniciado:
            self.estado_quiz.quiz_iniciado = True
            self.iniciar_timer()
            self.proxima_pergunta(e)

    def proxima_pergunta(self, e):
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

    def verificar_resposta(self, e):
        """Verifica a resposta selecionada pelo usuário."""
        if not self.estado_quiz.quiz_finalizado:
            # Correção: Comparar índice com índice
            resposta_correta = self.quiz_logic.load_question()[2]  # Obtém o índice da resposta correta
            if e.control.data == resposta_correta:
                self.estado_quiz.pontuacao += 1
                if self.som_ativado:
                    reproduzir_audio(
                        "certo"
                    )  # Reproduz um áudio aleatório da pasta "certo"
            else:
                if self.som_ativado:
                    reproduzir_audio(
                        "errado"
                    )  # Reproduz um áudio aleatório da pasta "errado"
            self.proxima_pergunta(e)

    def finalizar_quiz(self, e):
        """Finaliza o quiz."""
        self.parar_timer()
        self.estado_quiz.quiz_finalizado = True
        self.estado_quiz.quiz_iniciado = False
        exibir_resultados(self.page, self.estado_quiz, self)

    def voltar_ao_inicio(self, e):
        """Volta à tela inicial."""
        self.estado_quiz = EstadoQuiz()
        self.quiz_logic = QuizLogic()
        self.exibir_tela_inicial()

    def iniciar_timer(self):
        """Inicia o timer da prova."""

        def atualizar_tempo():
            """Atualiza o tempo restante a cada segundo."""
            if self.estado_quiz.tempo_restante > 0 and self.estado_quiz.quiz_iniciado:
                self.estado_quiz.tempo_restante -= 1
                self.atualizar_texto_tempo()
                self.timer = threading.Timer(1, atualizar_tempo)
                self.timer.start()
            else:
                self.finalizar_quiz(None)

        self.atualizar_texto_tempo()
        self.timer = threading.Timer(1, atualizar_tempo)
        self.timer.start()

    def parar_timer(self):
        """Para o timer da prova."""
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

    def atualizar_texto_tempo(self):
        """Atualiza o texto do tempo na tela da pergunta."""
        if self.texto_tempo:
            horas, resto = divmod(self.estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            self.texto_tempo.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            self.page.update()
