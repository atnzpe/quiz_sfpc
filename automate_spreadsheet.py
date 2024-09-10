# Importa as bibliotecas necessárias
import gspread  # Interage com o Google Sheets
from oauth2client.service_account import ServiceAccountCredentials  # Autenticação com conta de serviço
from googleapiclient.discovery import build  # Constrói serviços da API do Google
from google.oauth2 import service_account  # Autenticação OAuth 2.0
import time  # Pausas na execução
import os  # Interação com o sistema operacional
import traceback  # Rastreamento de exceções (erros)

# Define as constantes para os arquivos de credenciais
# Utiliza os.path.join para construir caminhos absolutos, tornando o código mais robusto
SHEETS_CREDENTIALS_FILE = os.path.join(
    os.path.dirname(__file__), "credentials_sheets.json"
)  # Caminho para o arquivo de credenciais do Google Sheets
DOCS_CREDENTIALS_FILE = os.path.join(
    os.path.dirname(__file__), "credentials_docs.json"
)  # Caminho para o arquivo de credenciais do Google Docs

# Define os escopos de acesso para o Google Sheets e Google Docs
# Especifica as permissões que o aplicativo precisa para interagir com as APIs
SHEETS_SCOPES = [
    "https://spreadsheets.google.com/feeds",  # Acesso aos dados da planilha
    "https://www.googleapis.com/auth/drive",  # Acesso ao Google Drive (para abrir a planilha)
]
DOCS_SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",  # Acesso de leitura ao Google Docs
    "https://www.googleapis.com/auth/drive.readonly",  # Acesso de leitura ao Google Drive
]

# Define a URL da planilha e o ID do documento
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Qg4BoRVHHniWdfibKovZr1x3ZuYHZ9pG9mmhNdZFmWM/edit?usp=sharing"  # URL da planilha
DOCUMENT_ID = "1kQU6ElV41Y73Iiu6N1lOcfAoHaaWSNTqmOnOWBhifgg"  # ID do documento do Google Docs

# Define o intervalo de verificação para alterações no Google Docs (em segundos)
MONITORING_INTERVAL = 300  # 5 minutos


# Define a função para extrair as perguntas do Google Docs
def extract_questions_from_doc(document_id: str) -> list:
    """
    Extrai perguntas e respostas de um documento do Google Docs.

    Args:
        document_id (str): O ID do documento do Google Docs.

    Returns:
        list: Uma lista de listas, onde cada sublista representa uma pergunta
              e suas opções de resposta (incluindo a resposta correta),
              ou None em caso de erro.
    """
    try:
        # Carrega as credenciais da conta de serviço a partir do arquivo JSON
        credentials = service_account.Credentials.from_service_account_file(
            DOCS_CREDENTIALS_FILE, scopes=DOCS_SCOPES
        )

        # Constrói o serviço da API do Google Docs usando as credenciais
        service = build("docs", "v1", credentials=credentials)

        # Obtém o conteúdo do documento usando a API do Google Docs
        document = service.documents().get(documentId=document_id).execute()
        content = document.get("body").get("content")

        questions = []  # Inicializa a lista para armazenar as perguntas
        current_question = []  # Lista temporária para a pergunta atual
        correct_answer = ""  # Variável para armazenar a resposta correta

        # Itera sobre os elementos de conteúdo do documento
        for item in content:
            # Verifica se o elemento é um parágrafo
            if "paragraph" in item:
                elements = item.get("paragraph").get(
                    "elements"
                )  # Obtém os elementos do parágrafo
                text = "".join(
                    element["textRun"]["content"]
                    for element in elements
                    if "textRun" in element
                ).strip()  # Extrai o texto do parágrafo, removendo espaços em branco

                # Se o texto estiver vazio, continue para o próximo elemento
                if not text:
                    continue

                # Verifica se o texto corresponde a uma opção de resposta (formato "(a) ...")
                if len(text) > 2 and text[0].islower() and text[1] == ")":
                    current_question.append(
                        text[2:].strip()
                    )  # Adiciona a opção de resposta à pergunta atual

                    # Verifica se a opção de resposta está em negrito, indicando a resposta correta
                    if "bold" in elements[0].get("textRun", {}).get("textStyle", {}):
                        correct_answer = text[
                            0
                        ]  # Define a resposta correta com base na formatação em negrito
                else:
                    # Se o texto não for uma opção de resposta, significa que é uma nova pergunta
                    if current_question:
                        # Se já houver uma pergunta sendo processada, adiciona a resposta correta e a pergunta à lista de perguntas
                        current_question.append(correct_answer)
                        questions.append(current_question)
                    # Inicia uma nova pergunta com o texto atual
                    current_question = [text]
                    correct_answer = ""  # Reinicia a resposta correta

        # Adiciona a última pergunta à lista, se houver
        if current_question:
            current_question.append(correct_answer)
            questions.append(current_question)

        return questions  # Retorna a lista de perguntas extraídas

    except Exception as e:
        # Em caso de erro, imprime uma mensagem de erro e o traceback
        print(f"Erro ao extrair perguntas do Google Docs: {e}")
        traceback.print_exc()
        return None  # Retorna None para indicar que ocorreu um erro


