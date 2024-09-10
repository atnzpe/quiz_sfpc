import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import time
import os
import json
import requests


class QuizLogic:
    """
    Classe responsável por gerenciar a lógica do quiz.
    """

    def __init__(self):
        """
        Inicializa a lógica do quiz, carregando as perguntas
        e inicializando variáveis de controle.
        """
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials_sheets.json", self.scope
        )
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"
        ).sheet1
        self.cache_file = "quiz_cache.json"
        self.questions = []  # Inicializa como lista vazia
        self.current_question = 0
        self.score = 0
        self.time_limit = 3600
        self.start_time = time.time()
        self.timer_running = False
        self.load_questions()  # Carrega as perguntas ao iniciar

    def start_timer(self):
        """Inicia o cronômetro do quiz."""
        self.start_time = time.time()
        self.timer_running = True

    def stop_timer(self):
        """Para o cronômetro do quiz."""
        self.timer_running = False

    def get_time_remaining(self):
        """
        Calcula e retorna o tempo restante no quiz.

        Returns:
            int: O tempo restante em segundos.
        """
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.time_limit = max(0, 3600 - elapsed_time)
        return self.time_limit

    def load_question(self):
        """
        Carrega a próxima pergunta do quiz, embaralhando
        as alternativas a cada chamada.
        """
        if self.current_question < len(self.questions):
            question_data = self.questions[self.current_question]
            question_text = f"{self.current_question + 1}. {question_data[0]}"

            # 1. Copia as opções e embaralha
            options = question_data[1:5].copy()
            random.shuffle(options)

            # 2. Calcula o índice da resposta correta na lista ORIGINAL
            correct_answer_index = ord(question_data[5].lower()) - ord("a")

            # 3. Encontra a resposta correta na lista embaralhada
            correct_answer = question_data[1:5][correct_answer_index]

            # 4. Encontra o índice da resposta correta na lista EMBARALHADA
            correct_answer_index = options.index(correct_answer)

            self.current_question += 1
            return question_text, options, correct_answer_index
        else:
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

        #  --- Correção: Usando correct_answer_index ---
        if selected_answer == self.quiz_logic.correct_answer_index:
            # Incrementa a pontuação se a resposta estiver correta
            self.score += 1
            return "Resposta correta!"
        else:
            return "Resposta incorreta."

    def get_final_results(self):
        """Retorna os resultados finais do quiz."""
        return (
            f"Sua pontuação final: {self.score}/40\n"
            f"{'Aprovado!' if self.score >= 32 else 'Reprovado.'}"
        )

    def load_questions(self):
        """Carrega as perguntas do cache ou do Google Sheets."""
        if self.check_internet_connection():
            self.download_and_cache_questions()
        else:
            self.load_questions_from_cache()

    def check_internet_connection(self):
        """Verifica a conexão com a internet."""
        try:
            requests.get("http://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def download_and_cache_questions(self):
        """Baixa e armazena em cache as perguntas do Google Sheets."""
        try:
            all_questions = self.sheet.get_all_values()[1:]
            random.shuffle(all_questions)
            with open(self.cache_file, "w", encoding="utf8") as f:
                json.dump(all_questions, f, ensure_ascii=False)
            self.questions = random.sample(all_questions, 40)
        except Exception as e:
            print(f"Erro ao baixar perguntas: {e}")
            self.load_questions_from_cache()  # Tenta carregar do cache em caso de erro

    def load_questions_from_cache(self):
        """Carrega as perguntas do arquivo de cache."""
        try:
            with open(self.cache_file, "r", encoding="utf8") as f:
                self.questions = json.load(f)
                random.shuffle(self.questions)  # Embaralha as perguntas aqui
                self.questions = random.sample(self.questions, 40)
        except FileNotFoundError:
            print("Arquivo de cache não encontrado. Carregando do Google Sheets...")
            self.download_and_cache_questions()  # Tenta baixar do Google Sheets
