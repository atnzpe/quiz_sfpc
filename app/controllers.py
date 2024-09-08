import flet as ft  # Importa a biblioteca Flet para criar a interface do usuário
import threading  # Importa a biblioteca threading para usar threads
import time
from .models import Pergunta, EstadoQuiz  # Importa as classes Pergunta e EstadoQuiz
from quiz_logic import (
    QuizLogic,
)  # Importa a classe QuizLogic que gerencia a lógica do quiz
from .views import (
    exibir_tela_inicial,  # Importa a função para exibir a tela inicial
    exibir_pergunta,  # Importa a função para exibir uma pergunta
    exibir_resultados,  # Importa a função para exibir os resultados
    reproduzir_audio,
    piscar_verde,
    piscar_vermelho,  # Importe as funções de animação# Importa a função para reproduzir áudio
)


class QuizController:
    """Classe que controla a lógica do quiz."""

    def __init__(self, page: ft.Page, switch_tema, som_ativado):
        """Inicializa o controlador do quiz."""
        self.page = page  # Define a página Flet que o controlador irá gerenciar
        self.switch_tema = switch_tema  # Armazena a referência ao switch de tema
        self.som_ativado = som_ativado  # Define se o som está ativado ou desativado
        self.estado_quiz = EstadoQuiz()  # Cria uma instância da classe EstadoQuiz
        self.quiz_logic = QuizLogic()  # Cria uma instância da classe QuizLogic
        self.timer = None  # Inicializa o timer como None
        self.texto_tempo = (
            None  # Inicializa o widget de texto do tempo restante como None
        )
        self.modal_aberto = False  # Inicializa o estado do modal como fechado
        self.exibir_tela_inicial()  # Exibe a tela inicial do quiz

    def exibir_tela_inicial(self):
        """Exibe a tela inicial do quiz."""
        self.parar_timer()  # Para o timer, caso esteja em execução
        self.estado_quiz = EstadoQuiz()  # Reinicia o estado do quiz
        self.page.clean()  # Limpa a página atual
        exibir_tela_inicial(
            self.page, self
        )  # Chama a função para exibir a tela inicial em views.py
        self.page.update()  # Atualiza a página

    def iniciar_quiz(self, e):
        """Inicia o quiz."""
        # Verifica se o quiz já está iniciado
        if not self.estado_quiz.quiz_iniciado:
            self.estado_quiz.quiz_iniciado = True  # Define o quiz como iniciado
            self.iniciar_timer()  # Inicia o timer do quiz
            self.proxima_pergunta(e)  # Exibe a próxima pergunta

    def proxima_pergunta(self, e):
        """Carrega e exibe a próxima pergunta."""
        # Verifica se ainda há perguntas a serem exibidas
        if self.estado_quiz.pergunta_atual < len(self.quiz_logic.questions):
            # Obtém a pergunta atual da lista de perguntas
            pergunta_atual = self.quiz_logic.questions[self.estado_quiz.pergunta_atual]
            # Cria uma instância da classe Pergunta com os dados da pergunta atual
            pergunta = Pergunta(
                pergunta_atual[0], pergunta_atual[1:5], pergunta_atual[5]
            )
            # Chama a função exibir_pergunta em views.py para exibir a pergunta
            exibir_pergunta(self.page, pergunta, self.estado_quiz, self)
            # Incrementa o contador de perguntas
            self.estado_quiz.pergunta_atual += 1

            # Armazena a referência para o widget ft.Text do timer
            self.texto_tempo = self.page.controls[0].controls[0]
        else:
            # Se não houver mais perguntas, finaliza o quiz
            self.finalizar_quiz(e)
        self.page.update()  # Atualiza a página

    def verificar_resposta(self, e):
        """Verifica a resposta selecionada pelo usuário."""
        if not self.estado_quiz.quiz_finalizado:
            resposta_correta = self.quiz_logic.load_question()[2]
            botao_clicado = e.control  # Obtém a referência ao botão clicado

            if e.control.data == resposta_correta:
                self.estado_quiz.pontuacao += 1
                if self.som_ativado:
                    reproduzir_audio("certo")
                piscar_verde(botao_clicado)  # Chama a função de views.py
            else:
                if self.som_ativado:
                    reproduzir_audio("errado")
                piscar_vermelho(botao_clicado)  # Chama a função de views.py

            # Aguarda a animação terminar antes de ir para a próxima pergunta
            def proxima_pergunta_com_atraso():
                time.sleep(0.5)  # Ajuste o tempo de atraso aqui
                self.proxima_pergunta(e)

            threading.Timer(0.1, proxima_pergunta_com_atraso).start()

    def finalizar_quiz(self, e):
        """Finaliza o quiz."""
        self.parar_timer()  # Para o timer do quiz
        self.estado_quiz.quiz_finalizado = True  # Define o quiz como finalizado
        self.estado_quiz.quiz_iniciado = False  # Define o quiz como não iniciado
        # Verifica se o modal de resultados já está aberto
        if not self.modal_aberto:
            # Chama a função exibir_resultados em views.py para exibir os resultados
            exibir_resultados(self.page, self.estado_quiz, self)

    def voltar_ao_inicio(self, e):
        """Volta à tela inicial."""
        print("Voltando ao início...")  # Mensagem de debug

        # Fecha o modal de resultados explicitamente
        self.fechar_modal(e)

        self.estado_quiz = EstadoQuiz()  # Reinicia o estado do quiz
        self.quiz_logic = QuizLogic()  # Reinicia a lógica do quiz
        self.exibir_tela_inicial()  # Exibe a tela inicial
        self.page.update()  # Atualiza a página

        print("Tela inicial exibida.")  # Mensagem de debug

    def fechar_modal(self, e):
        """Fecha o modal de resultados, se estiver aberto."""
        # Itera sobre os overlays da página
        for overlay in self.page.overlay:
            # Verifica se o overlay é um AlertDialog e se está aberto
            if isinstance(overlay, ft.AlertDialog) and overlay.open:
                # Fecha o modal
                overlay.open = False
                # Define o estado do modal como fechado
                self.modal_aberto = False
                print("Fechou o Modal")

                # Atualiza a página
                self.page.update()
                print("Chamado voltaar ao incio")
                self.voltar_ao_inicio(e)
                self.page.update()
                break  # Sai do loop após fechar o modal

    def iniciar_timer(self):
        """Inicia o timer da prova."""

        def atualizar_tempo():
            """Atualiza o tempo restante a cada segundo."""
            # Verifica se o tempo restante é maior que zero e se o quiz está iniciado
            if self.estado_quiz.tempo_restante > 0 and self.estado_quiz.quiz_iniciado:
                # Decrementa o tempo restante
                self.estado_quiz.tempo_restante -= 1
                # Atualiza o texto do tempo restante na tela
                self.atualizar_texto_tempo()
                # Cria um novo timer que chama a função atualizar_tempo após 1 segundo
                self.timer = threading.Timer(1, atualizar_tempo)
                # Inicia o timer
                self.timer.start()
            else:
                # Finaliza o quiz se o tempo acabar
                self.finalizar_quiz(None)

        # Atualiza o texto do tempo restante na tela
        self.atualizar_texto_tempo()
        # Cria um novo timer que chama a função atualizar_tempo após 1 segundo
        self.timer = threading.Timer(1, atualizar_tempo)
        # Inicia o timer
        self.timer.start()

    def parar_timer(self):
        """Para o timer da prova."""
        # Verifica se o timer está em execução
        if self.timer is not None:
            # Cancela o timer
            self.timer.cancel()
            # Define o timer como None
            self.timer = None

    def atualizar_texto_tempo(self):
        """Atualiza o texto do tempo na tela da pergunta."""
        # Verifica se o widget de texto do tempo restante está definido
        if self.texto_tempo:
            # Calcula as horas, minutos e segundos restantes
            horas, resto = divmod(self.estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            # Define o valor do widget de texto do tempo restante
            self.texto_tempo.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            # Atualiza a página
            self.page.update()
