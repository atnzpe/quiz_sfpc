import threading

import flet as ft
from flet import icons

import automate_spreadsheet
from app.controllers import QuizController
from app.models import EstadoQuiz  
from quiz_logic import QuizLogic 
from app.views import exibir_pergunta, exibir_resultados, exibir_tela_inicial 

def main(page: ft.Page):
    """
    Função principal que inicializa o aplicativo Flet do Quiz SFPC.
    
    Args:
        page (ft.Page): Objeto página do Flet.
    """

    page.title = "Quiz - Scrum Foundation Professional Certification - SFPC™ (v2020)"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Inicia a atualização das perguntas em uma thread separada
    thread_atualizacao = threading.Thread(
        target=automate_spreadsheet.monitor_google_docs,  
        args=(
            automate_spreadsheet.DOCUMENT_ID,
            automate_spreadsheet.SPREADSHEET_URL,
        ),
    )
    thread_atualizacao.daemon = True
    thread_atualizacao.start()

    # Variável para controlar o tema (padrão: claro)
    tema_escuro_ativado = False 

    # Variável para controlar o som (padrão: ativado)
    som_ativado = True

    def mudar_tema(e):
        """
        Alterna entre os temas claro e escuro da aplicação.
        
        Args:
            e: Objeto evento do Flet.
        """
        nonlocal tema_escuro_ativado
        tema_escuro_ativado = not tema_escuro_ativado
        page.theme_mode = ft.ThemeMode.DARK if tema_escuro_ativado else ft.ThemeMode.LIGHT
        switch_tema.label = "Tema Escuro" if tema_escuro_ativado else "Tema Claro"
        page.update()

    def alternar_som(e):
        """
        Ativa/desativa os efeitos sonoros do quiz.
        
        Args:
            e: Objeto evento do Flet.
        """
        nonlocal som_ativado
        som_ativado = not som_ativado
        botao_som.icon = icons.VOLUME_UP if som_ativado else icons.VOLUME_OFF
        quiz_controller.som_ativado = som_ativado  # Atualiza o controlador
        page.update()

    # Cria o Switch para alternar o tema
    switch_tema = ft.Switch(
        label="Tema Escuro",
        value=False, # Valor inicial: tema claro
        on_change=mudar_tema
    )

    # Cria o botão para ativar/desativar o som
    botao_som = ft.IconButton(
        icon=icons.VOLUME_UP,
        on_click=alternar_som
    )

    # Inicializa o Controller, passando o switch de tema e som_ativado
    quiz_controller = QuizController(page, switch_tema, som_ativado)  

    # Adiciona o switch de tema e o botão de som ao AppBar da página
    page.appbar = ft.AppBar(
        title=ft.Text("Quiz - SFPC™"),
        actions=[
            ft.Row([switch_tema, botao_som], alignment=ft.MainAxisAlignment.END) 
        ]
    )

    # Exibe a tela inicial
    quiz_controller.exibir_tela_inicial()

ft.app(target=main)
