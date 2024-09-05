# app/models.py

class Pergunta:
    """
    Representa uma pergunta do quiz com seu enunciado, opções de resposta
    e a resposta correta.
    """
    def __init__(self, enunciado, opcoes, resposta_correta):
        self.enunciado = enunciado  # O texto da pergunta
        self.opcoes = opcoes  # Uma lista de opções de resposta
        self.resposta_correta = resposta_correta  # O índice da resposta correta na lista 'opcoes'

class EstadoQuiz:
    """
    Mantém o estado atual do quiz, incluindo a pergunta atual, tempo restante,
    pontuação, e se o quiz está em andamento ou finalizado.
    """
    def __init__(self):
        self.pergunta_atual = 0  # Índice da pergunta atual na lista de perguntas
        self.tempo_restante = 3600  # Tempo restante em segundos (1 hora)
        self.pontuacao = 0  # Pontuação atual do usuário
        self.quiz_iniciado = False  # Indica se o quiz foi iniciado
        self.quiz_finalizado = False  # Indica se o quiz foi finalizado
