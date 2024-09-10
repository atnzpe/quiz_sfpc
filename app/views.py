import flet as ft  # Importa a biblioteca Flet para a interface gráfica
from .models import (
    Pergunta,
    EstadoQuiz,
)  # Importa as classes Pergunta e EstadoQuiz (provavelmente de um arquivo models.py)
import random  # Importa a biblioteca random para escolher áudios aleatórios

# import pygame  # Importa a biblioteca Pygame para reprodução de áudio
import os  # Importa a biblioteca os para interagir com o sistema de arquivos
import threading  # Importa a biblioteca threading para usar threads
import time  # Importa a biblioteca time para usar funções relacionadas a tempo

# Inicializa o mixer do Pygame
# pygame.mixer.init()

# Define o botão "Fechar" como uma variável global (será melhorado posteriormente)
# Idealmente, evite variáveis globais. Melhor encapsular em uma classe para melhor organização.
btn_result__close = ft.ElevatedButton("Fechar", on_click=None, width=200, height=50)


# Define a função para reproduzir áudio
def reproduzir_audio(pasta: str):
    """
    Reproduz um áudio aleatório da pasta especificada.

    Args:
        pasta (str): O nome da pasta dentro do diretório "audio"
            onde os arquivos de áudio estão localizados.
    """
    # Constrói o caminho absoluto para a pasta de áudio
    caminho_pasta = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
        "audio",
        pasta,
    )
    # Obtém a lista de arquivos de áudio na pasta
    arquivos_de_audio = [
        f for f in os.listdir(caminho_pasta) if f.endswith((".mp3", ".wav"))
    ]
    # Se houver arquivos de áudio na pasta
    if arquivos_de_audio:
        # Escolhe um arquivo de áudio aleatório
        audio_aleatorio = random.choice(arquivos_de_audio)
        # Constrói o caminho completo para o arquivo de áudio
        caminho_do_audio = os.path.join(caminho_pasta, audio_aleatorio)
        # Carrega o arquivo de áudio


#       pygame.mixer.music.load(caminho_do_audio)
# Reproduz o áudio
#      pygame.mixer.music.play()


