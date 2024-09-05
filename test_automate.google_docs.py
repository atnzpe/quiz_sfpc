import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Substitua pelo caminho correto do seu arquivo
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials_docs.json') 

DOCS_SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH, scopes=DOCS_SCOPES
)
service = build('docs', 'v1', credentials=credentials)

document_id = '1kQU6ElV41Y73Iiu6N1lOcfAoHaaWSNTqmOnOWBhifgg'
document = service.documents().get(documentId=document_id).execute()
print(document.get('title')) 
