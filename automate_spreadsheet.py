import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import time

# Credenciais do Google Sheets e Google Docs (separadas para clareza)
SHEETS_CREDENTIALS_FILE = "credentials.json"
DOCS_CREDENTIALS_FILE = "credentials_docs.json"

# Escopos para Google Sheets e Google Docs
SHEETS_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
DOCS_SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

# URL da planilha e ID do documento (mantidos como constantes globais)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"
DOCUMENT_ID = "1kQU6ElV41Y73Iiu6N1lOcfAoHaaWSNTqmOnOWBhifgg"

# Intervalo de verificação para alterações no Google Docs (em segundos)
MONITORING_INTERVAL = 300


def extract_questions_from_doc(document_id):
    """
    Extrai perguntas e respostas de um documento do Google Docs,
    levando em consideração as quebras de linha dentro das opções de resposta.

    Args:
        document_id: O ID do documento do Google Docs.

    Returns:
        Uma lista de listas, onde cada sublista representa uma pergunta
        e suas opções de resposta, com a resposta correta no final.
    """

    credentials = service_account.Credentials.from_service_account_file(
        DOCS_CREDENTIALS_FILE, scopes=DOCS_SCOPES
    )
    service = build("docs", "v1", credentials=credentials)

    document = service.documents().get(documentId=document_id).execute()
    content = document.get("body").get("content")

    questions = []
    current_question = None
    correct_answer = ""

    for item in content:
        if "paragraph" in item:
            elements = item.get("paragraph").get("elements")
            text = ""
            for element in elements:
                if "textRun" in element:
                    text += element["textRun"]["content"]

            text = text.strip()

            if text:
                # Verifica se é uma opção de resposta (formato: "a) ")
                if len(text) > 2 and text[1] == ")" and text[0] in ['a', 'b', 'c', 'd']:
                    if current_question is not None:
                        current_question.append(text[2:].strip())
                        if "bold" in elements[0].get("textRun", {}).get("textStyle", {}):
                            correct_answer = text[0]
                else:
                    # Se não for uma opção, é uma nova pergunta
                    if current_question is not None:
                        current_question.append(correct_answer)
                        questions.append(current_question)
                    current_question = [text]
                    correct_answer = ""
        else:
            # Se não for um parágrafo, finaliza a pergunta atual
            if current_question is not None:
                current_question.append(correct_answer)
                questions.append(current_question)
                current_question = None
                correct_answer = ""

    # Adiciona a última pergunta, se houver
    if current_question is not None:
        current_question.append(correct_answer)
        questions.append(current_question)

    return questions


def write_to_spreadsheet(questions, spreadsheet_url):
    """
    Escreve as perguntas na planilha, evitando duplicatas e formatando
    cada pergunta em uma linha separada, com cada elemento da pergunta
    em uma coluna diferente. Preenche as opções de resposta faltantes
    com strings vazias. Exibe uma mensagem de aviso para perguntas
    com menos de 4 opções.
    Aplica formatação em negrito à coluna "Pergunta" e à coluna que contém a resposta correta.

    Args:
        questions: Uma lista de listas representando as perguntas e respostas.
        spreadsheet_url: A URL da planilha.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SHEETS_CREDENTIALS_FILE, scopes=SHEETS_SCOPES
    )
    client = gspread.authorize(credentials)

    sheet = client.open_by_url(spreadsheet_url).sheet1
    existing_questions = sheet.col_values(1)[1:]  # Ignora o cabeçalho

    new_questions = [
        question for question in questions if question[0] not in existing_questions
    ]

    if new_questions:
        formatted_questions = []
        for question in new_questions:
            # Verifica se a pergunta tem pelo menos 4 opções de resposta
            if len(question) < 5:
                print(f"Aviso: A pergunta '{question[0]}' tem menos de 4 opções de resposta. Verifique o Google Docs.")

            # Formata a pergunta em negrito
            question[0] = f"<b>{question[0]}</b>"

            # Formata a opção correta em negrito
            if len(question) == 6 and question[5] in ['a', 'b', 'c', 'd']:
                correct_option_index = ord(question[5]) - ord('a') + 1  # Calcula o índice da opção correta (1 para 'a', 2 para 'b', etc.)
                if 1 <= correct_option_index <= 4:
                    question[correct_option_index] = f"<b>{question[correct_option_index]}</b>"

            # Preenche as opções de resposta faltantes com strings vazias
            while len(question) < 6:  # Garante que a pergunta tenha 6 elementos (pergunta + 4 opções + resposta)
                question.append("")

            formatted_questions.append(question)

        next_row = len(existing_questions) + 2
        update_range = f"A{next_row}:F{next_row + len(formatted_questions) - 1}"

        # Usa a ordem correta dos argumentos e argumentos nomeados
        sheet.update(values=formatted_questions, range_name=update_range)

        print(f"{len(formatted_questions)} novas perguntas adicionadas à planilha.")
    else:
        print("Nenhuma nova pergunta encontrada.")


def monitor_google_docs(document_id, spreadsheet_url, interval=MONITORING_INTERVAL):
    """
    Monitora o Google Docs para alterações e atualiza a planilha.

    Args:
        document_id: O ID do documento do Google Docs a ser monitorado.
        spreadsheet_url: A URL da planilha do Google Sheets a ser atualizada.
        interval: O intervalo de tempo (em segundos) para verificar se há alterações
                  no Google Docs.
    """
    last_revision_id = None
    while True:
        try:
            credentials = service_account.Credentials.from_service_account_file(
                DOCS_CREDENTIALS_FILE, scopes=DOCS_SCOPES
            )
            service = build("docs", "v1", credentials=credentials)
            document = service.documents().get(documentId=document_id).execute()
            current_revision_id = document["revisionId"]

            if current_revision_id != last_revision_id:
                print("Mudanças detectadas no Google Docs. Atualizando a planilha...")

                # Chama a função e atribui o resultado à variável 'questions'
                questions = extract_questions_from_doc(document_id)

                write_to_spreadsheet(questions, spreadsheet_url)
                last_revision_id = current_revision_id

            time.sleep(interval)
        except Exception as e:
            print(f"Erro ao monitorar o Google Docs: {e}")
            time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente


if __name__ == "__main__":
    monitor_google_docs(DOCUMENT_ID, SPREADSHEET_URL)
