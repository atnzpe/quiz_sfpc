# app/controllers.py
import flet as ft
from .models import Pergunta, EstadoQuiz  # Importa as classes do modelo
from quiz_logic import QuizLogic  # Importa a lógica do quiz
from .views import (
    exibir_tela_inicial,
    exibir_pergunta,
    exibir_resultados,
)  # Importa as funções de visualização


class QuizController:
    def __init__(self, page: ft.Page, botao_tema):  # Recebe o botão de tema
        """
        Inicializa o controlador do quiz.
        """
        self.page = page
        self.botao_tema = botao_tema  # Armazena o botão
        self.estado_quiz = EstadoQuiz()
        self.quiz_logic = QuizLogic()
        self.exibir_tela_inicial()

    def exibir_tela_inicial(self):
        """Exibe a tela inicial do quiz."""
        self.page.clean()
        exibir_tela_inicial(
            self.page, self, self.botao_tema
        )  # Passa o botão para a View
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
