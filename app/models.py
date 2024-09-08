class Pergunta:
    """
    Representa uma pergunta do quiz com seu enunciado, opções de resposta
    e a resposta correta.
    """

    def __init__(self, enunciado: str, opcoes: list, resposta_correta: int):
        """
        Inicializa uma nova pergunta.

        Args:
            enunciado (str): O texto da pergunta.
            opcoes (list): Uma lista de opções de resposta (strings).
            resposta_correta (int): O índice da resposta correta na lista 'opcoes'.
        """
        self.enunciado = enunciado
        self.opcoes = opcoes
        self.resposta_correta = resposta_correta


class EstadoQuiz:
    """
    Mantém o estado atual do quiz, incluindo a pergunta atual, tempo restante,
    pontuação, e se o quiz está em andamento ou finalizado.
    """

    def __init__(self):
        """Inicializa um novo estado de quiz."""
        self.pergunta_atual: int = 0  # Índice da pergunta atual 
        self.tempo_restante: int = 3600  # Tempo restante em segundos
        self.pontuacao: int = 0  # Pontuação atual 
        self.quiz_iniciado: bool = False  # True se o quiz foi iniciado
        self.quiz_finalizado: bool = False  # True se o quiz foi finalizado

    def proxima_pergunta(self):
        """Avança para a próxima pergunta do quiz."""
        self.pergunta_atual += 1

    def reiniciar(self):
        """Reinicia o estado do quiz para o início."""
        self.pergunta_atual = 0
        self.tempo_restante = 3600
        self.pontuacao = 0
        self.quiz_iniciado = False
        self.quiz_finalizado = False
