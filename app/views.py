import flet as ft
from .models import Pergunta, EstadoQuiz  # Importa as classes Pergunta e EstadoQuiz do arquivo models.py
import random
import pygame  # Importa a biblioteca Pygame para reprodução de áudio
import os
import threading

# Inicializa o mixer do Pygame para reprodução de áudio
pygame.mixer.init()

# Define o botão "Fechar" como uma variável global.
# Inicialmente, o evento on_click é definido como None, 
# pois será configurado posteriormente na função exibir_tela_inicial.
btn_result__close = ft.ElevatedButton(
    "Fechar", on_click=None, width=200, height=50
)

# Função para reproduzir um áudio aleatório de uma pasta específica
def reproduzir_audio(pasta):
    """Reproduz um áudio aleatório da pasta especificada."""
    # Define o caminho completo para a pasta de áudio, 
    # considerando a estrutura de diretórios do projeto.
    caminho_pasta = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
        "audio",
        pasta,
    )
    # Cria uma lista com os nomes dos arquivos de áudio na pasta especificada,
    # filtrando apenas arquivos .mp3 e .wav.
    arquivos_de_audio = [
        f
        for f in os.listdir(caminho_pasta)
        if f.endswith(".mp3") or f.endswith(".wav")
    ]
    # Se houver arquivos de áudio na pasta:
    if arquivos_de_audio:
        # Escolhe aleatoriamente um arquivo de áudio da lista.
        audio_aleatorio = random.choice(arquivos_de_audio)
        # Define o caminho completo para o arquivo de áudio selecionado.
        caminho_do_audio = os.path.join(caminho_pasta, audio_aleatorio)
        # Carrega o arquivo de áudio no mixer do Pygame.
        pygame.mixer.music.load(caminho_do_audio)
        # Reproduz o áudio carregado.
        pygame.mixer.music.play()


# Função para exibir a tela inicial do quiz
def exibir_tela_inicial(page: ft.Page, controller):
    """Exibe a tela inicial do quiz."""

    # Cria um widget Image para exibir o ícone do Scrum.
    scrum_icon = ft.Image(
        src="https://ucarecdn.com/6cf435db-3b5e-4833-9f06-bce1388e9610/-/format/auto/-/preview/600x600/-/quality/lighter/CertiProf-Scrum-Foundation.png",
        width=100,
        height=100,
    )

    # Define uma função interna para iniciar o quiz e reproduzir o áudio de início.
    def iniciar_quiz_com_som(e):
        # Reproduz o áudio da pasta "inicio".
        reproduzir_audio("inicio")
        # Chama a função iniciar_quiz do controlador para iniciar o quiz.
        controller.iniciar_quiz(e)

    # Cria um botão "Iniciar Quiz" que chama a função iniciar_quiz_com_som quando clicado.
    button_start = ft.ElevatedButton(
        "Iniciar Quiz", on_click=iniciar_quiz_com_som, width=200, height=50
    )
    # Cria um botão "Fechar" que fecha a janela do aplicativo quando clicado.
    close = ft.ElevatedButton(
        "Fechar", on_click=lambda _: page.window.close(), width=200, height=50
    )
    # Cria um botão "Certificação agora!" que abre o link da certificação no navegador.
    button_certificacao = ft.ElevatedButton(
        "Certificação agora!",
        on_click=lambda _: page.launch_url(
            "https://certiprof.com/pages/sfpc-scrum-foundation-certification-portuguese?srsltid=AfmBOopH_aNk26kwJWdz54azChJOrEy9F9xy8lUFa3F63pBq6bWBf602"
        ),
        width=200,
        height=50,
    )

    # Adiciona os widgets à página, organizando-os em uma coluna centralizada.
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
    # para chamar a função voltar_ao_inicio do controlador.
    # Isso é feito aqui para garantir que o controlador já esteja inicializado.
    btn_result__close.on_click = controller.voltar_ao_inicio