# Define a função para escrever as perguntas na planilha do Google Sheets
def write_to_spreadsheet(questions: list, spreadsheet_url: str):
    """
    Escreve as perguntas extraídas na planilha do Google Sheets.

    Args:
        questions (list): Lista de perguntas e respostas extraídas do Google Docs.
        spreadsheet_url (str): URL da planilha do Google Sheets.
    """
    try:
        # Carrega as credenciais da conta de serviço a partir do arquivo JSON
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            SHEETS_CREDENTIALS_FILE, scopes=SHEETS_SCOPES
        )
        # Autoriza o acesso à API do Google Sheets usando as credenciais
        client = gspread.authorize(credentials)
        # Abre a planilha especificada pela URL
        sheet = client.open_by_url(spreadsheet_url).sheet1

        # Obtém os valores da primeira coluna da planilha (onde estão as perguntas existentes)
        existing_questions = sheet.col_values(1)[
            1:
        ]  # Ignora a primeira linha (cabeçalho)

        new_questions = []  # Lista para armazenar as novas perguntas
        # Itera sobre as perguntas extraídas do Google Docs
        for question in questions:
            question_text = question[0].replace("<b>", "").replace(
                "</b>", ""
            )  # Remove as tags HTML da pergunta
            # Verifica se a pergunta já existe na planilha
            if question_text not in existing_questions:
                new_questions.append(
                    question
                )  # Adiciona a pergunta à lista de novas perguntas

        # Se houver novas perguntas a serem adicionadas
        if new_questions:
            formatted_questions = (
                []
            )  # Lista para armazenar as perguntas formatadas para a planilha
            # Itera sobre as novas perguntas
            for question in new_questions:
                # Verifica se a pergunta tem pelo menos 4 opções de resposta
                if len(question) < 5:
                    # Se a pergunta tiver menos de 4 opções de resposta, imprime um aviso
                    print(
                        f"Aviso: A pergunta '{question[0]}' tem menos de 4 opções de resposta. Verifique o Google Docs."
                    )

                # Remove as tags HTML das perguntas e respostas
                question = [
                    item.replace("<b>", "").replace("</b>", "") for item in question
                ]
                # Completa a pergunta com células vazias para garantir que tenha 6 colunas
                question.extend([""] * (6 - len(question)))
                # Adiciona a pergunta formatada à lista
                formatted_questions.append(question)

            # Define a linha a partir da qual as novas perguntas serão adicionadas
            next_row = len(existing_questions) + 2
            # Define o intervalo de células a serem atualizadas na planilha
            update_range = f"A{next_row}:F{next_row + len(formatted_questions) - 1}"
            # Atualiza a planilha com as novas perguntas formatadas
            sheet.update(values=formatted_questions, range_name=update_range)

            # Imprime uma mensagem informando quantas perguntas foram adicionadas
            print(f"{len(formatted_questions)} novas perguntas adicionadas à planilha.")
        else:
            # Se não houver novas perguntas, imprime uma mensagem informando
            print("Nenhuma nova pergunta encontrada.")

    except Exception as e:
        # Em caso de erro, imprime uma mensagem de erro e o traceback
        print(f"Erro ao escrever na planilha: {e}")
        traceback.print_exc()


# Define a função para monitorar o Google Docs por alterações
def monitor_google_docs(
    document_id: str, spreadsheet_url: str, interval: int = MONITORING_INTERVAL
):
    """
    Monitora o Google Docs para alterações e atualiza a planilha do Google Sheets.

    Args:
        document_id (str): ID do documento do Google Docs a ser monitorado.
        spreadsheet_url (str): URL da planilha do Google Sheets a ser atualizada.
        interval (int): Intervalo de tempo (em segundos) para verificar alterações.
    """
    # Inicializa a variável para armazenar o ID da última revisão
    last_revision_id = None
    # Loop infinito para monitorar o documento continuamente
    while True:
        try:
            # Carrega as credenciais da conta de serviço a partir do arquivo JSON
            credentials = service_account.Credentials.from_service_account_file(
                DOCS_CREDENTIALS_FILE, scopes=DOCS_SCOPES
            )
            # Constrói o serviço da API do Google Docs usando as credenciais
            service = build("docs", "v1", credentials=credentials)
            # Obtém o documento do Google Docs
            document = service.documents().get(documentId=document_id).execute()
            # Obtém o ID da revisão atual do documento
            current_revision_id = document["revisionId"]

            # Verifica se o ID da revisão atual é diferente do ID da última revisão
            if current_revision_id != last_revision_id:
                # Se o ID da revisão for diferente, significa que houve alterações no documento
                print(
                    "Mudanças detectadas no Google Docs. Atualizando a planilha..."
                )  # Imprime uma mensagem informando que o documento foi atualizado
                # Extrai as perguntas do Google Docs usando a função extract_questions_from_doc()
                questions = extract_questions_from_doc(document_id)
                # Se a extração das perguntas for bem-sucedida
                if questions is not None:
                    # Escreve as perguntas na planilha do Google Sheets usando a função write_to_spreadsheet()
                    write_to_spreadsheet(questions, spreadsheet_url)
                # Atualiza o ID da última revisão para o ID da revisão atual
                last_revision_id = current_revision_id

            # Pausa a execução por um intervalo de tempo definido pelo parâmetro 'interval'
            time.sleep(interval)

        except Exception as e:
            # Em caso de erro, imprime uma mensagem de erro e o traceback
            print(f"Erro ao monitorar o Google Docs: {e}")
            traceback.print_exc()
            # Pausa a execução por 60 segundos (1 minuto) antes de tentar novamente
            time.sleep(60)


# Verifica se o script está sendo executado como principal
if __name__ == "__main__":
    # Se o script estiver sendo executado como principal, chama a função monitor_google_docs()
    # Passa o ID do documento, a URL da planilha e o intervalo de monitoramento como argumentos
    monitor_google_docs(DOCUMENT_ID, SPREADSHEET_URL)
