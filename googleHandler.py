from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

from quarterHandler import make_file_name
from doc_config import file_id
from doc_config import folder_id

# link to file to clone
file_id = file_id
folder_id = folder_id

SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "keys", "xina_service.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=credentials)
docs_service = build("docs", "v1", credentials=credentials)


def clone_document(service, file_id, new_title):
    copied_file = {"name": new_title, 'parents': [folder_id]}
    return service.files().copy(fileId=file_id, body=copied_file).execute()


def file_exists(service, file_name):
    query = f"name='{file_name}' and trashed=false"
    results = service.files().list(q=query, 
                                   spaces='drive',
                                   fields='files(id, name)').execute()
    files = results.get('files', [])
    return len(files) > 0


cur_quarter_name = make_file_name()
cloned_doc = clone_document(drive_service, file_id, cur_quarter_name)
print(f'Cloned document ID: {cloned_doc["id"]}')
