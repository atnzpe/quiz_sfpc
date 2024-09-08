import flet as ft
import threading
import time

from .models import Pergunta, EstadoQuiz
from quiz_logic import QuizLogic
from .views import (
    exibir_tela_inicial,
    exibir_pergunta,
    exibir_resultados,
    reproduzir_audio,
    piscar_verde,
    piscar_vermelho,
)


class QuizController:
    """
    Classe que controla a lógica do quiz, gerenciando a interação
    entre a lógica do jogo, a interface do usuário e o estado do quiz.
    """

    def __init__(self, page: ft.Page, switch_tema: ft.Switch, som_ativado: bool):
        """
        Inicializa o controlador do quiz.

        Args:
            page (ft.Page): A página Flet principal da aplicação.
            switch_tema (ft.Switch): O controle Flet para alternar o tema.
            som_ativado (bool): Indica se o som está ativado inicialmente.
        """
        self.page = page
        self.switch_tema = switch_tema
        self.som_ativado = som_ativado
        self.estado_quiz = EstadoQuiz()
        self.quiz_logic = QuizLogic()
        self.timer = None
        self.texto_tempo = None 
        self.modal_aberto = False 
        self.exibir_tela_inicial()  

    def exibir_tela_inicial(self):
        """Exibe a tela inicial do quiz, reiniciando o estado do jogo."""
        self.parar_timer()
        self.estado_quiz.reiniciar()  # Usa o método reiniciar do EstadoQuiz
        self.page.clean()
        exibir_tela_inicial(self.page, self)
        self.page.update()

    def iniciar_quiz(self, e):
        """
        Inicia o quiz e configura o timer.

        Args:
            e: Objeto evento do Flet.
        """
        if not self.estado_quiz.quiz_iniciado:
            self.estado_quiz.quiz_iniciado = True
            self.iniciar_timer()
            self.proxima_pergunta(e)

    def proxima_pergunta(self, e):
        """
        Carrega e exibe a próxima pergunta do quiz.
        Se não houver mais perguntas, o quiz é finalizado.

        Args:
            e: Objeto evento do Flet.
        """
        if self.estado_quiz.pergunta_atual < len(self.quiz_logic.questions):
            pergunta_atual = self.quiz_logic.questions[
                self.estado_quiz.pergunta_atual
            ]
            pergunta = Pergunta(
                pergunta_atual[0], pergunta_atual[1:5], pergunta_atual[5]
            )
            exibir_pergunta(self.page, pergunta, self.estado_quiz, self)
            self.estado_quiz.proxima_pergunta()
            self.texto_tempo = self.page.controls[0].controls[0]
        else:
            self.finalizar_quiz(e)
        self.page.update()

    def verificar_resposta(self, e):
        """
        Verifica a resposta selecionada pelo usuário, 
        atualiza a pontuação e fornece feedback visual e sonoro.

        Args:
            e: Objeto evento do Flet.
        """
        if not self.estado_quiz.quiz_finalizado:
            resposta_correta = self.quiz_logic.load_question()[2]
            botao_clicado = e.control

            if e.control.data == resposta_correta:
                self.estado_quiz.pontuacao += 1
                if self.som_ativado:
                    reproduzir_audio("certo")
                piscar_verde(botao_clicado) 
            else:
                if self.som_ativado:
                    reproduzir_audio("errado")
                piscar_vermelho(botao_clicado) 

            def proxima_pergunta_com_atraso():
                """
                Função auxiliar para adicionar um atraso 
                antes de carregar a próxima pergunta.
                """
                time.sleep(0.5)
                self.proxima_pergunta(e)

            threading.Timer(0.1, proxima_pergunta_com_atraso).start()

    def finalizar_quiz(self, e):
        """
        Finaliza o quiz, para o timer e exibe os resultados.

        Args:
            e: Objeto evento do Flet.
        """
        self.parar_timer()
        self.estado_quiz.quiz_finalizado = True
        self.estado_quiz.quiz_iniciado = False 
        if not self.modal_aberto:
            exibir_resultados(self.page, self.estado_quiz, self)

    def voltar_ao_inicio(self, e):
        """Volta à tela inicial do quiz, fechando o modal se necessário."""
        self.fechar_modal(e)  # Garante que o modal seja fechado antes
        self.exibir_tela_inicial() 

    def fechar_modal(self, e):
        """
        Fecha o modal de resultados, se estiver aberto.

        Args:
            e: Objeto evento do Flet.
        """
        for overlay in self.page.overlay:
            if isinstance(overlay, ft.AlertDialog) and overlay.open:
                overlay.open = False
                self.modal_aberto = False
                self.page.update()
                break 

    def iniciar_timer(self):
        """Inicia o timer do quiz e configura a atualização do tempo."""

        def atualizar_tempo():
            """
            Função auxiliar para atualizar o tempo restante 
            do quiz a cada segundo. 
            """
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
        """Para o timer do quiz."""
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

    def atualizar_texto_tempo(self):
        """Atualiza o texto do tempo restante na interface do usuário."""
        if self.texto_tempo:
            horas, resto = divmod(self.estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            self.texto_tempo.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            self.page.update()

