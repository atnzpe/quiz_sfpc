# quiz_logic.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import time
import os
import json
import requests


class QuizLogic:
    """
    Gerencia a lógica do quiz, incluindo carregamento de perguntas,
    verificação de respostas, controle do tempo e cache.
    """

    def __init__(self):
        """Inicializa a lógica do quiz, carregando perguntas e configurando o cache."""

        # Define o escopo de acesso necessário ao Google Sheets
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # Carrega as credenciais da conta de serviço do arquivo 'credentials_sheets.json'
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials_sheets.json", self.scope  # Nome do arquivo corrigido
        )
        self.client = gspread.authorize(self.creds)

        # Abre a planilha do Google Sheets
        self.sheet = self.client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"
        ).sheet1

        # Nome do arquivo de cache JSON
        self.cache_file = "quiz_cache.json"

        # Carrega as perguntas (do cache ou do Google Sheets)
        self.load_questions()

        # Inicializa variáveis de controle
        self.current_question = 0
        self.score = 0
        self.time_limit = 3600
        self.start_time = time.time()
        self.timer_running = False

    def start_timer(self):
        """Inicia o cronômetro do quiz."""
        self.start_time = time.time()
        self.timer_running = True

    def stop_timer(self):
        """Para o cronômetro do quiz."""
        self.timer_running = False

    def get_time_remaining(self):
        """Calcula e retorna o tempo restante no quiz."""
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.time_limit = max(0, 3600 - elapsed_time)
        return self.time_limit

    def load_question(self):
        """
        Carrega a próxima pergunta do quiz, embaralha as opções de resposta
        e retorna a pergunta, opções e índice da resposta correta.

        """

        if self.current_question < len(self.questions):
            question_data = self.questions[self.current_question]
            print(
                f"Resposta correta antes do embaralhamento: {question_data[5]} (índice original: {question_data.index(question_data[5]) - 1})"
            )  # Adicione esta linha

            question_text = f"{self.current_question + 1}. {question_data[0]}"
            options = question_data[1:5]
            random.shuffle(options)  # Embaralha as opções
            correct_answer = options.index(question_data[5].strip()) 

            print(
                f"Resposta correta depois do embaralhamento: {options[correct_answer]} (novo índice: {correct_answer})"
            )  # Adicione esta linha
            return question_text, options, correct_answer
        else:
            return None, None, None

    def check_answer(self, selected_answer):
        """Verifica se a resposta selecionada está correta."""
        if (
            selected_answer
            == self.questions[self.current_question].index(
                self.questions[self.current_question][5]
            )
            - 1
        ):
            self.score += 1
            return "Resposta correta!"
        else:
            return "Resposta incorreta."

    def get_final_results(self):
        """Retorna os resultados finais do quiz, incluindo a pontuação e a mensagem de aprovação/reprovação."""
        return f"Sua pontuação final: {self.score}/40\n{'Aprovado!' if self.score >= 32 else 'Reprovado.'}"

    def load_questions(self):
        """Carrega as perguntas do cache ou do Google Sheets, dependendo da conectividade."""
        if self.check_internet_connection():
            self.download_and_cache_questions()
        else:
            self.load_questions_from_cache()

    def check_internet_connection(self):
        """Verifica se há conexão com a internet."""
        try:
            # Tenta se conectar ao Google
            response = requests.get("http://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def download_and_cache_questions(self):
        """Baixa as perguntas do Google Sheets e as armazena em cache."""
        self.all_questions = self.sheet.get_all_values()[
            1:
        ]  # Lê todas as linhas da planilha (exceto o cabeçalho)
        self.questions = random.sample(
            self.all_questions, 40
        )  # Seleciona 40 perguntas aleatoriamente

        # Salva as perguntas no cache (arquivo JSON)
        with open(self.cache_file, "w", encoding="utf8") as f:
            json.dump(self.all_questions, f, ensure_ascii=False)

    def load_questions_from_cache(self):
        """Carrega as perguntas do arquivo de cache."""
        try:
            with open(self.cache_file, "r", encoding="utf8") as f:
                self.all_questions = json.load(f)
                self.questions = random.sample(self.all_questions, 40)
        except FileNotFoundError:
            # Lida com o caso em que o arquivo de cache não existe
            self.all_questions = []
            self.questions = []
