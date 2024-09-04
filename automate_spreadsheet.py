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
    Extrai perguntas e respostas de um documento do Google Docs.

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
    current_question = []
    correct_answer = ""

    for item in content:
        if "paragraph" in item:
            elements = item.get("paragraph").get("elements")
            text = "".join(
                element.get("textRun", {}).get("content", "").strip()
                for element in elements
            )

            text = text.strip()

            # Verifica se o parágrafo não está vazio
            if text:
                # Verifica se o parágrafo começa com uma letra seguida de ')', o que indica uma opção de resposta
                if len(text) > 2 and text[1] == ")" and text[0] in ['a', 'b', 'c', 'd']:
                    current_question.append(text[2:].strip())  # Adiciona a opção à pergunta atual
                    if "bold" in elements[0].get("textRun", {}).get("textStyle", {}):
                        correct_answer = text[0]  # Define a resposta correta se estiver em negrito
                else:
                    # Se não for uma opção, considera como uma nova pergunta
                    if current_question:
                        current_question.append(correct_answer)  # Adiciona a resposta correta à pergunta anterior
                        questions.append(current_question)
                    current_question = [text]  # Inicia uma nova pergunta
                    correct_answer = ""
            else:
                # Se o parágrafo estiver vazio, termina a pergunta atual
                if current_question:
                    current_question.append(correct_answer)
                    questions.append(current_question)
                    current_question = []
                    correct_answer = ""

    # Adiciona a última pergunta coletada
    if current_question:
        current_question.append(correct_answer)
        questions.append(current_question)

    return questions


def write_to_spreadsheet(questions, spreadsheet_url):
    """
    Escreve as perguntas na planilha, evitando duplicatas e formatando
    cada pergunta em uma linha separada, com cada elemento da pergunta
    em uma coluna diferente.

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
            # Formata a Opção 2 em negrito
            question[2] = f"<b>{question[2]}</b>"

            # Adiciona a resposta correta no final, se presente
            if len(question) > 5 and question[5] in ["a", "b", "c", "d"]:
                formatted_questions.append(question[:5] + [question[5]])
            else:
                formatted_questions.append(question[:5] + [""])

        next_row = len(existing_questions) + 2
        update_range = f"A{next_row}:F{next_row + len(formatted_questions) - 1}"

        # Correção: Usa a ordem correta dos argumentos e argumentos nomeados
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
                questions = extract_questions_from_doc(document_id)
                write_to_spreadsheet(questions, spreadsheet_url)
                last_revision_id = current_revision_id

            time.sleep(interval)
        except Exception as e:
            print(f"Erro ao monitorar o Google Docs: {e}")
            time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente


if __name__ == "__main__":
    monitor_google_docs(DOCUMENT_ID, SPREADSHEET_URL)
