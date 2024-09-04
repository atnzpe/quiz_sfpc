import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import time

# Credenciais do Google Sheets
SCOPE_SHEETS = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
CREDS_SHEETS = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPE_SHEETS
)
CLIENT_SHEETS = gspread.authorize(CREDS_SHEETS)

# Credenciais do Google Docs
SCOPE_DOCS = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
CREDS_DOCS = service_account.Credentials.from_service_account_file(
    "credentials_docs.json", scopes=SCOPE_DOCS
)

# URL da planilha
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"

# ID do documento do Google Docs
DOCUMENT_ID = "1kQU6ElV41Y73Iiu6N1lOcfAoHaaWSNTqmOnOWBhifgg"


def extract_questions_from_doc(document_id):
    """Extrai perguntas e respostas de um documento do Google Docs."""
    service = build("docs", "v1", credentials=CREDS_DOCS)
    document = service.documents().get(documentId=document_id).execute()
    content = document.get("body").get("content")

    questions = []
    current_question = []
    correct_answer = ""

    for item in content:
        if "paragraph" in item:
            elements = item.get("paragraph").get("elements")
            text = "".join(
                [
                    element.get("textRun").get("content").strip()
                    for element in elements
                    if "textRun" in element
                ]
            )

            if text:
                # Verifica se o texto está em negrito para identificar a pergunta e a resposta correta
                is_bold = "bold" in elements[0].get("textRun").get("textStyle", {})

                if is_bold:
                    if current_question:
                        # Adiciona a resposta correta à pergunta atual
                        current_question.append(correct_answer)
                        questions.append(current_question)

                    # Inicia uma nova pergunta
                    current_question = [text]
                    correct_answer = ""
                elif (
                    text[0] in ["a", "b", "c", "d"] and text[1] == ")"
                ):  # Opção de resposta
                    if is_bold:
                        correct_answer = text[
                            0
                        ]  # Define a resposta correta (letra da opção)
                    current_question.append(
                        text[2:].strip()
                    )  # Adiciona a opção de resposta
        elif "table" in item:
            continue

    # Adiciona a última pergunta
    if current_question:
        current_question.append(correct_answer)
        questions.append(current_question)

    return questions


def write_to_spreadsheet(questions, spreadsheet_url):
    """Escreve as perguntas na planilha, evitando duplicatas."""
    # ... (Função sem alterações)


def monitor_google_docs(document_id, spreadsheet_url, interval=300):
    """Monitora o Google Docs para alterações e atualiza a planilha."""
    # ... (Função sem alterações)


if __name__ == "__main__":
    monitor_google_docs(DOCUMENT_ID, SPREADSHEET_URL)
