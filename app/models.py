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
        self.enunciado = enunciado  # Atribui o enunciado da pergunta
        self.opcoes = opcoes  # Atribui a lista de opções de resposta
        self.resposta_correta = resposta_correta  # Atribui o índice da resposta correta


class EstadoQuiz:
    """
    Mantém o estado atual do quiz, incluindo a pergunta atual, tempo restante,
    pontuação, e se o quiz está em andamento ou finalizado.
    """

    def __init__(self):
        """Inicializa um novo estado de quiz."""
        self.pergunta_atual: int = (
            0  # Índice da pergunta atual (inicia na primeira pergunta)
        )
        self.tempo_restante: int = 3600  # Tempo restante em segundos (1 hora)
        self.pontuacao: int = 0  # Pontuação atual (inicia em 0)
        self.quiz_iniciado: bool = (
            False  # Indica se o quiz foi iniciado (inicia como False)
        )
        self.quiz_finalizado: bool = (
            False  # Indica se o quiz foi finalizado (inicia como False)
        )

    def proxima_pergunta(self):
        """Avança para a próxima pergunta do quiz."""
        self.pergunta_atual += 1  # Incrementa o índice da pergunta atual

    def reiniciar(self):
        """Reinicia o estado do quiz para o início."""
        self.pergunta_atual = 0  # Reinicia o índice da pergunta atual
        self.tempo_restante = 3600  # Reinicia o tempo restante
        self.pontuacao = 0  # Reinicia a pontuação
        self.quiz_iniciado = False  # Define o quiz como não iniciado
        self.quiz_finalizado = False  # Define o quiz como não finalizado
