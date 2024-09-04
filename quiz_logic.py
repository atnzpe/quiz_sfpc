import gspread  # Para interagir com o Google Sheets
from oauth2client.service_account import (
    ServiceAccountCredentials,
)  # Autenticação com o Google
import random  # Para embaralhar as opções de resposta
import time  # Para controlar o tempo
import os
import json


class QuizLogic:
    """
    Gerencia a lógica do quiz, incluindo carregamento de perguntas, verificação de respostas
    e controle do tempo.
    """

    def __init__(self):
        """Inicializa a lógica do quiz carregando as perguntas do Google Sheets."""

        # Define o escopo de acesso necessário ao Google Sheets
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # Carrega as credenciais da conta de serviço do arquivo 'credentials.json'
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", self.scope
        )

        # Autoriza o acesso ao Google Sheets
        self.client = gspread.authorize(self.creds)

        # Abre a planilha específica usando o URL
        self.sheet = self.client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"
        ).sheet1

        # Carrega todas as perguntas (excluindo o cabeçalho)
        self.all_questions = self.sheet.get_all_values()[1:]

        # Seleciona 30 perguntas aleatórias
        self.questions = random.sample(self.all_questions, 30)

        # Inicializa variáveis de controle
        self.current_question = 0  # Índice da pergunta atual
        self.score = 0  # Pontuação do jogador
        self.time_limit = 3600  # Tempo limite em segundos (1 hora)
        self.start_time = time.time()  # Tempo de início do quiz
        self.timer_running = False  # Indica se o cronômetro está em execução

        # Nome do arquivo de cache JSON
        self.cache_file = "quiz_cache.json"
        self.load_questions()

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
        # ... (código para carregar do Google Sheets)

        # Salva as perguntas no cache (arquivo JSON)
        with open(self.cache_file, "w", encoding="utf8") as f:
            json.dump(self.all_questions, f, ensure_ascii=False)

    def load_questions_from_cache(self):
        """Carrega as perguntas do arquivo de cache."""
        try:
            with open(self.cache_file, "r", encoding="utf8") as f:
                self.all_questions = json.load(f)
                self.questions = random.sample(self.all_questions, 30)
        except FileNotFoundError:
            # Lida com o caso em que o arquivo de cache não existe
            self.all_questions = []
            self.questions = []

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
        return f"Sua pontuação final: {self.score}\n{'Aprovado!' if self.score >= 70 else 'Reprovado.'}"