# Função para exibir uma pergunta do quiz
def exibir_pergunta(
    page: ft.Page, pergunta: Pergunta, estado_quiz: EstadoQuiz, controller
):
    """Exibe a pergunta atual do quiz."""

    # Limpa a página atual.
    page.clean()
    # Cria um widget Text para exibir o número da pergunta e o enunciado.
    question_text = ft.Text(
        f"{estado_quiz.pergunta_atual + 1}. {pergunta.enunciado}", size=20
    )
    # Cria uma lista vazia para armazenar os botões de resposta.
    answer_buttons = []

    # Cria uma lista com as letras das opções de resposta (a, b, c, d).
    option_letters = ["a", "b", "c", "d"]
    # Embaralha a ordem das letras para que as opções de resposta não sejam sempre na mesma ordem.
    random.shuffle(option_letters)

    # Itera sobre as opções de resposta da pergunta.
    for i, opcao in enumerate(pergunta.opcoes):
        # Verifica se a opção é uma string não vazia.
        if isinstance(opcao, str) and opcao.strip():
            # Cria um botão para a opção de resposta.
            button = ft.ElevatedButton(
                # Define o texto do botão como a letra da opção seguida da opção em si.
                text=f"{option_letters[i]}) {opcao}",
                # Define o evento on_click do botão para chamar a função verificar_resposta do controlador.
                on_click=controller.verificar_resposta,
                # Define o atributo data do botão como o índice da opção de resposta na lista de opções.
                data=i,
            )
            # Adiciona o botão à lista de botões de resposta.
            answer_buttons.append(button)

    # Cria um widget Text para exibir o tempo restante do quiz.
    score_text = ft.Text(
        f"Tempo restante: {estado_quiz.tempo_restante // 60:02d}:{estado_quiz.tempo_restante % 60:02d}",
        size=16,
    )
    # Define o atributo texto_tempo do controlador como o widget score_text,
    # permitindo que o controlador acesse e atualize o tempo restante na tela.
    controller.texto_tempo = score_text

    # Adiciona os widgets à página, organizando-os em uma coluna centralizada.
    page.add(
        ft.Column(
            [
                # Widget para exibir o tempo restante.
                score_text,
                # Widget para exibir o número e enunciado da pergunta.
                question_text,
                # Desempacota a lista de botões de resposta e os adiciona à coluna.
                *answer_buttons,
                # Cria um botão "Voltar ao Início" que chama a função voltar_ao_inicio do controlador quando clicado.
                ft.ElevatedButton(
                    "Voltar ao Início", on_click=controller.voltar_ao_inicio
                ),
            ],
            # Define o alinhamento vertical da coluna para o centro.
            alignment=ft.MainAxisAlignment.CENTER,
            # Define o alinhamento horizontal da coluna para o centro.
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # Define uma função interna para atualizar o tempo restante do quiz.
    def atualizar_tempo():
        """Atualiza o tempo restante a cada segundo."""
        # Verifica se o quiz está em andamento (tempo restante > 0 e quiz iniciado).
        if estado_quiz.tempo_restante > 0 and estado_quiz.quiz_iniciado:
            # Decrementa o tempo restante em 1 segundo.
            estado_quiz.tempo_restante -= 1
            # Calcula as horas, minutos e segundos restantes a partir do tempo restante.
            horas, resto = divmod(estado_quiz.tempo_restante, 3600)
            minutos, segundos = divmod(resto, 60)
            # Atualiza o texto do widget score_text com o tempo restante formatado.
            score_text.value = (
                f"Tempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
            # Atualiza a página para refletir as mudanças.
            page.update()
            # Agenda a próxima chamada da função atualizar_tempo em 1 segundo,
            # criando um loop de atualização do tempo restante.
            page.on_idle = lambda _: threading.Timer(1, atualizar_tempo).start()
        else:
            # Se o tempo acabar, reproduz o áudio da pasta "acabar".
            reproduzir_audio("acabar")
            # Chama a função finalizar_quiz do controlador para finalizar o quiz.
            controller.finalizar_quiz(None)

    # Inicia a atualização do tempo chamando a função atualizar_tempo pela primeira vez.
    atualizar_tempo()


# Função para exibir os resultados do quiz
def exibir_resultados(page: ft.Page, estado_quiz, controller):
    """
    Exibe os resultados do quiz, incluindo estatísticas, mensagem de aprovação/reprovação
    e link para download do guia (se necessário).
    """

    # Obtém o número total de perguntas do quiz.
    total_perguntas = len(controller.quiz_logic.questions)
    # Obtém o número de acertos do usuário.
    total_acertos = estado_quiz.pontuacao
    # Calcula o número de erros do usuário.
    total_erros = total_perguntas - total_acertos

    # Define uma função interna para fechar o diálogo modal de resultados
    # e retornar à tela inicial.
    def close_dlg(e):
        """Fecha o diálogo modal e retorna à tela inicial."""
        # Fecha o diálogo modal definindo o atributo open como False.
        dlg_modal.open = False
        # Chama a função exibir_tela_inicial do controlador para retornar à tela inicial.
        controller.exibir_tela_inicial()
        # Atualiza a página para refletir as mudanças.
        page.update()

    # Cria um diálogo modal (AlertDialog) para exibir os resultados do quiz.
    dlg_modal = ft.AlertDialog(
        # Define o diálogo como modal, impedindo a interação com o restante da tela enquanto estiver aberto.
        modal=True,
        # Define o título do diálogo.
        title=ft.Text("Fim do Quiz!"),
        # Define o conteúdo do diálogo como uma coluna com os resultados do quiz.
        content=ft.Column(
            [
                # Exibe a pontuação final do usuário.
                ft.Text(
                    f"Sua pontuação final: {estado_quiz.pontuacao}/{total_perguntas}"
                ),
                # Exibe o número de acertos.
                ft.Text(f"Acertos: {total_acertos}"),
                # Exibe o número de erros.
                ft.Text(f"Erros: {total_erros}"),
                # Exibe a mensagem de aprovado ou reprovado,
                # dependendo da pontuação do usuário.
                ft.Text(
                    f"{'Aprovado!' if estado_quiz.pontuacao >= 32 else 'Reprovado.'}"
                ),
            ]
        ),
        # Define as ações do diálogo, que são os botões exibidos na parte inferior.
        actions=[
            # Adiciona o botão "Fechar" (btn_result__close) ao diálogo.
            # O botão já está definido globalmente e tem o evento on_click configurado para
            # chamar a função voltar_ao_inicio do controlador.
            btn_result__close,
        ],
        # Define o evento on_dismiss do diálogo para chamar a função close_dlg quando o diálogo for fechado.
        on_dismiss=close_dlg,
    )

    # Adiciona um botão "Baixar Guia Scrum" ao diálogo se o usuário for reprovado.
    if estado_quiz.pontuacao < 32:
        dlg_modal.actions.append(
            ft.ElevatedButton(
                "Baixar Guia Scrum",
                # Define o evento on_click do botão para abrir o link do Guia Scrum no navegador.
                on_click=lambda _: page.launch_url("https://www.scrumguides.org/"),
            )
        )

    # Adiciona o diálogo modal à lista de overlays da página.
    page.overlay.append(dlg_modal)
    # Abre o diálogo modal definindo o atributo open como True.
    dlg_modal.open = True
    # Atualiza a página para refletir as mudanças.
    page.update()

    # Reproduz o áudio de "ganhou" se o usuário for aprovado
    # ou o áudio de "perdeu" se o usuário for reprovado.
    if estado_quiz.pontuacao >= 70:
        reproduzir_audio("ganhou")
    else:
        reproduzir_audio("perdeu")