# Define a função para exibir a tela inicial
def exibir_tela_inicial(page: ft.Page, controller):
    """
    Exibe a tela inicial do quiz com um ícone, botão de início
    e botão de fechar.

    Args:
        page (ft.Page): A página do Flet para exibir os elementos.
        controller: O objeto controlador do quiz.
    """
    # Cria o ícone do Scrum
    scrum_icon = ft.Image(
        src="https://ucarecdn.com/6cf435db-3b5e-4833-9f06-bce1388e9610/-/format/auto/-/preview/600x600/-/quality/lighter/CertiProf-Scrum-Foundation.png",  # Define a URL da imagem
        width=100,  # Define a largura da imagem
        height=100,  # Define a altura da imagem
    )

    # Define a função que será chamada quando o botão "Iniciar Quiz" for clicado
    def iniciar_quiz_com_som(e):
        """
        Inicia o quiz e reproduz o áudio de início.

        Args:
            e: Objeto evento do Flet.
        """
        reproduzir_audio("inicio")  # Reproduz o áudio de início
        controller.iniciar_quiz(e)  # Chama a função do controlador para iniciar o quiz

    # Cria o botão "Iniciar Quiz"
    button_start = ft.ElevatedButton(
        "Iniciar Quiz",  # Define o texto do botão
        on_click=iniciar_quiz_com_som,  # Define a função que será chamada ao clicar
        width=200,  # Define a largura do botão
        height=50,  # Define a altura do botão
    )
    # Cria o botão "Fechar"
    close = ft.ElevatedButton(
        "Fechar",
        on_click=lambda _: page.window.close(),  # Fecha a janela ao clicar
        width=200,
        height=50,
    )
    # Cria o botão "Certificação agora!"
    button_certificacao = ft.ElevatedButton(
        "Certificação agora!",
        on_click=lambda _: page.launch_url(
            "https://certiprof.com/pages/sfpc-scrum-foundation-certification-portuguese?srsltid=AfmBOopH_aNk26kwJWdz54azChJOrEy9F9xy8lUFa3F63pBq6bWBf602"
        ),  # Abre a URL no navegador ao clicar
        width=200,
        height=50,
    )

    # Adiciona os elementos à página
    page.add(
        ft.Column(
            [
                scrum_icon,  # Ícone do Scrum
                button_start,  # Botão "Iniciar Quiz"
                close,  # Botão "Fechar"
                button_certificacao,  # Botão "Certificação agora!"
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # Alinha os elementos ao centro verticalmente
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Alinha os elementos ao centro horizontalmente
        )
    )

    # Utiliza o controlador para gerenciar o botão "Fechar"
    btn_result__close.on_click = (
        controller.voltar_ao_inicio
    )  # Define a função que será chamada ao clicar no botão "Fechar"


# Define a função para exibir uma pergunta do quiz
def exibir_pergunta(
    page: ft.Page, pergunta: Pergunta, estado_quiz: EstadoQuiz, controller
):
    """
    Exibe uma pergunta do quiz com suas opções de resposta.

    Args:
        page (ft.Page): A página do Flet para exibir a pergunta.
        pergunta (Pergunta): A pergunta a ser exibida.
        estado_quiz (EstadoQuiz): O estado atual do quiz.
        controller: O objeto controlador do quiz.
    """

    # Limpa a página
    page.clean()
    # Cria o texto da pergunta
    question_text = ft.Text(
        f"{estado_quiz.pergunta_atual + 1}. {pergunta.enunciado}",  # Define o texto da pergunta com base no estado atual do quiz
        size=20,  # Define o tamanho da fonte
    )
    # Cria uma lista para armazenar os botões de resposta
    answer_buttons = []

    # Itera pelas opções de resposta da pergunta
    for i, opcao in enumerate(pergunta.opcoes):
        # Verifica se a opção é uma string e se não está vazia
        if isinstance(opcao, str) and opcao.strip():
            # Cria um botão para a opção de resposta
            button = ft.ElevatedButton(
                text=f"{chr(ord('a') + i)}) {opcao}",  # Define o texto do botão com a letra correspondente à opção
                on_click=controller.verificar_resposta,  # Define a função que será chamada ao clicar no botão
                data=i,  # Armazena o índice da opção como dado no botão
            )
            # Adiciona o botão à lista de botões de resposta
            answer_buttons.append(button)

    # Cria o texto para exibir o tempo restante
    score_text = ft.Text(
        f"Tempo restante: {estado_quiz.tempo_restante // 60:02d}:{estado_quiz.tempo_restante % 60:02d}",  # Define o texto do tempo restante
        size=16,  # Define o tamanho da fonte
    )
    # Armazena o texto do tempo restante no controlador
    controller.texto_tempo = score_text

    # Adiciona os elementos à página
    page.add(
        ft.Column(
            [
                score_text,  # Texto do tempo restante
                question_text,  # Texto da pergunta
                *answer_buttons,  # Botões de resposta (desempacota a lista)
                ft.ElevatedButton(
                    "Voltar ao Início",  # Botão "Voltar ao Início"
                    on_click=controller.voltar_ao_inicio,  # Define a função que será chamada ao clicar
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # Alinha os elementos ao centro verticalmente
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Alinha os elementos ao centro horizontalmente
        )
    )

    # Define a função que será executada em segundo plano para atualizar o tempo restante
    def atualizar_tempo():
        """Atualiza o tempo restante do quiz a cada segundo."""
        # Verifica se o tempo restante é maior que 0 e se o quiz foi iniciado
        if estado_quiz.tempo_restante > 0 and estado_quiz.quiz_iniciado:
            # Decrementa o tempo restante em 1 segundo
            estado_quiz.tempo_restante -= 1
            # Calcula as horas, minutos e segundos restantes
            horas, resto = divmod(estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            # Atualiza o texto do tempo restante
            score_text.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            # Atualiza a página
            page.update()
            # Agenda a próxima chamada da função atualizar_tempo() após 1 segundo
            page.on_idle = lambda _: threading.Timer(1, atualizar_tempo).start()
        else:
            # Se o tempo acabar, reproduz o áudio de "acabar"
            reproduzir_audio("acabar")
            # Chama a função do controlador para finalizar o quiz
            controller.finalizar_quiz(None)

    # Inicia a atualização do tempo
    atualizar_tempo()


# Define a função para exibir os resultados do quiz
def exibir_resultados(page: ft.Page, estado_quiz: EstadoQuiz, controller):
    """
    Exibe os resultados do quiz em um AlertDialog.

    Args:
        page (ft.Page): A página do Flet para exibir os resultados.
        estado_quiz (EstadoQuiz): O estado final do quiz.
        controller: O objeto controlador do quiz.
    """
    # Obtém o número total de perguntas
    total_perguntas = len(controller.quiz_logic.questions)
    # Obtém o número de acertos
    total_acertos = estado_quiz.pontuacao
    # Calcula o número de erros
    total_erros = total_perguntas - total_acertos

    # Verifica se o modal já está aberto
    if not controller.modal_aberto:
        # Define a função que será chamada quando o botão "Fechar" do modal for clicado
        def close_dlg(e):
            """Fecha o diálogo modal."""
            dlg_modal.open = False  # Fecha o modal
            controller.modal_aberto = False  # Define a flag de modal aberto como False
            page.update()  # Atualiza a página

        # Cria o AlertDialog para exibir os resultados
        dlg_modal = ft.AlertDialog(
            modal=True,  # Define o diálogo como modal
            title=ft.Text("Fim do Quiz!"),  # Define o título do modal
            content=ft.Column(
                [
                    ft.Text(
                        f"Sua pontuação final: {estado_quiz.pontuacao}/{total_perguntas}"
                    ),  # Exibe a pontuação final
                    ft.Text(f"Acertos: {total_acertos}"),  # Exibe o número de acertos
                    ft.Text(f"Erros: {total_erros}"),  # Exibe o número de erros
                    ft.Text(
                        f"{'Aprovado!' if estado_quiz.pontuacao >= 32 else 'Reprovado.'}"
                    ),  # Exibe se o usuário foi aprovado ou reprovado
                ]
            ),
            actions=[
                ft.ElevatedButton(
                    "Fechar", on_click=controller.fechar_modal
                ),  # Botão "Fechar"
            ],
            on_dismiss=close_dlg,  # Define a função que será chamada ao fechar o modal
        )

        # Se a pontuação for menor que 32 (reprovado), adiciona um botão para baixar o Guia Scrum
        if estado_quiz.pontuacao < 32:
            dlg_modal.actions.append(
                ft.ElevatedButton(
                    "Baixar Guia Scrum",
                    on_click=lambda _: page.launch_url(
                        "https://www.scrumguides.org/"
                    ),  # Abre a URL no navegador ao clicar
                )
            )

        # Adiciona o modal à página
        page.overlay.append(dlg_modal)
        dlg_modal.open = True  # Abre o modal
        controller.modal_aberto = True  # Define a flag de modal aberto como True
        page.update()  # Atualiza a página

    # Reproduz o áudio de acordo com a pontuação


# if estado_quiz.pontuacao >= 70:
#    reproduzir_audio("ganhou")
# else:
#    reproduzir_audio("perdeu")


# Define a função para fazer o botão piscar em verde
# def piscar_verde(botao: ft.Control):
#   """
#  Faz o botão piscar na cor verde.
#
#   Args:
#      botao (ft.Control): O botão que irá piscar.
# """
# botao.bgcolor = ft.colors.GREEN  # Define a cor de fundo do botão para verde
# botao.update()  # Atualiza o botão
# time.sleep(0.2)  # Aguarda 0.2 segundos
# botao.bgcolor = None  # Remove a cor de fundo do botão
# botao.update()  # Atualiza o botão


# Define a função para fazer o botão piscar em vermelho
# def piscar_vermelho(botao: ft.Control):
#    """
#    Faz o botão piscar na cor vermelha.

#    Args:
#       botao (ft.Control): O botão que irá piscar.
#  """
# botao.bgcolor = ft.colors.RED  # Define a cor de fundo do botão para vermelho
# botao.update()  # Atualiza o botão
# time.sleep(0.2)  # Aguarda 0.2 segundos
# botao.bgcolor = None  # Remove a cor de fundo do botão
# botao.update()  # Atualiza o botão
