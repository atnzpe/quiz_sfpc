import flet as ft  # Importa a biblioteca Flet para a interface gráfica
import threading  # Importa a biblioteca threading para usar threads
import time  # Importa a biblioteca time para usar funções relacionadas a tempo

from .models import (
    Pergunta,
    EstadoQuiz,
)  # Importa as classes Pergunta e EstadoQuiz
from quiz_logic import (
    QuizLogic,
)  # Importa a classe QuizLogic (provavelmente de um arquivo quiz_logic.py)
from .views import (  # Importa funções para exibir diferentes telas do aplicativo
    exibir_tela_inicial,
    exibir_pergunta,
    exibir_resultados,
    #reproduzir_audio,
    #piscar_verde,
    #piscar_vermelho,
)

# Define a classe QuizController
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
        self.page = page  # Armazena a página Flet
        self.switch_tema = switch_tema  # Armazena o controle do switch de tema
        self.som_ativado = som_ativado  # Armazena o estado do som
        self.estado_quiz = EstadoQuiz()  # Cria uma instância da classe EstadoQuiz
        self.quiz_logic = (
            QuizLogic()
        )  # Cria uma instância da classe QuizLogic
        self.timer = None  # Inicializa o timer como None
        self.texto_tempo = (
            None  # Inicializa o texto do tempo como None
        )
        self.modal_aberto = (
            False  # Inicializa o estado do modal como fechado
        )
        self.exibir_tela_inicial()  # Exibe a tela inicial ao iniciar

    def exibir_tela_inicial(self):
        """Exibe a tela inicial do quiz, reiniciando o estado do jogo."""
        self.parar_timer()  # Para o timer, se estiver ativo
        self.estado_quiz.reiniciar()  # Reinicia o estado do quiz
        self.page.clean()  # Limpa a página
        exibir_tela_inicial(
            self.page, self
        )  # Exibe a tela inicial usando a função importada de views.py
        self.page.update()  # Atualiza a página

    def iniciar_quiz(self, e):
        """
        Inicia o quiz e configura o timer.

        Args:
            e: Objeto evento do Flet.
        """
        # Verifica se o quiz já foi iniciado
        if not self.estado_quiz.quiz_iniciado:
            self.estado_quiz.quiz_iniciado = True  # Define o quiz como iniciado
            self.iniciar_timer()  # Inicia o timer
            self.proxima_pergunta(e)  # Carrega a próxima pergunta (primeira, nesse caso)

    def proxima_pergunta(self, e):
        """
        Carrega e exibe a próxima pergunta do quiz.
        Se não houver mais perguntas, o quiz é finalizado.

        Args:
            e: Objeto evento do Flet.
        """
        # Verifica se ainda há perguntas a serem exibidas
        if self.estado_quiz.pergunta_atual < len(
            self.quiz_logic.questions
        ):
            # Obtém a pergunta atual da lista de perguntas
            pergunta_atual = self.quiz_logic.questions[
                self.estado_quiz.pergunta_atual
            ]
            # Cria uma instância da classe Pergunta com os dados da pergunta atual
            pergunta = Pergunta(
                pergunta_atual[0],
                pergunta_atual[1:5],
                pergunta_atual[5],
            )
            # Exibe a pergunta usando a função importada de views.py
            exibir_pergunta(
                self.page, pergunta, self.estado_quiz, self
            )

            # Correção: Incrementar a pergunta_atual DEPOIS de exibir a pergunta
            self.estado_quiz.proxima_pergunta()

            # Define o texto do tempo restante
            self.texto_tempo = self.page.controls[0].controls[0]
        else:
            # Se não houver mais perguntas, finaliza o quiz
            self.finalizar_quiz(e)
        self.page.update()  # Atualiza a página

    def verificar_resposta(self, e):
        """
        Verifica a resposta selecionada pelo usuário.
        """
        if not self.estado_quiz.quiz_finalizado:
            # Corrigido: Usar o índice da resposta correta retornado por load_question()
            _, _, resposta_correta = self.quiz_logic.load_question()
            botao_clicado = e.control

            if e.control.data == resposta_correta:
                self.estado_quiz.pontuacao += 1
                #if self.som_ativado:
                    #reproduzir_audio("certo")
                #piscar_verde(botao_clicado)
                #else: # <-- Bloco else movido para cá
                #if self.som_ativado:
                    #reproduzir_audio("errado")
                #piscar_vermelho(botao_clicado)  # Faz o botão piscar em vermelho
            
            # Define a função que será executada após um pequeno atraso
            def proxima_pergunta_com_atraso():
                """
                Função auxiliar para adicionar um atraso
                antes de carregar a próxima pergunta.
                """
                time.sleep(
                    0.5
                )  # Aguarda 0.5 segundos antes de carregar a próxima pergunta
                self.proxima_pergunta(
                    e
                )  # Carrega a próxima pergunta

            # Cria um timer para executar a função proxima_pergunta_com_atraso() após 0.1 segundos
            threading.Timer(0.1, proxima_pergunta_com_atraso).start()

    def finalizar_quiz(self, e):
        """
        Finaliza o quiz, para o timer e exibe os resultados.

        Args:
            e: Objeto evento do Flet.
        """
        self.parar_timer()  # Para o timer
        self.estado_quiz.quiz_finalizado = (
            True  # Define o quiz como finalizado
        )
        self.estado_quiz.quiz_iniciado = (
            False  # Define o quiz como não iniciado
        )
        # Verifica se o modal de resultados já está aberto
        if not self.modal_aberto:
            # Exibe os resultados usando a função importada de views.py
            exibir_resultados(self.page, self.estado_quiz, self)

    def voltar_ao_inicio(self, e):
        """Volta à tela inicial do quiz, fechando o modal se necessário."""
        self.fechar_modal(
            e
        )  # Fecha o modal de resultados, se estiver aberto
        self.exibir_tela_inicial()  # Exibe a tela inicial

    def fechar_modal(self, e):
        """
        Fecha o modal de resultados, se estiver aberto.

        Args:
            e: Objeto evento do Flet.
        """
        # Itera pelos elementos da interface que estão na camada de overlay (sobreposição)
        for overlay in self.page.overlay:
            # Verifica se o elemento é um AlertDialog e se está aberto
            if isinstance(overlay, ft.AlertDialog) and overlay.open:
                overlay.open = False  # Fecha o AlertDialog
                self.modal_aberto = False  # Define o modal como fechado
                self.page.update()  # Atualiza a página
                break  # Sai do loop, já que encontrou o modal

    def iniciar_timer(self):
        """Inicia o timer do quiz e configura a atualização do tempo."""

        # Define a função que será executada a cada segundo pelo timer
        def atualizar_tempo():
            """
            Função auxiliar para atualizar o tempo restante
            do quiz a cada segundo.
            """
            # Verifica se ainda há tempo restante e se o quiz está em andamento
            if self.estado_quiz.tempo_restante > 0 and self.estado_quiz.quiz_iniciado:
                self.estado_quiz.tempo_restante -= 1  # Decrementa o tempo restante
                self.atualizar_texto_tempo()  # Atualiza o texto do tempo na interface
                # Define o timer para executar a função atualizar_tempo() novamente após 1 segundo
                self.timer = threading.Timer(1, atualizar_tempo)
                self.timer.start()  # Inicia o timer
            else:
                self.finalizar_quiz(
                    None
                )  # Finaliza o quiz se o tempo acabar

        self.atualizar_texto_tempo()  # Atualiza o texto do tempo na interface
        # Define o timer para executar a função atualizar_tempo() após 1 segundo
        self.timer = threading.Timer(1, atualizar_tempo)
        self.timer.start()  # Inicia o timer

    def parar_timer(self):
        """Para o timer do quiz."""
        # Verifica se o timer está ativo
        if self.timer is not None:
            self.timer.cancel()  # Cancela o timer
            self.timer = None  # Define o timer como None

    def atualizar_texto_tempo(self):
        """Atualiza o texto do tempo restante na interface do usuário."""
        # Verifica se o texto do tempo foi definido
        if self.texto_tempo:
            # Calcula as horas, minutos e segundos restantes
            horas, resto = divmod(self.estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            # Formata o tempo restante e define o valor do texto na interface
            self.texto_tempo.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            self.page.update()  # Atualiza a página

