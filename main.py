import threading  # Para executar a atualização das perguntas em segundo plano

import flet as ft  # Importa a biblioteca Flet para a interface gráfica
from flet import icons  # Ícones da biblioteca Flet

import automate_spreadsheet  # Importa o módulo responsável pela automação com Google Docs/Sheets
from app.controllers import QuizController  # Importa o controlador do quiz
from app.models import EstadoQuiz  # Importa o modelo de estado do quiz (não utilizado no código, verificar necessidade)
from quiz_logic import QuizLogic  # Importa a lógica do quiz (não utilizado no código, verificar necessidade)
from app.views import (  # Importa as funções para exibir diferentes telas do aplicativo
    exibir_pergunta,
    exibir_resultados,
    exibir_tela_inicial,
)

# Define a função principal que será executada pelo Flet
def main(page: ft.Page):
    """
    Função principal que inicializa o aplicativo Flet do Quiz SFPC.

    Args:
        page (ft.Page): Objeto página do Flet.
    """
    # Configura o título da página
    page.title = "Quiz - Scrum Foundation Professional Certification - SFPC™ (v2020)"
    # Define o alinhamento vertical do conteúdo da página para o centro
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    # Define o alinhamento horizontal do conteúdo da página para o centro
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Cria e inicia uma thread para atualizar as perguntas em segundo plano
    # Isso evita que a interface do aplicativo trave durante a atualização
    thread_atualizacao = threading.Thread(
        target=automate_spreadsheet.monitor_google_docs,  # Função que será executada na thread
        args=(
            automate_spreadsheet.DOCUMENT_ID,  # ID do documento do Google Docs
            automate_spreadsheet.SPREADSHEET_URL,  # URL da planilha do Google Sheets
        ),
    )
    thread_atualizacao.daemon = True  # Define a thread como daemon (encerra quando o programa principal termina)
    thread_atualizacao.start()  # Inicia a thread

    # Variável para controlar o tema escuro (False = tema claro, True = tema escuro)
    tema_escuro_ativado = False

    # Variável para controlar o som (True = som ativado, False = som desativado)
    som_ativado = True

    # Define a função que será chamada quando o switch de tema for alterado
    def mudar_tema(e):
        """
        Alterna entre os temas claro e escuro da aplicação.

        Args:
            e: Objeto evento do Flet.
        """
        nonlocal tema_escuro_ativado  # Acessa a variável externa tema_escuro_ativado
        # Inverte o estado da variável tema_escuro_ativado
        tema_escuro_ativado = not tema_escuro_ativado
        # Define o tema da página com base no estado da variável tema_escuro_ativado
        page.theme_mode = (
            ft.ThemeMode.DARK if tema_escuro_ativado else ft.ThemeMode.LIGHT
        )
        # Atualiza o label do switch de tema
        switch_tema.label = (
            "Tema Escuro" if tema_escuro_ativado else "Tema Claro"
        )
        # Atualiza a página para refletir as alterações
        page.update()

    # Define a função que será chamada quando o botão de som for clicado
    def alternar_som(e):
        """
        Ativa/desativa os efeitos sonoros do quiz.

        Args:
            e: Objeto evento do Flet.
        """
        nonlocal som_ativado  # Acessa a variável externa som_ativado
        som_ativado = not som_ativado  # Inverte o estado da variável som_ativado
        # Altera o ícone do botão de som com base no estado da variável som_ativado
        botao_som.icon = icons.VOLUME_UP if som_ativado else icons.VOLUME_OFF
        quiz_controller.som_ativado = (
            som_ativado  # Atualiza o controlador do quiz
        )
        page.update()  # Atualiza a página para refletir as alterações

    # Cria um switch para alternar o tema da aplicação
    switch_tema = ft.Switch(
        label="Tema Escuro",  # Define o texto do switch
        value=False,  # Define o valor inicial do switch (False = tema claro)
        on_change=mudar_tema,  # Define a função que será chamada ao alterar o switch
    )

    # Cria um botão para ativar/desativar o som
    botao_som = ft.IconButton(
        icon=icons.VOLUME_UP,  # Define o ícone inicial do botão
        on_click=alternar_som,  # Define a função que será chamada ao clicar no botão
    )

    # Cria uma instância do controlador do quiz
    quiz_controller = QuizController(
        page, switch_tema, som_ativado
    )  # Passa a página, o switch de tema e o estado do som para o controlador

    # Define a barra de aplicativo (AppBar) da página
    page.appbar = ft.AppBar(
        title=ft.Text(
            "Quiz - SFPC™"
        ),  # Define o título da barra de aplicativo
        actions=[
            ft.Row(
                [switch_tema, botao_som],  # Adiciona o switch de tema e o botão de som à barra de aplicativo
                alignment=ft.MainAxisAlignment.END,  # Alinha os elementos à direita
            )
        ],
    )

    # Exibe a tela inicial do quiz
    quiz_controller.exibir_tela_inicial()

# Inicializa o aplicativo Flet, definindo a função main() como ponto de entrada
ft.app(target=main)
