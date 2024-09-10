import gspread  # Importa a biblioteca para interagir com o Google Sheets
from oauth2client.service_account import (
    ServiceAccountCredentials,
)  # Importa a classe para autenticação com o Google
import random  # Importa a biblioteca para gerar números aleatórios
import time  # Importa a biblioteca para trabalhar com tempo
import os  # Importa a biblioteca para interagir com o sistema operacional
import json  # Importa a biblioteca para trabalhar com arquivos JSON
import requests  # Importa a biblioteca para fazer requisições HTTP


class QuizLogic:
    """
    Classe responsável por gerenciar a lógica do quiz, incluindo:
        - Carregamento de perguntas do Google Sheets ou do cache.
        - Verificação de respostas.
        - Controle do tempo do quiz.
        - Gerenciamento do cache de perguntas.
    """

    def __init__(self):
        """
        Inicializa a lógica do quiz, configurando a conexão com o Google Sheets,
        carregando as perguntas e inicializando variáveis de controle.
        """
        # Define o escopo de acesso necessário para a API do Google Sheets
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # Carrega as credenciais da conta de serviço a partir do arquivo JSON
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials_sheets.json", self.scope
        )
        # Autoriza o acesso à API do Google Sheets usando as credenciais
        self.client = gspread.authorize(self.creds)

        # Abre a planilha do Google Sheets pela URL
        self.sheet = self.client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"
        ).sheet1

        # Define o nome do arquivo para armazenar o cache das perguntas
        self.cache_file = "quiz_cache.json"

        # Carrega as perguntas, priorizando o cache se disponível
        self.load_questions()

        # Inicializa variáveis para controlar o estado do quiz
        self.current_question = (
            0  # Índice da pergunta atual, começa na primeira (índice 0)
        )
        self.score = 0  # Pontuação do jogador, começa em 0
        self.time_limit = 3600  # Tempo limite do quiz em segundos (1 hora)
        self.start_time = time.time()  # Armazena o tempo de início do quiz
        self.timer_running = (
            False  # Indica se o timer está em execução, inicialmente não
        )

    def start_timer(self):
        """
        Inicia o cronômetro do quiz, definindo o tempo de início e
        marcando o timer como em execução.
        """
        self.start_time = time.time()
        self.timer_running = True

    def stop_timer(self):
        """
        Para o cronômetro do quiz, marcando o timer como não em execução.
        """
        self.timer_running = False

    def get_time_remaining(self):
        """
        Calcula e retorna o tempo restante no quiz.

        Returns:
            int: O tempo restante em segundos.
        """
        if self.timer_running:
            # Calcula o tempo decorrido desde o início do quiz
            elapsed_time = int(time.time() - self.start_time)
            # Calcula o tempo restante, garantindo que não seja negativo
            self.time_limit = max(0, 3600 - elapsed_time)
        # Retorna o tempo restante
        return self.time_limit

    def load_question(self):
        """
        Carrega a próxima pergunta do quiz. As alternativas já foram 
        embaralhadas previamente em download_and_cache_questions ou
        load_questions_from_cache.

        Returns:
            tuple: Uma tupla contendo:
                - str: O texto da pergunta.
                - list: A lista de opções de resposta.
                - int: O índice da resposta correta na lista de opções.
            Ou None se não houver mais perguntas.
        """
        if self.current_question < len(self.questions):
            # Obtém os dados da pergunta atual da lista de perguntas
            question_data = self.questions[self.current_question]
            # Formata o texto da pergunta, incluindo o número da pergunta
            question_text = f"{self.current_question + 1}. {question_data[0]}"
            # Calcula o índice da resposta correta (0 para 'a', 1 para 'b', etc.)
            correct_answer_index = ord(question_data[5].lower()) - ord("a")

            # Imprime informações de debug sobre a pergunta carregada
            print(f"Carregando pergunta {self.current_question + 1}")
            print(f"Resposta correta: {chr(correct_answer_index + ord('a'))}")

            # Retorna o texto da pergunta, as opções e o índice da resposta correta
            return question_text, question_data[1:5], correct_answer_index
        else:
            # Retorna None se não houver mais perguntas
            return None, None, None

    def check_answer(self, selected_answer: int):
        """
        Verifica se a resposta selecionada pelo usuário está correta.

        Args:
            selected_answer (int): O índice da resposta selecionada na lista
                de opções (0 para 'a', 1 para 'b', etc.).

        Returns:
            str: Uma mensagem indicando se a resposta está correta ou incorreta.
        """
        # Obtém o índice da resposta correta da pergunta atual
        correct_answer_index = self.questions[self.current_question].index(
            self.questions[self.current_question][5]
        ) - 1

        # Compara o índice da resposta selecionada com o índice da resposta correta
        if selected_answer == correct_answer_index:
            # Incrementa a pontuação se a resposta estiver correta
            self.score += 1
            return "Resposta correta!"
        else:
            return "Resposta incorreta."

    def get_final_results(self):
        """
        Retorna os resultados finais do quiz, incluindo a pontuação e
        uma mensagem indicando se o jogador foi aprovado ou reprovado.

        Returns:
            str: Uma string formatada com os resultados finais do quiz.
        """
        return (
            f"Sua pontuação final: {self.score}/40\n"
            f"{'Aprovado!' if self.score >= 32 else 'Reprovado.'}"
        )

    def load_questions(self):
        """
        Carrega as perguntas do quiz, priorizando o cache se houver 
        conexão com a internet, caso contrário, carrega do Google Sheets.
        """
        if self.check_internet_connection():
            self.download_and_cache_questions()
        else:
            self.load_questions_from_cache()

    def check_internet_connection(self):
        """
        Verifica se há conexão com a internet.

        Returns:
            bool: True se houver conexão, False caso contrário.
        """
        try:
            # Tenta acessar o Google para verificar a conexão
            requests.get("http://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def download_and_cache_questions(self):
        """
        Baixa as perguntas da planilha do Google Sheets, embaralha
        as alternativas de cada pergunta, as armazena em cache
        em um arquivo JSON e imprime informações de debug.
        """
        # Obtém todas as linhas da planilha, exceto o cabeçalho
        self.all_questions = self.sheet.get_all_values()[1:]
        # Embaralha a ordem das perguntas aleatoriamente
        random.shuffle(self.all_questions)
        # Seleciona 40 perguntas aleatoriamente para o quiz
        self.questions = random.sample(self.all_questions, 40)

        # Imprime as perguntas após o embaralhamento da ordem
        print("Perguntas originais (após embaralhamento da ordem):")
        for q in self.questions:
            print(q)

        # Embaralha as alternativas de cada pergunta
        for i in range(len(self.questions)):
            # Embaralha apenas as alternativas, mantendo a pergunta e a resposta correta
            random.shuffle(self.questions[i][1:5])
            # Imprime a pergunta com as alternativas embaralhadas para debug
            print(f"Pergunta {i+1} após embaralhar alternativas: {self.questions[i]}")

        # Salva as perguntas embaralhadas no arquivo de cache
        with open(self.cache_file, "w", encoding="utf8") as f:
            json.dump(self.all_questions, f, ensure_ascii=False)

    def load_questions_from_cache(self):
        """
        Carrega as perguntas do arquivo de cache, embaralha as alternativas
        de cada pergunta e imprime informações de debug.
        """
        try:
            # Tenta abrir o arquivo de cache em modo de leitura
            with open(self.cache_file, "r", encoding="utf8") as f:
                # Carrega as perguntas do arquivo JSON
                self.all_questions = json.load(f)
                # Seleciona 40 perguntas aleatoriamente para o quiz
                self.questions = random.sample(self.all_questions, 40)

                # Imprime as perguntas após o embaralhamento da ordem
                print("Perguntas do cache (após embaralhamento da ordem):")
                for q in self.questions:
                    print(q)

                # Embaralha as alternativas de cada pergunta
                for i in range(len(self.questions)):
                    # Embaralha apenas as alternativas, mantendo a pergunta e a resposta correta
                    random.shuffle(self.questions[i][1:5])
                    # Imprime a pergunta com as alternativas embaralhadas para debug
                    print(
                        f"Pergunta {i+1} após embaralhar alternativas: {self.questions[i]}"
                    )

        except FileNotFoundError:
            # Define as listas de perguntas como vazias se o arquivo não for encontrado
            self.all_questions = []
            self.questions = []
