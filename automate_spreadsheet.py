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
                # Remove espaços em branco (incluindo quebras de linha) no início e no final da string
                text = text.strip()

                # Verifica se o texto está em negrito
                is_bold = "bold" in elements[0].get("textRun").get("textStyle", {})

                if is_bold:
                    # Se for uma nova pergunta em negrito
                    if text[0].isdigit() and text[1] == ".":
                        if current_question:
                            current_question.append(correct_answer)
                            questions.append(current_question)
                        current_question = [text[2:].strip()]
                        correct_answer = ""
                    # Se for a resposta correta em negrito
                    elif text[0] in ["a", "b", "c", "d"] and text[1] == ")":
                        correct_answer = text[0]
                # Se não for negrito, é uma opção de resposta normal
                elif text[0] in ["a", "b", "c", "d"] and text[1] == ")":
                    current_question.append(text[2:].strip())

        elif "table" in item:  # Ignora tabelas no documento
            continue

    if current_question:
        current_question.append(correct_answer)
        questions.append(current_question)

    return questions


def write_to_spreadsheet(questions, spreadsheet_url):
    """Escreve as perguntas na planilha, evitando duplicatas."""
    sheet = CLIENT_SHEETS.open_by_url(spreadsheet_url).sheet1
    existing_questions = sheet.col_values(1)[1:]

    print(
        "Perguntas existentes na planilha:", existing_questions
    )  # Depuração: Imprime as perguntas existentes

    new_questions = []
    for question in questions:
        if question[0] not in existing_questions:
            new_questions.append(question)
        else:
            print(f"Pergunta duplicada ignorada: {question[0]}")

    if new_questions:
        sheet.append_rows(new_questions)
        print(f"{len(new_questions)} novas perguntas adicionadas à planilha.")
    else:
        print("Nenhuma nova pergunta encontrada.")


def monitor_google_docs(document_id, spreadsheet_url, interval=300):
    """Monitora o Google Docs para alterações e atualiza a planilha."""
    last_revision_id = None
    while True:
        try:
            service = build("docs", "v1", credentials=CREDS_DOCS)
            document = service.documents().get(documentId=document_id).execute()
            current_revision_id = document["revisionId"]

            if current_revision_id != last_revision_id:
                print("Mudanças detectadas no Google Docs. Atualizando a planilha...")
                questions = extract_questions_from_doc(document_id)
                print(
                    "Perguntas extraídas do Google Docs:", questions
                )  # Depuração: Imprime as perguntas extraídas
                write_to_spreadsheet(questions, spreadsheet_url)
                last_revision_id = current_revision_id

            time.sleep(interval)  # Aguarda o intervalo especificado
        except Exception as e:
            print(f"Erro ao monitorar o Google Docs: {e}")
            time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente


if __name__ == "__main__":
    monitor_google_docs(DOCUMENT_ID, SPREADSHEET_URL)
