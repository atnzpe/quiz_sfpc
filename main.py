import flet as ft
from app.controllers import QuizController


def main(page: ft.Page):
    """
    Função principal que inicializa o aplicativo Flet.
    """

    #page.title = "Quiz - Teste seus conhecimentos!"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Variável para controlar o tema (padrão: claro)
    tema_escuro = False

    def mudar_tema(e):
        """Alterna entre os temas claro e escuro."""
        nonlocal tema_escuro
        tema_escuro = not tema_escuro
        page.theme_mode = ft.ThemeMode.DARK if tema_escuro else ft.ThemeMode.LIGHT
        switch_tema.label = "Tema Escuro" if tema_escuro else "Tema Claro"
        page.update()

    # Cria o Switch para alternar o tema
    switch_tema = ft.Switch(
        label="Tema Escuro",
        value=False,  # Valor inicial: tema claro
        on_change=mudar_tema,
    )

    # Inicializa o Controller
    quiz_controller = QuizController(page, switch_tema)  # Passa o switch de tema

    # Adiciona o switch de tema ao AppBar da página
    page.appbar = ft.AppBar(actions=[switch_tema])

    # Exibe a tela inicial
    quiz_controller.exibir_tela_inicial()


ft.app(target=main)
