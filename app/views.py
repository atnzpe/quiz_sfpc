import flet as ft
from .models import Pergunta, EstadoQuiz
import random
import pygame
import os
import threading
import time

# Inicializa o mixer do Pygame para reprodução de áudio
pygame.mixer.init()

# Define o botão "Fechar" como uma variável global (será melhorado posteriormente)
btn_result__close = ft.ElevatedButton(
    "Fechar", on_click=None, width=200, height=50
)

def reproduzir_audio(pasta: str):
    """
    Reproduz um áudio aleatório da pasta especificada.

    Args:
        pasta (str): O nome da pasta dentro do diretório "audio" 
            onde os arquivos de áudio estão localizados.
    """
    caminho_pasta = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
        "audio",
        pasta,
    )
    arquivos_de_audio = [
        f for f in os.listdir(caminho_pasta) if f.endswith((".mp3", ".wav"))
    ]
    if arquivos_de_audio:
        audio_aleatorio = random.choice(arquivos_de_audio)
        caminho_do_audio = os.path.join(caminho_pasta, audio_aleatorio)
        pygame.mixer.music.load(caminho_do_audio)
        pygame.mixer.music.play()


def exibir_tela_inicial(page: ft.Page, controller):
    """
    Exibe a tela inicial do quiz com um ícone, botão de início 
    e botão de fechar.

    Args:
        page (ft.Page): A página do Flet para exibir os elementos.
        controller: O objeto controlador do quiz.
    """
    scrum_icon = ft.Image(
        src="https://ucarecdn.com/6cf435db-3b5e-4833-9f06-bce1388e9610/-/format/auto/-/preview/600x600/-/quality/lighter/CertiProf-Scrum-Foundation.png",
        width=100,
        height=100,
    )

    def iniciar_quiz_com_som(e):
        """
        Inicia o quiz e reproduz o áudio de início.

        Args:
            e: Objeto evento do Flet.
        """
        reproduzir_audio("inicio")
        controller.iniciar_quiz(e)

    button_start = ft.ElevatedButton(
        "Iniciar Quiz", on_click=iniciar_quiz_com_som, width=200, height=50
    )
    close = ft.ElevatedButton(
        "Fechar", on_click=lambda _: page.window.close(), width=200, height=50
    )
    button_certificacao = ft.ElevatedButton(
        "Certificação agora!",
        on_click=lambda _: page.launch_url(
            "https://certiprof.com/pages/sfpc-scrum-foundation-certification-portuguese?srsltid=AfmBOopH_aNk26kwJWdz54azChJOrEy9F9xy8lUFa3F63pBq6bWBf602"
        ),
        width=200,
        height=50,
    )

    page.add(
        ft.Column(
            [
                scrum_icon,
                button_start,
                close,
                button_certificacao,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # Utiliza o controlador para gerenciar o botão "Fechar"
    btn_result__close.on_click = controller.voltar_ao_inicio


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

    page.clean() 
    question_text = ft.Text(
        f"{estado_quiz.pergunta_atual + 1}. {pergunta.enunciado}", size=20
    )
    answer_buttons = []

    for i, opcao in enumerate(pergunta.opcoes):
        if isinstance(opcao, str) and opcao.strip():
            button = ft.ElevatedButton(
                text=f"{chr(ord('a') + i)}) {opcao}",
                on_click=controller.verificar_resposta,
                data=i, 
            )
            answer_buttons.append(button)

    score_text = ft.Text(
        f"Tempo restante: {estado_quiz.tempo_restante // 60:02d}:{estado_quiz.tempo_restante % 60:02d}",
        size=16,
    )
    controller.texto_tempo = score_text

    page.add(
        ft.Column(
            [
                score_text, 
                question_text,
                *answer_buttons,
                ft.ElevatedButton(
                    "Voltar ao Início", on_click=controller.voltar_ao_inicio
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    def atualizar_tempo():
        """Atualiza o tempo restante do quiz a cada segundo."""
        if estado_quiz.tempo_restante > 0 and estado_quiz.quiz_iniciado:
            estado_quiz.tempo_restante -= 1
            horas, resto = divmod(estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            score_text.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            page.update()
            page.on_idle = lambda _: threading.Timer(1, atualizar_tempo).start()
        else:
            reproduzir_audio("acabar")
            controller.finalizar_quiz(None)

    atualizar_tempo()


def exibir_resultados(page: ft.Page, estado_quiz: EstadoQuiz, controller):
    """
    Exibe os resultados do quiz em um AlertDialog.

    Args:
        page (ft.Page): A página do Flet para exibir os resultados.
        estado_quiz (EstadoQuiz): O estado final do quiz.
        controller: O objeto controlador do quiz. 
    """
    total_perguntas = len(controller.quiz_logic.questions)
    total_acertos = estado_quiz.pontuacao
    total_erros = total_perguntas - total_acertos

    if not controller.modal_aberto:  # Verifica se o modal já está aberto
        def close_dlg(e):
            """Fecha o diálogo modal."""
            dlg_modal.open = False
            controller.modal_aberto = False
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
                ft.ElevatedButton("Fechar", on_click=controller.fechar_modal),
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
        controller.modal_aberto = True
        page.update()

    if estado_quiz.pontuacao >= 70:
        reproduzir_audio("ganhou")
    else:
        reproduzir_audio("perdeu")


def piscar_verde(botao: ft.Control):
    """
    Faz o botão piscar na cor verde.

    Args:
        botao (ft.Control): O botão que irá piscar.
    """
    botao.bgcolor = ft.colors.GREEN
    botao.update()
    time.sleep(0.2)
    botao.bgcolor = None
    botao.update()


def piscar_vermelho(botao: ft.Control):
    """
    Faz o botão piscar na cor vermelha.

    Args:
        botao (ft.Control): O botão que irá piscar.
    """
    botao.bgcolor = ft.colors.RED
    botao.update()
    time.sleep(0.2)
    botao.bgcolor = None
    botao.update()
