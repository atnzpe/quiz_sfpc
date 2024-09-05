# main.py
import flet as ft  # Importa a biblioteca Flet para construir a interface
from app.controllers import QuizController  # Importa a classe do controlador

def main(page: ft.Page):
    """
    Função principal que inicializa e executa o aplicativo Flet.

    Args:
        page (ft.Page): A página principal do aplicativo Flet.
    """
    page.title = "Quiz - Teste seus conhecimentos!"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER  # Alinhamento vertical
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER  # Alinhamento horizontal

    # Inicializa o Controller, passando a instância da página Flet
    quiz_controller = QuizController(page)

# Inicia o aplicativo Flet
ft.app(target=main)
