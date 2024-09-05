import flet as ft
from app.controllers import QuizController

def main(page: ft.Page):
    """
    Função principal que inicializa e executa o aplicativo Flet, 
    permitindo ao usuário escolher o tema (claro ou escuro) na tela inicial.
    """

    page.title = "Quiz Scrum Foundation Professional Certification (SFPC™) - Teste seus conhecimentos!"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Variável para controlar o tema (padrão: claro)
    tema_escuro = False  

    def mudar_tema(e):
        """
        Função para alternar entre os temas claro e escuro.
        """
        nonlocal tema_escuro
        tema_escuro = not tema_escuro
        page.theme_mode = ft.ThemeMode.DARK if tema_escuro else ft.ThemeMode.LIGHT
        page.update()

    # Cria o botão para alternar o tema
    botao_tema = ft.ElevatedButton(
        "Tema Escuro" if tema_escuro else "Tema Claro", 
        on_click=mudar_tema
    )

    # Inicializa o Controller
    quiz_controller = QuizController(page)

    # Adiciona o botão de tema à tela inicial
    quiz_controller.exibir_tela_inicial(botao_tema) 

ft.app(target=main)

