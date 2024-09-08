import flet as ft
from .models import Pergunta, EstadoQuiz
import random
import pygame
import os
import threading
import time
# Inicializa o mixer do Pygame para reprodução de áudio
pygame.mixer.init()

# Define o botão "Fechar" como uma variável global.
# Inicialmente, o evento on_click é definido como None, pois será configurado posteriormente
btn_result__close = ft.ElevatedButton("Fechar", on_click=None, width=200, height=50)


# Função para reproduzir um áudio aleatório de uma pasta específica
def reproduzir_audio(pasta):
    """Reproduz um áudio aleatório da pasta especificada."""
    # Define o caminho completo para a pasta de áudio
    caminho_pasta = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
        "audio",
        pasta,
    )
    # Cria uma lista com os nomes dos arquivos de áudio na pasta (apenas .mp3 e .wav)
    arquivos_de_audio = [
        f for f in os.listdir(caminho_pasta) if f.endswith(".mp3") or f.endswith(".wav")
    ]
    # Se houver arquivos de áudio na pasta
    if arquivos_de_audio:
        # Escolhe aleatoriamente um arquivo de áudio da lista
        audio_aleatorio = random.choice(arquivos_de_audio)
        # Define o caminho completo para o arquivo de áudio selecionado
        caminho_do_audio = os.path.join(caminho_pasta, audio_aleatorio)
        # Carrega o arquivo de áudio no mixer do Pygame
        pygame.mixer.music.load(caminho_do_audio)
        # Reproduz o áudio carregado
        pygame.mixer.music.play()


