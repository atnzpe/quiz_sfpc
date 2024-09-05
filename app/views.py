# app/views.py
import flet as ft
from .models import Pergunta, EstadoQuiz
import random
import pygame  # Importe o pygame
import os
import threading

# Inicialize o mixer do Pygame
pygame.mixer.init()

# Função para reproduzir um áudio aleatório de uma pasta
def reproduzir_audio(pasta):
    """Reproduz um áudio aleatório da pasta especificada."""
    caminho_pasta = os.path.join(os.path.dirname(__file__), 'audio', pasta)  # Caminho relativo
    arquivos_de_audio = [
        f for f in os.listdir(caminho_pasta) if f.endswith(".mp3") or f.endswith(".wav")
    ]
    if arquivos_de_audio:
        audio_aleatorio = random.choice(arquivos_de_audio)
        caminho_do_audio = os.path.join(caminho_pasta, audio_aleatorio)
        pygame.mixer.music.load(caminho_do_audio)  # Carrega o áudio
        pygame.mixer.music.play()  # Reproduz o áudio


def exibir_tela_inicial(page: ft.Page, controller):
    """Exibe a tela inicial do quiz."""
    reproduzir_audio("inicio")  # Reproduz um áudio aleatório da pasta "inicio"

    titulo = ft.Container(
        ft.Text("Quiz - SFPC™", size=24, weight="bold"),
        alignment=ft.alignment.center,
    )

    scrum_icon = ft.Image(
        src="https://ucarecdn.com/6cf435db-3b5e-4833-9f06-bce1388e9610/-/format/auto/-/preview/600x600/-/quality/lighter/CertiProf-Scrum-Foundation.png",
        width=100,
        height=100,
    )

    button_start = ft.ElevatedButton(
        "Iniciar Quiz", on_click=controller.iniciar_quiz, width=200, height=50
    )
    button_close = ft.ElevatedButton(
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
                titulo,  # Título centralizado
                scrum_icon,
                button_start,
                button_close,
                button_certificacao,  # Botão de certificação
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


def exibir_pergunta(
    page: ft.Page, pergunta: Pergunta, estado_quiz: EstadoQuiz, controller
):
    """Exibe a pergunta atual do quiz."""

    page.clean()
    question_text = ft.Text(
        f"{estado_quiz.pergunta_atual + 1}. {pergunta.enunciado}", size=20
    )
    answer_buttons = []

    for i, opcao in enumerate(pergunta.opcoes):
        button = ft.ElevatedButton(
            text=opcao, on_click=controller.verificar_resposta, data=i
        )
        answer_buttons.append(button)

    # Cria o Text para exibir o tempo
    score_text = ft.Text(
        f"Tempo restante: {estado_quiz.tempo_restante // 60:02d}:{estado_quiz.tempo_restante % 60:02d}",
        size=16,
    )
    controller.texto_tempo = (
        score_text  # Define a referencia do texto_tempo no Controller
    )

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
        """Atualiza o tempo restante a cada segundo."""
        if estado_quiz.tempo_restante > 0 and estado_quiz.quiz_iniciado:
            estado_quiz.tempo_restante -= 1
            horas, resto = divmod(estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            score_text.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            page.update()
            # Agenda a próxima atualização em 1 segundo
            page.on_idle = lambda _: threading.Timer(1, atualizar_tempo).start()
        else:
            reproduzir_audio(
                "acabar"
            )  # Reproduz áudio da pasta "acabar" quando o tempo acabar
            controller.finalizar_quiz(None)  # Finaliza o quiz se o tempo acabar

    # Inicia a atualização do tempo
    atualizar_tempo()


def exibir_resultados(page: ft.Page, estado_quiz: EstadoQuiz, controller):
    """Exibe os resultados do quiz."""

    def close_dlg(e):
        """Fecha o diálogo modal."""
        dlg_modal.open = False
        page.update()

    # Cria o diálogo modal para exibir os resultados
    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Fim do Quiz!"),
        content=ft.Text(
            f"Sua pontuação final: {estado_quiz.pontuacao}\n{'Aprovado!' if estado_quiz.pontuacao >= 70 else 'Reprovado.'}"
        ),
        actions=[
            ft.TextButton("Fechar", on_click=close_dlg),
        ],
        on_dismiss=lambda e: print(
            "Modal dialog dismissed!"
        ),  # Ação ao fechar o diálogo
    )
    page.dialog = dlg_modal
    dlg_modal.open = True
    page.update()

    if estado_quiz.pontuacao >= 70:
        reproduzir_audio("ganhou")  # Reproduz áudio da pasta "ganhou" se aprovado
    else:
        reproduzir_audio("perdeu")  # Reproduz áudio da pasta "perdeu" se reprovado

