"""
Arquivo principal do aplicativo de quiz. 
Gerencia a inicialização do aplicativo Flet, a lógica do quiz, 
a interface do usuário e o monitoramento do Google Docs.
"""

import flet as ft  # Importa a biblioteca Flet para a interface do usuário
from quiz_logic import QuizLogic  # Importa a classe que gerencia a lógica do quiz
from ui import QuizUI  # Importa a classe responsável pela interface do usuário
from automate_spreadsheet import (
    monitor_google_docs,
)  # Importa a função de monitoramento
import threading  # Importa a biblioteca para trabalhar com threads


def main(page: ft.Page):
    """
    Função principal que inicializa e executa o aplicativo Flet,
    incluindo o monitoramento do Google Docs em segundo plano.

    Args:
        page (ft.Page): A página principal do aplicativo Flet.
    """

    # Configura a página do aplicativo Flet
    page.title = "Quiz - Teste seus conhecimentos!"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Inicializa a lógica do quiz e a interface do usuário
    quiz_logic = QuizLogic()
    QuizUI(page, quiz_logic)

    # Define os argumentos para a função de monitoramento
    document_id = "1kQU6ElV41Y73Iiu6N1lOcfAoHaaWSNTqmOnOWBhifgg"  # ID do Google Docs
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"  # URL da planilha

    # Cria e inicia a thread de monitoramento do Google Docs
    monitor_thread = threading.Thread(
        target=monitor_google_docs, args=(document_id, spreadsheet_url)
    )
    monitor_thread.daemon = (
        True  # Define como daemon para encerrar com o programa principal
    )
    monitor_thread.start()


# Inicia o aplicativo Flet
ft.app(target=main, view=ft.WEB_BROWSER)