# Função para exibir a tela inicial do quiz
def exibir_tela_inicial(page: ft.Page, controller):
    """Exibe a tela inicial do quiz."""

    # Cria um widget Image para exibir o ícone do Scrum
    scrum_icon = ft.Image(
        src="https://ucarecdn.com/6cf435db-3b5e-4833-9f06-bce1388e9610/-/format/auto/-/preview/600x600/-/quality/lighter/CertiProf-Scrum-Foundation.png",
        width=100,
        height=100,
    )

    # Define uma função interna para iniciar o quiz e reproduzir o áudio de início
    def iniciar_quiz_com_som(e):
        # Reproduz o áudio da pasta "inicio"
        reproduzir_audio("inicio")
        # Chama a função iniciar_quiz do controlador para iniciar o quiz
        controller.iniciar_quiz(e)

    # Cria um botão "Iniciar Quiz" que chama a função iniciar_quiz_com_som quando clicado
    button_start = ft.ElevatedButton(
        "Iniciar Quiz", on_click=iniciar_quiz_com_som, width=200, height=50
    )
    # Cria um botão "Fechar" que fecha a janela do aplicativo quando clicado
    close = ft.ElevatedButton(
        "Fechar", on_click=lambda _: page.window.close(), width=200, height=50
    )
    # Cria um botão "Certificação agora!" que abre o link da certificação no navegador
    button_certificacao = ft.ElevatedButton(
        "Certificação agora!",
        on_click=lambda _: page.launch_url(
            "https://certiprof.com/pages/sfpc-scrum-foundation-certification-portuguese?srsltid=AfmBOopH_aNk26kwJWdz54azChJOrEy9F9xy8lUFa3F63pBq6bWBf602"
        ),
        width=200,
        height=50,
    )

    # Adiciona os widgets à página, organizando-os em uma coluna centralizada
    page.add(
        ft.Column(
            [
                scrum_icon,
                button_start,
                close,
                button_certificacao,  # Botão de certificação
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # Define o evento on_click do botão "Fechar" (btn_result__close)
    # para chamar a função voltar_ao_inicio do controlador
    btn_result__close.on_click = controller.voltar_ao_inicio


# Função para exibir uma pergunta do quiz
def exibir_pergunta(
    page: ft.Page, pergunta: Pergunta, estado_quiz: EstadoQuiz, controller
):
    """Exibe a pergunta atual do quiz."""

    page.clean()  # Limpa a página
    # Cria um widget Text para exibir o número da pergunta e o enunciado
    question_text = ft.Text(
        f"{estado_quiz.pergunta_atual + 1}. {pergunta.enunciado}", size=20
    )
    # Cria uma lista vazia para armazenar os botões de resposta
    answer_buttons = []

    # Embaralha as opções de resposta para que a ordem seja aleatória
    random.shuffle(pergunta.opcoes)

    # Itera pelas opções de resposta da pergunta
    for i, opcao in enumerate(pergunta.opcoes):
        # Verifica se a opção é uma string não vazia
        if isinstance(opcao, str) and opcao.strip():
            # Cria um botão para a opção de resposta
            button = ft.ElevatedButton(
                text=f"{opcao}",  # Define o texto do botão como a opção
                on_click=controller.verificar_resposta,  # Define o evento on_click
                data=i,  # Define o atributo data do botão como o índice da opção
            )
            # Adiciona o botão à lista de botões de resposta
            answer_buttons.append(button)

    # Cria um widget Text para exibir o tempo restante do quiz
    score_text = ft.Text(
        f"Tempo restante: {estado_quiz.tempo_restante // 60:02d}:{estado_quiz.tempo_restante % 60:02d}",
        size=16,
    )
    # Define o atributo texto_tempo do controlador como o widget score_text
    controller.texto_tempo = score_text

    # Adiciona os widgets à página, organizando-os em uma coluna centralizada
    page.add(
        ft.Column(
            [
                score_text,  # Widget para exibir o tempo restante
                question_text,  # Widget para exibir a pergunta
                *answer_buttons,  # Desempacota os botões de resposta
                ft.ElevatedButton(
                    "Voltar ao Início",
                    on_click=controller.voltar_ao_inicio,  # Botão para voltar ao início
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # Alinhamento vertical
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Alinhamento horizontal
        )
    )

    # Define uma função interna para atualizar o tempo restante do quiz
    def atualizar_tempo():
        """Atualiza o tempo restante a cada segundo."""
        # Verifica se o tempo restante é maior que zero e se o quiz foi iniciado
        if estado_quiz.tempo_restante > 0 and estado_quiz.quiz_iniciado:
            # Decrementa o tempo restante
            estado_quiz.tempo_restante -= 1
            # Calcula as horas, minutos e segundos restantes
            horas, resto = divmod(estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            # Atualiza o texto do widget score_text com o tempo restante formatado
            score_text.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            # Atualiza a página
            page.update()
            # Agenda a próxima chamada da função atualizar_tempo em 1 segundo
            page.on_idle = lambda _: threading.Timer(1, atualizar_tempo).start()
        else:
            # Se o tempo acabar
            reproduzir_audio("acabar")  # Reproduz o áudio de fim de tempo
            controller.finalizar_quiz(None)  # Finaliza o quiz

    # Inicia a atualização do tempo
    atualizar_tempo()


# Função para exibir os resultados do quiz
def exibir_resultados(page: ft.Page, estado_quiz, controller):
    """
    Exibe os resultados do quiz usando AlertDialog.
    """

    # Calcula as estatísticas do quiz
    total_perguntas = len(controller.quiz_logic.questions)
    total_acertos = estado_quiz.pontuacao
    total_erros = total_perguntas - total_acertos

    # Verifica se o modal já está aberto
    if not controller.modal_aberto:

        def close_dlg(e):
            """Fecha o diálogo modal."""
            dlg_modal.open = False
            controller.modal_aberto = False  # Define modal_aberto como False
            page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Fim do Quiz!"),
            content=ft.Column(
                [
                    ft.Text(
                        f"Sua pontuação final: {estado_quiz.pontuacao}/{total_perguntas}"
                    ),
                    ft.Text(f"Acertos: {total_acertos}"),
                    ft.Text(f"Erros: {total_erros}"),
                    ft.Text(
                        f"{'Aprovado!' if estado_quiz.pontuacao >= 32 else 'Reprovado.'}"
                    ),
                ]
            ),
            actions=[
                ft.ElevatedButton(
                    "Fechar", on_click=controller.fechar_modal
                ),  # Chamando a função
            ],
            on_dismiss=close_dlg,
        )

        if estado_quiz.pontuacao < 32:
            dlg_modal.actions.append(
                ft.ElevatedButton(
                    "Baixar Guia Scrum",
                    on_click=lambda _: page.launch_url("https://www.scrumguides.org/"),
                )
            )

        page.overlay.append(dlg_modal)
        dlg_modal.open = True
        controller.modal_aberto = True  # Define modal_aberto como True
        page.update()

    if estado_quiz.pontuacao >= 70:
        reproduzir_audio("ganhou")
    else:
        reproduzir_audio("perdeu")

def piscar_verde(botao):
    """Faz o botão piscar na cor verde."""
    botao.bgcolor = ft.colors.GREEN
    botao.update()
    time.sleep(0.2)  # Ajuste o tempo de piscada aqui
    botao.bgcolor = None
    botao.update()

def piscar_vermelho(botao):
    """Faz o botão piscar na cor vermelha."""
    botao.bgcolor = ft.colors.RED
    botao.update()
    time.sleep(0.2)  # Ajuste o tempo de piscada aqui
    botao.bgcolor = None
    botao.update()