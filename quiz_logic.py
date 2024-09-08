import gspread  # Importa biblioteca para interagir com o Google Sheets
from oauth2client.service_account import (
    ServiceAccountCredentials,
)  # Importa classe para autenticação
import random  # Importa biblioteca para gerar números aleatórios
import time  # Importa biblioteca para trabalhar com tempo
import os  # Importa biblioteca para interagir com o sistema operacional
import json  # Importa biblioteca para trabalhar com JSON
import requests  # Importa biblioteca para fazer requisições HTTP


# Define a classe QuizLogic, responsável por gerenciar a lógica do quiz
class QuizLogic:
    """
    Gerencia a lógica do quiz, incluindo carregamento de perguntas,
    verificação de respostas, controle do tempo e cache.
    """

    # Define o método construtor da classe
    def __init__(self):
        """Inicializa a lógica do quiz, carregando perguntas e configurando o cache."""

        # Define o escopo de acesso necessário ao Google Sheets
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # Carrega as credenciais da conta de serviço do arquivo 'credentials_sheets.json'
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials_sheets.json", self.scope
        )
        # Autoriza o acesso ao Google Sheets usando as credenciais
        self.client = gspread.authorize(self.creds)

        # Abre a planilha do Google Sheets
        self.sheet = self.client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"
        ).sheet1

        # Define o nome do arquivo de cache JSON
        self.cache_file = "quiz_cache.json"

        # Carrega as perguntas (do cache ou do Google Sheets)
        self.load_questions()

        # Inicializa variáveis de controle
        self.current_question = 0  # Índice da pergunta atual
        self.score = 0  # Pontuação do usuário
        self.time_limit = 3600  # Tempo limite do quiz em segundos (1 hora)
        self.start_time = time.time()  # Tempo de início do quiz
        self.timer_running = False  # Indica se o timer está em execução

    # Define o método para iniciar o timer
    def start_timer(self):
        """Inicia o cronômetro do quiz."""
        self.start_time = time.time()  # Define o tempo de início
        self.timer_running = True  # Define o timer como em execução

    # Define o método para parar o timer
    def stop_timer(self):
        """Para o cronômetro do quiz."""
        self.timer_running = False  # Define o timer como parado

    # Define o método para obter o tempo restante
    def get_time_remaining(self):
        """Calcula e retorna o tempo restante no quiz."""
        # Verifica se o timer está em execução
        if self.timer_running:
            # Calcula o tempo decorrido
            elapsed_time = int(time.time() - self.start_time)
            # Calcula o tempo restante
            self.time_limit = max(0, 3600 - elapsed_time)
        # Retorna o tempo restante
        return self.time_limit

    # Define o método para carregar a próxima pergunta
    def load_question(self):
        """
        Carrega a próxima pergunta do quiz, embaralha as opções de resposta
        e retorna a pergunta, opções e índice da resposta correta.
        """
        # Verifica se ainda há perguntas para carregar
        if self.current_question < len(self.questions):
            # Obtém os dados da pergunta atual
            question_data = self.questions[self.current_question]
            # Define o texto da pergunta
            question_text = f"{self.current_question + 1}. {question_data[0]}"
            # Armazenar o índice da resposta correta ANTES de embaralhar
            correct_answer_index = ord(question_data[5].lower()) - ord('a')
            # Define as opções de resposta
            options = question_data[1:5]
            # Embaralha as opções de resposta
            random.shuffle(options)
            # Cria uma lista com as letras das opções de resposta
            #option_letters = ["a", "b", "c", "d"]
            # Encontra o índice da resposta correta
            #correct_answer = options.index(question_data[5])
            # Retorna o texto da pergunta, as opções de resposta e o índice da resposta correta
            return question_text, options, correct_answer_index
        else:
            # Retorna None se não houver mais perguntas
            return None, None, None

    # Define o método para verificar se a resposta está correta
    def check_answer(self, selected_answer):
        """Verifica se a resposta selecionada está correta."""
        # Compara o índice da resposta selecionada com o índice da resposta correta
        if (
            selected_answer
            == self.questions[self.current_question].index(
                self.questions[self.current_question][5]
            )
            - 1
        ):
            # Se a resposta estiver correta, incrementa a pontuação
            self.score += 1
            # Retorna uma mensagem de resposta correta
            return "Resposta correta!"
        else:
            # Retorna uma mensagem de resposta incorreta
            return "Resposta incorreta."

    # Define o método para obter os resultados finais do quiz
    def get_final_results(self):
        """Retorna os resultados finais do quiz, incluindo a pontuação e a mensagem de aprovação/reprovação."""
        # Retorna a pontuação final e a mensagem de aprovação ou reprovação
        return f"Sua pontuação final: {self.score}/40\n{'Aprovado!' if self.score >= 32 else 'Reprovado.'}"

    # Define o método para carregar as perguntas
    def load_questions(self):
        """Carrega as perguntas do cache ou do Google Sheets, dependendo da conectividade."""
        # Verifica se há conexão com a internet
        if self.check_internet_connection():
            # Baixa as perguntas do Google Sheets e as armazena em cache
            self.download_and_cache_questions()
        else:
            # Carrega as perguntas do cache
            self.load_questions_from_cache()

    # Define o método para verificar a conexão com a internet
    def check_internet_connection(self):
        """Verifica se há conexão com a internet."""
        try:
            # Tenta fazer uma requisição ao Google
            response = requests.get("http://www.google.com", timeout=5)
            # Retorna True se a requisição for bem-sucedida
            return True
        except requests.ConnectionError:
            # Retorna False se houver um erro de conexão
            return False

    # Define o método para baixar e armazenar as perguntas em cache
    def download_and_cache_questions(self):
        """Baixa as perguntas do Google Sheets, embaralha e as armazena em cache."""
        # Obtém todas as linhas da planilha (exceto o cabeçalho)
        self.all_questions = self.sheet.get_all_values()[1:]
        # Embaralha as perguntas
        random.shuffle(self.all_questions)
        # Seleciona aleatoriamente 40 perguntas
        self.questions = random.sample(self.all_questions, 40)
        # Salva as perguntas no cache (arquivo JSON)
        with open(self.cache_file, "w", encoding="utf8") as f:
            json.dump(self.all_questions, f, ensure_ascii=False)

    # Define o método para carregar as perguntas do cache
    def load_questions_from_cache(self):
        """Carrega as perguntas do arquivo de cache."""
        try:
            # Tenta abrir o arquivo de cache
            with open(self.cache_file, "r", encoding="utf8") as f:
                # Carrega as perguntas do arquivo JSON
                self.all_questions = json.load(f)
                # Seleciona aleatoriamente 40 perguntas
                self.questions = random.sample(self.all_questions, 40)
        except FileNotFoundError:
            # Define as listas de perguntas como vazias se o arquivo de cache não for encontrado
            self.all_questions = []
            self.questions = []
