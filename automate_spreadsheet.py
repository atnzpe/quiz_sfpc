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
        e suas opções de resposta. A resposta correta é indicada pela
        letra da opção (a, b, c, d).
    """

    # Constrói o serviço Google Docs usando as credenciais
    credentials = service_account.Credentials.from_service_account_file(
        DOCS_CREDENTIALS_FILE, scopes=DOCS_SCOPES
    )
    service = build("docs", "v1", credentials=credentials)

    #  Correção: Utiliza 'service.documents()' para acessar o recurso 'documents'
    document = service.documents().get(documentId=document_id).execute() 
    content = document.get("body").get("content")

    questions = []
    current_question = []
    correct_answer = ""

    # Itera sobre os elementos do conteúdo do documento
    for item in content:
        if "paragraph" in item:
            elements = item.get("paragraph").get("elements")
            text = "".join(
                element.get("textRun", {}).get("content", "").strip()
                for element in elements
            )

            # Remove espaços em branco desnecessários
            text = text.strip()

            # Verifica se é o início de uma nova pergunta
            if text and text[0].isdigit() and text[1] == ".":
                if current_question:
                    current_question.append(correct_answer)
                    questions.append(current_question)
                current_question = [text[2:].strip()]
                correct_answer = ""
            # Verifica se é uma opção de resposta
            elif text and text[0] in ["a", "b", "c", "d"] and text[1] == ")":
                # Verifica se a opção está em negrito (resposta correta)
                if "bold" in elements[0].get("textRun", {}).get("textStyle", {}):
                    correct_answer = text[0]
                current_question.append(text[2:].strip())

        # Ignora tabelas no documento
        elif "table" in item:
            continue

    # Adiciona a última pergunta coletada
    if current_question:
        current_question.append(correct_answer)
        questions.append(current_question)

    return questions


def write_to_spreadsheet(questions, spreadsheet_url):
    """
    Escreve as perguntas na planilha, evitando duplicatas.

    Args:
        questions: Uma lista de listas representando as perguntas e respostas.
        spreadsheet_url: A URL da planilha.
    """

    # Autoriza o acesso à API do Google Sheets
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SHEETS_CREDENTIALS_FILE, scopes=SHEETS_SCOPES
    )
    client = gspread.authorize(credentials)

    # Abre a planilha e seleciona a primeira aba
    sheet = client.open_by_url(spreadsheet_url).sheet1

    # Obtém as perguntas existentes na planilha
    existing_questions = sheet.col_values(1)[1:]

    # Filtra as perguntas para evitar duplicatas
    new_questions = [
        question for question in questions if question[0] not in existing_questions
    ]

    # Adiciona as novas perguntas à planilha
    if new_questions:
        # Determina o intervalo de células a serem atualizadas
        start_row = len(existing_questions) + 2
        end_row = start_row + len(new_questions) - 1
        update_range = f"A{start_row}:F{end_row}"

        # Atualiza a planilha com as novas perguntas
        sheet.update(update_range, new_questions)
        print(f"{len(new_questions)} novas perguntas adicionadas à planilha.")
    else:
        print("Nenhuma nova pergunta encontrada.")


def monitor_google_docs(document_id, spreadsheet_url, interval=MONITORING_INTERVAL):
    """
    Monitora o Google Docs para alterações e atualiza a planilha.

    Args:
        document_id: O ID do documento do Google Docs.
        spreadsheet_url: A URL da planilha.
        interval: O intervalo de tempo (em segundos) para verificar as alterações.
    """

    last_revision_id = None

    while True:
        try:
            # Constrói o serviço Google Docs
            credentials = service_account.Credentials.from_service_account_file(
                DOCS_CREDENTIALS_FILE, scopes=DOCS_SCOPES
            )
            service = build("docs", "v1", credentials=credentials)

            #  Correção: Utiliza 'service.documents()' para acessar o recurso 'documents'
            document = service.documents().get(documentId=document_id).execute()
            current_revision_id = document["revisionId"]

            # Verifica se houve alterações no documento
            if current_revision_id != last_revision_id:
                print("Mudanças detectadas no Google Docs. Atualizando a planilha...")

                # Extrai as perguntas do documento
                questions = extract_questions_from_doc(document_id)

                # Escreve as perguntas na planilha
                write_to_spreadsheet(questions, spreadsheet_url)

                # Atualiza o ID da última revisão
                last_revision_id = current_revision_id

            # Aguarda o intervalo de tempo especificado
            time.sleep(interval)
        except Exception as e:
            print(f"Erro ao monitorar o Google Docs: {e}")
            time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente


# Inicia o monitoramento quando o script é executado
if __name__ == "__main__":
    monitor_google_docs(DOCUMENT_ID, SPREADSHEET_URL)

