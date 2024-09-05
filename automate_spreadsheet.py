import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import time
import os
import traceback

# Caminhos para os arquivos de credenciais, utilizando caminhos absolutos
# para evitar problemas com diretórios relativos.
SHEETS_CREDENTIALS_FILE = os.path.join(
    os.path.dirname(__file__), "credentials_sheets.json"
)
DOCS_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials_docs.json")

# Escopos de acesso necessários para o Google Sheets e Google Docs.
SHEETS_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
DOCS_SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

# URL da planilha e ID do documento.
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"
DOCUMENT_ID = "1kQU6ElV41Y73Iiu6N1lOcfAoHaaWSNTqmOnOWBhifgg"

# Intervalo de verificação para alterações no Google Docs (em segundos).
MONITORING_INTERVAL = 300


def extract_questions_from_doc(document_id):
    """
    Extrai perguntas e respostas de um documento do Google Docs.

    Args:
        document_id: O ID do documento do Google Docs.

    Returns:
        Uma lista de listas, onde cada sublista representa uma pergunta
        e suas opções de resposta, com a resposta correta no final, ou None em caso de erro.
    """
    try:
        # Carrega as credenciais do Google Docs do arquivo 'credentials_docs.json'.
        credentials = service_account.Credentials.from_service_account_file(
            DOCS_CREDENTIALS_FILE, scopes=DOCS_SCOPES
        )
        # Constrói o serviço da API do Google Docs.
        service = build("docs", "v1", credentials=credentials)
        # Obtém o conteúdo do documento do Google Docs.
        document = service.documents().get(documentId=document_id).execute()
        content = document.get("body").get("content")

        questions = []
        current_question = []
        correct_answer = ""

        # Itera sobre o conteúdo do documento extraindo perguntas e respostas.
        for item in content:
            if "paragraph" in item:
                elements = item.get("paragraph").get("elements")
                text = ""
                for element in elements:
                    if "textRun" in element:
                        text += element["textRun"]["content"]
                text = text.strip()

                # Ignora parágrafos vazios.
                if not text:
                    continue

                # Identifica opções de resposta pelo formato "(a) ...".
                if len(text) > 2 and text[0].islower() and text[1] == ")":
                    current_question.append(text[2:].strip())
                    # A resposta correta está em negrito.
                    if "bold" in elements[0].get("textRun", {}).get("textStyle", {}):
                        correct_answer = text[0]
                else:
                    # Se não for uma opção, é uma nova pergunta.
                    if current_question:
                        current_question.append(correct_answer)
                        questions.append(current_question)
                    current_question = [text]
                    correct_answer = ""

        # Adiciona a última pergunta, se houver.
        if current_question:
            current_question.append(correct_answer)
            questions.append(current_question)

        return questions

    except Exception as e:
        print(f"Erro ao extrair perguntas do Google Docs: {e}")
        traceback.print_exc()
        return None


def write_to_spreadsheet(questions, spreadsheet_url):
    """
    Escreve as perguntas extraídas na planilha do Google Sheets.

    Args:
        questions: Lista de perguntas e respostas extraídas do Google Docs.
        spreadsheet_url: URL da planilha do Google Sheets.
    """
    try:
        # Carrega as credenciais do Google Sheets do arquivo 'credentials_sheets.json'.
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            SHEETS_CREDENTIALS_FILE, scopes=SHEETS_SCOPES
        )
        # Autoriza o acesso à API do Google Sheets.
        client = gspread.authorize(credentials)
        # Abre a planilha pelo URL.
        sheet = client.open_by_url(spreadsheet_url).sheet1
        # Obtém as perguntas existentes na primeira coluna da planilha.
        existing_questions = sheet.col_values(1)[1:]  # Ignora o cabeçalho

        new_questions = []
        # Verifica se há novas perguntas a serem adicionadas,
        # evitando duplicatas.
        for question in questions:
            question_text = question[0].replace("<b>", "").replace("</b>", "")
            if question_text not in existing_questions:
                new_questions.append(question)

        # Adiciona as novas perguntas à planilha.
        if new_questions:
            formatted_questions = []
            for question in new_questions:
                # Emite um aviso se a pergunta tiver menos de 4 opções.
                if len(question) < 5:
                    print(
                        f"Aviso: A pergunta '{question[0]}' tem menos de 4 opções de resposta. Verifique o Google Docs."
                    )
                # Remove tags HTML das perguntas e respostas.
                for i in range(len(question)):
                    question[i] = question[i].replace("<b>", "").replace("</b>", "")
                # Preenche as opções faltantes com strings vazias.
                while len(question) < 6:
                    question.append("")

                formatted_questions.append(question)

            # Define o intervalo de células para inserir as novas perguntas.
            next_row = len(existing_questions) + 2
            update_range = f"A{next_row}:F{next_row + len(formatted_questions) - 1}"

            # Atualiza a planilha com as novas perguntas.
            sheet.update(values=formatted_questions, range_name=update_range)

            print(f"{len(formatted_questions)} novas perguntas adicionadas à planilha.")
        else:
            print("Nenhuma nova pergunta encontrada.")

    except Exception as e:
        print(f"Erro ao escrever na planilha: {e}")
        traceback.print_exc()


def monitor_google_docs(document_id, spreadsheet_url, interval=MONITORING_INTERVAL):
    """
    Monitora o Google Docs para alterações e atualiza a planilha do Google Sheets.

    Args:
        document_id: ID do documento do Google Docs a ser monitorado.
        spreadsheet_url: URL da planilha do Google Sheets a ser atualizada.
        interval: Intervalo de tempo (em segundos) para verificar as alterações.
    """
    last_revision_id = None
    while True:
        try:
            # Obtém as credenciais da conta de serviço para o Google Docs.
            credentials = service_account.Credentials.from_service_account_file(
                DOCS_CREDENTIALS_FILE, scopes=DOCS_SCOPES
            )
            # Cria o serviço da API do Google Docs.
            service = build("docs", "v1", credentials=credentials)
            # Obtém a última revisão do documento.
            document = service.documents().get(documentId=document_id).execute()
            current_revision_id = document["revisionId"]

            # Verifica se houve alterações no documento.
            if current_revision_id != last_revision_id:
                print("Mudanças detectadas no Google Docs. Atualizando a planilha...")
                # Extrai as perguntas do Google Docs.
                questions = extract_questions_from_doc(document_id)
                # Se a extração foi bem-sucedida, escreve as perguntas na planilha.
                if questions is not None:
                    write_to_spreadsheet(questions, spreadsheet_url)
                # Atualiza o ID da última revisão.
                last_revision_id = current_revision_id

            # Aguarda o intervalo definido antes da próxima verificação.
            time.sleep(interval)

        except Exception as e:
            print(f"Erro ao monitorar o Google Docs: {e}")
            traceback.print_exc()
            # Aguarda 1 minuto antes de tentar novamente em caso de erro.
            time.sleep(60)


if __name__ == "__main__":
    monitor_google_docs(DOCUMENT_ID, SPREADSHEET_URL)
