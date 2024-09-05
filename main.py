import flet as ft
from app.controllers import QuizController


def main(page: ft.Page):
    """
    Função principal que inicializa e executa o aplicativo Flet,
    incluindo o monitoramento do Google Docs em segundo plano.
    """

    page.title = "Quiz - Teste seus conhecimentos!"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Variável para controlar o tema (padrão: claro)
    tema_escuro = False

    def mudar_tema(e):
        """Alterna entre os temas claro e escuro."""
        nonlocal tema_escuro
        tema_escuro = not tema_escuro
        page.theme_mode = ft.ThemeMode.DARK if tema_escuro else ft.ThemeMode.LIGHT
        botao_tema.text = "Tema Claro" if tema_escuro else "Tema Escuro"
        page.update()

    # Cria o botão para alternar o tema
    botao_tema = ft.ElevatedButton("Tema Escuro", on_click=mudar_tema)

    # Inicializa o Controller
    quiz_controller = QuizController(page, botao_tema)  # Passa o botão de tema


ft.app(target=main)
