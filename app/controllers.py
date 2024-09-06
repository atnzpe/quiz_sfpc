import flet as ft  # Importa a biblioteca Flet para a interface do usuário
import threading  # Importa o módulo threading para lidar com threads
from .models import (
    Pergunta,
    EstadoQuiz,
)  # Importa as classes Pergunta e EstadoQuiz do arquivo models.py
from quiz_logic import QuizLogic  # Importa a classe QuizLogic do arquivo quiz_logic.py
from .views import (
    exibir_tela_inicial,
    exibir_pergunta,
    exibir_resultados,
    reproduzir_audio,  # Importa a função reproduzir_audio do arquivo views.py
)


# Define a classe QuizController, que controla a lógica do quiz
class QuizController:
    # Método construtor da classe
    def __init__(self, page: ft.Page, switch_tema, som_ativado):
        # Define a página Flet que será controlada pelo controlador
        self.page = page
        # Define o widget switch_tema que controla o tema claro/escuro da página
        self.switch_tema = switch_tema
        # Define se o som do quiz está ativado ou desativado
        self.som_ativado = som_ativado
        # Cria uma instância da classe EstadoQuiz para armazenar o estado atual do quiz
        self.estado_quiz = EstadoQuiz()
        # Cria uma instância da classe QuizLogic para lidar com a lógica do quiz
        self.quiz_logic = QuizLogic()
        # Define o timer do quiz como None inicialmente
        self.timer = None
        # Define o widget texto_tempo como None inicialmente
        self.texto_tempo = None
        # Chama o método exibir_tela_inicial para exibir a tela inicial do quiz
        self.exibir_tela_inicial()

    # Método para exibir a tela inicial do quiz
    def exibir_tela_inicial(self):
        """Exibe a tela inicial do quiz."""
        # Para o timer do quiz, se estiver em execução
        self.parar_timer()
        # Reinicia o estado do quiz
        self.estado_quiz = EstadoQuiz()
        # Limpa a página atual
        self.page.clean()
        # Chama a função exibir_tela_inicial do arquivo views.py para exibir a tela inicial
        exibir_tela_inicial(self.page, self)
        # Atualiza a página para exibir as mudanças
        self.page.update()

    # Método para iniciar o quiz
    def iniciar_quiz(self, e):
        """Inicia o quiz."""
        # Verifica se o quiz já foi iniciado
        if not self.estado_quiz.quiz_iniciado:
            # Define o quiz como iniciado
            self.estado_quiz.quiz_iniciado = True
            # Inicia o timer do quiz
            self.iniciar_timer()
            # Chama o método proxima_pergunta para exibir a primeira pergunta
            self.proxima_pergunta(e)

    # Método para carregar e exibir a próxima pergunta do quiz
    def proxima_pergunta(self, e):
        """Carrega e exibe a próxima pergunta."""
        # Verifica se ainda há perguntas para exibir
        if self.estado_quiz.pergunta_atual < len(self.quiz_logic.questions):
            # Obtém a pergunta atual da lista de perguntas
            pergunta_atual = self.quiz_logic.questions[self.estado_quiz.pergunta_atual]
            # Cria uma instância da classe Pergunta com os dados da pergunta atual
            pergunta = Pergunta(
                pergunta_atual[0], pergunta_atual[1:5], pergunta_atual[5]
            )
            # Chama a função exibir_pergunta do arquivo views.py para exibir a pergunta
            exibir_pergunta(self.page, pergunta, self.estado_quiz, self)
            # Incrementa o contador de perguntas para avançar para a próxima pergunta
            self.estado_quiz.pergunta_atual += 1

            # Armazena a referência para o widget ft.Text do timer
            self.texto_tempo = self.page.controls[0].controls[0]

        # Se não houver mais perguntas, chama o método finalizar_quiz
        else:
            self.finalizar_quiz(e)
        # Atualiza a página para exibir as mudanças
        self.page.update()

    # Método para verificar a resposta selecionada pelo usuário
    def verificar_resposta(self, e):
        """Verifica a resposta selecionada pelo usuário."""
        # Verifica se o quiz ainda está em andamento
        if not self.estado_quiz.quiz_finalizado:
            # Obtém o índice da resposta correta da pergunta atual
            resposta_correta = self.quiz_logic.load_question()[2]
            # Compara o índice da resposta selecionada pelo usuário com o índice da resposta correta
            if e.control.data == resposta_correta:
                # Se a resposta estiver correta, incrementa a pontuação do usuário
                self.estado_quiz.pontuacao += 1
                # Se o som estiver ativado, reproduz um áudio de resposta correta
                if self.som_ativado:
                    reproduzir_audio("certo")
            # Se a resposta estiver incorreta e o som estiver ativado, reproduz um áudio de resposta incorreta
            else:
                if self.som_ativado:
                    reproduzir_audio("errado")
            # Chama o método proxima_pergunta para exibir a próxima pergunta
            self.proxima_pergunta(e)

    # Método para finalizar o quiz
    def finalizar_quiz(self, e):
        """Finaliza o quiz."""
        # Para o timer do quiz
        self.parar_timer()
        # Define o quiz como finalizado
        self.estado_quiz.quiz_finalizado = True
        # Define o quiz como não iniciado
        self.estado_quiz.quiz_iniciado = False
        # Chama a função exibir_resultados do arquivo views.py para exibir os resultados
        exibir_resultados(self.page, self.estado_quiz, self)

    # Método para voltar à tela inicial do quiz
    def voltar_ao_inicio(self, e):
        """Volta à tela inicial."""
        # Fecha o modal de resultados, se estiver aberto
        for overlay in self.page.overlay:
            if isinstance(overlay, ft.AlertDialog) and overlay.open:
                overlay.open = False
                break

        # Reinicia o estado do quiz
        self.estado_quiz = EstadoQuiz()
        # Reinicia a lógica do quiz
        self.quiz_logic = QuizLogic()
        # Chama o método exibir_tela_inicial para exibir a tela inicial
        self.exibir_tela_inicial()

    # Método para iniciar o timer do quiz
    def iniciar_timer(self):
        """Inicia o timer da prova."""

        # Define uma função interna para atualizar o tempo restante do quiz
        def atualizar_tempo():
            """Atualiza o tempo restante a cada segundo."""
            # Verifica se o quiz está em andamento
            if self.estado_quiz.tempo_restante > 0 and self.estado_quiz.quiz_iniciado:
                # Decrementa o tempo restante em 1 segundo
                self.estado_quiz.tempo_restante -= 1
                # Chama o método atualizar_texto_tempo para atualizar o texto do timer na tela
                self.atualizar_texto_tempo()
                # Agenda a próxima chamada da função atualizar_tempo em 1 segundo
                self.timer = threading.Timer(1, atualizar_tempo)
                # Inicia o timer
                self.timer.start()
            # Se o quiz não estiver em andamento, chama o método finalizar_quiz
            else:
                self.finalizar_quiz(None)

        # Chama o método atualizar_texto_tempo para atualizar o texto do timer na tela
        self.atualizar_texto_tempo()
        # Agenda a primeira chamada da função atualizar_tempo em 1 segundo
        self.timer = threading.Timer(1, atualizar_tempo)
        # Inicia o timer
        self.timer.start()

    # Método para parar o timer do quiz
    def parar_timer(self):
        """Para o timer da prova."""
        # Verifica se o timer está em execução
        if self.timer is not None:
            # Cancela o timer
            self.timer.cancel()
            # Define o timer como None
            self.timer = None

    # Método para atualizar o texto do timer na tela
    def atualizar_texto_tempo(self):
        """Atualiza o texto do tempo na tela da pergunta."""
        # Verifica se o widget texto_tempo está definido
        if self.texto_tempo:
            # Calcula as horas, minutos e segundos restantes a partir do tempo restante
            horas, resto = divmod(self.estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            # Define o valor do widget texto_tempo com o tempo restante formatado
            self.texto_tempo.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            # Atualiza a página para exibir as mudanças
            self.page.update()
