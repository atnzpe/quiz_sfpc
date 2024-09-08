# Importa a biblioteca Flet para a criação de interfaces de usuário.
import flet as ft

# Importa a biblioteca threading para lidar com multithreading.
import threading

# Importa as classes Pergunta e EstadoQuiz, que são usadas para modelar os dados do quiz.
from .models import Pergunta, EstadoQuiz

# Importa a classe QuizLogic, que lida com a lógica principal do quiz.
from quiz_logic import QuizLogic

# Importa funções do módulo views que são usadas para exibir diferentes partes da interface do quiz.
from .views import (
    exibir_tela_inicial,  # Função para exibir a tela inicial.
    exibir_pergunta,  # Função para exibir a pergunta atual.
    exibir_resultados,  # Função para exibir os resultados do quiz.
    reproduzir_audio,  # Função para reproduzir efeitos sonoros.
)


class QuizController:
    """
    Classe responsável por controlar o fluxo e a lógica do quiz.
    Ela gerencia o estado do quiz, as perguntas, o tempo, a pontuação e a interface do usuário.
    """

    def __init__(self, page: ft.Page, switch_tema, som_ativado):
        """
        Inicializa o controlador do quiz.

        Args:
            page (ft.Page): A página Flet principal do aplicativo.
            switch_tema: O widget switch que controla o tema da página (claro/escuro).
            som_ativado (bool): Indica se os efeitos sonoros estão ativados.
        """
        self.page = page  # A página Flet que o controlador irá gerenciar.
        self.switch_tema = (
            switch_tema  # O widget switch que controla o tema da página.
        )
        self.som_ativado = som_ativado  # Indica se o som está ativado.
        self.estado_quiz = EstadoQuiz()  # Uma instância da classe EstadoQuiz que mantém o estado do quiz.
        self.quiz_logic = (
            QuizLogic()
        )  # Uma instância da classe QuizLogic que lida com a lógica do quiz.
        self.timer = None  # O timer que controla o tempo restante do quiz, inicialmente definido como None.
        self.texto_tempo = (
            None  # O widget de texto que exibe o tempo restante do quiz na tela.
        )
        self.modal_aberto = (
            False  # Indica se o modal de resultados está aberto ou fechado.
        )
        self.exibir_tela_inicial()  # Exibe a tela inicial do quiz quando o controlador é inicializado.

    def exibir_tela_inicial(self):
        """Exibe a tela inicial do quiz."""
        self.parar_timer()  # Para o timer do quiz, se estiver em execução.
        self.estado_quiz = (
            EstadoQuiz()
        )  # Reinicializa o estado do quiz para um novo quiz.
        self.page.clean()  # Limpa todos os widgets da página atual.
        exibir_tela_inicial(
            self.page, self
        )  # Chama a função exibir_tela_inicial do módulo views para exibir a tela inicial na página.
        self.page.update()  # Atualiza a interface do usuário para mostrar as mudanças.

    def iniciar_quiz(self, e):
        """
        Inicia o quiz.

        Args:
            e: O evento Flet que acionou a chamada da função, geralmente um clique de botão.
        """
        # Verifica se o quiz ainda não foi iniciado.
        if not self.estado_quiz.quiz_iniciado:
            self.estado_quiz.quiz_iniciado = (
                True  # Define o estado do quiz como iniciado.
            )
            self.iniciar_timer()  # Inicia o timer do quiz.
            self.proxima_pergunta(e)  # Exibe a próxima pergunta (primeira pergunta neste caso).

    def proxima_pergunta(self, e):
        """
        Carrega e exibe a próxima pergunta do quiz.

        Args:
            e: O evento Flet que acionou a chamada da função.
        """
        # Verifica se ainda há perguntas para serem exibidas.
        if self.estado_quiz.pergunta_atual < len(self.quiz_logic.questions):
            # Obtém a pergunta atual da lista de perguntas no objeto quiz_logic.
            pergunta_atual = self.quiz_logic.questions[
                self.estado_quiz.pergunta_atual
            ]
            # Cria uma nova instância da classe Pergunta com os dados da pergunta atual.
            pergunta = Pergunta(
                pergunta_atual[0], pergunta_atual[1:5], pergunta_atual[5]
            )
            # Chama a função exibir_pergunta no módulo views para exibir a pergunta na interface do usuário.
            exibir_pergunta(self.page, pergunta, self.estado_quiz, self)
            # Incrementa o índice da pergunta atual para a próxima pergunta.
            self.estado_quiz.pergunta_atual += 1

            # Obtém a referência para o widget de texto que exibe o tempo restante do quiz.
            self.texto_tempo = self.page.controls[0].controls[0]
        else:
            # Se não houver mais perguntas, finaliza o quiz.
            self.finalizar_quiz(e)
        self.page.update()  # Atualiza a interface do usuário para mostrar as mudanças.

    def verificar_resposta(self, e):
        """
        Verifica a resposta selecionada pelo usuário.

        Args:
            e: O evento Flet que acionou a chamada da função, geralmente um clique de botão.
        """
        # Verifica se o quiz ainda não foi finalizado.
        if not self.estado_quiz.quiz_finalizado:
            # Obtém o índice da resposta correta da pergunta atual.
            resposta_correta = self.quiz_logic.load_question()[2]
            # Verifica se o índice da resposta selecionada pelo usuário corresponde ao índice da resposta correta.
            if e.control.data == resposta_correta:
                # Se a resposta estiver correta, aumenta a pontuação do quiz.
                self.estado_quiz.pontuacao += 1
                # Se os efeitos sonoros estiverem ativados, reproduz o som de resposta correta.
                if self.som_ativado:
                    reproduzir_audio("certo")
            else:
                # Se os efeitos sonoros estiverem ativados, reproduz o som de resposta incorreta.
                if self.som_ativado:
                    reproduzir_audio("errado")
            # Carrega e exibe a próxima pergunta do quiz.
            self.proxima_pergunta(e)

    def finalizar_quiz(self, e):
        """
        Finaliza o quiz.

        Args:
            e: O evento Flet que acionou a chamada da função.
        """
        self.parar_timer()  # Para o timer do quiz.
        self.estado_quiz.quiz_finalizado = True  # Define o estado do quiz como finalizado.
        self.estado_quiz.quiz_iniciado = (
            False  # Define o estado do quiz como não iniciado.
        )
        # Verifica se o modal de resultados já está aberto.
        if not self.modal_aberto:
            # Se o modal não estiver aberto, chama a função exibir_resultados do módulo views para mostrar os resultados do quiz.
            exibir_resultados(self.page, self.estado_quiz, self)

    def voltar_ao_inicio(self, e):
        """
        Volta para a tela inicial do quiz.

        Args:
            e: O evento Flet que acionou a chamada da função.
        """
        print("Voltando ao início...")  # Imprime uma mensagem de depuração no console.

        # Fecha o modal de resultados, se estiver aberto.
        self.fechar_modal(e)

        # Reinicia o estado do quiz para um novo quiz.
        self.estado_quiz = EstadoQuiz()
        # Reinicia a lógica do quiz.
        self.quiz_logic = QuizLogic()
        # Exibe a tela inicial do quiz.
        self.exibir_tela_inicial()
        # Atualiza a interface do usuário para refletir as mudanças.
        self.page.update()

        print("Tela inicial exibida.")  # Imprime uma mensagem de depuração no console.

    def fechar_modal(self, e):
        """
        Fecha o modal de resultados, se estiver aberto.

        Args:
            e: O evento Flet que acionou a chamada da função.
        """
        # Itera sobre os widgets de overlay na página (modais, etc.).
        for overlay in self.page.overlay:
            # Verifica se o overlay é um AlertDialog e se está aberto.
            if isinstance(overlay, ft.AlertDialog) and overlay.open:
                # Se for um AlertDialog aberto, define o estado 'open' como False para fechá-lo.
                overlay.open = False
                # Define o estado do modal como fechado.
                self.modal_aberto = False
                print("Fechou o Modal")
                # Atualiza a interface do usuário para refletir as mudanças.
                self.page.update()
                print("Chamado voltar ao inicio")
                break  # Sai do loop, pois o modal já foi fechado.

    def iniciar_timer(self):
        """Inicia o timer do quiz."""

        # Define uma função interna chamada 'atualizar_tempo', que será executada a cada segundo pelo timer.
        def atualizar_tempo():
            """Atualiza o tempo restante do quiz a cada segundo."""
            # Verifica se o tempo restante é maior que zero e se o quiz está em andamento.
            if (
                self.estado_quiz.tempo_restante > 0
                and self.estado_quiz.quiz_iniciado
            ):
                # Decrementa o tempo restante do quiz em um segundo.
                self.estado_quiz.tempo_restante -= 1
                # Atualiza o widget de texto que exibe o tempo restante na tela.
                self.atualizar_texto_tempo()
                # Cria uma nova instância do timer que chama a função 'atualizar_tempo' novamente após um segundo.
                self.timer = threading.Timer(1, atualizar_tempo)
                # Inicia o timer.
                self.timer.start()
            else:
                # Se o tempo restante for zero ou o quiz não estiver em andamento, finaliza o quiz.
                self.finalizar_quiz(None)

        # Atualiza o widget de texto que exibe o tempo restante na tela.
        self.atualizar_texto_tempo()
        # Cria uma nova instância do timer que chama a função 'atualizar_tempo' após um segundo.
        self.timer = threading.Timer(1, atualizar_tempo)
        # Inicia o timer.
        self.timer.start()

    def parar_timer(self):
        """Para o timer do quiz."""
        # Verifica se o timer está em execução.
        if self.timer is not None:
            # Se o timer estiver em execução, cancela a sua execução.
            self.timer.cancel()
            # Define o timer como None, indicando que ele não está mais em execução.
            self.timer = None

    def atualizar_texto_tempo(self):
        """Atualiza o widget de texto que exibe o tempo restante do quiz na tela."""
        # Verifica se o widget de texto do tempo restante está definido.
        if self.texto_tempo:
            # Calcula as horas, minutos e segundos restantes a partir do tempo restante em segundos.
            horas, resto = divmod(self.estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            # Formata o tempo restante como uma string no formato HH:MM:SS.
            tempo_formatado = f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            # Define o valor do widget de texto do tempo restante como o tempo formatado.
            self.texto_tempo.value = tempo_formatado
            # Atualiza a interface do usuário para mostrar a mudança no widget de texto do tempo restante.
            self.page.update()
