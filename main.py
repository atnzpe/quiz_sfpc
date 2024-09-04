"""
Arquivo principal do aplicativo de quiz. 
Gerencia a inicialização do aplicativo Flet e conecta a lógica do quiz à interface do usuário.
"""

import flet as ft  # Importa a biblioteca Flet para a interface do usuário
from quiz_logic import QuizLogic  # Importa a classe que gerencia a lógica do quiz
from ui import QuizUI  # Importa a classe responsável pela interface do usuário


def main(page: ft.Page):
    """
    Função principal que inicializa e executa o aplicativo Flet.

    Args:
        page (ft.Page): A página principal do aplicativo Flet.
    """

    page.title = (
        "Quiz - Teste seus conhecimentos!"  # Define o título da janela do aplicativo
    )
    page.vertical_alignment = (
        ft.MainAxisAlignment.CENTER
    )  # Centraliza o conteúdo verticalmente
    page.horizontal_alignment = (
        ft.CrossAxisAlignment.CENTER
    )  # Centraliza o conteúdo horizontalmente

    quiz_logic = QuizLogic()  # Cria uma instância da lógica do quiz
    QuizUI(
        page, quiz_logic
    )  # Inicializa a interface do usuário, passando a página e a lógica do quiz


# Inicia o aplicativo Flet, definindo 'main' como a função principal e usando a visualização de navegador da web
ft.app(target=main, view=ft.WEB_BROWSER)
