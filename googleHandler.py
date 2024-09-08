from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

from quarterHandler import get_time_info
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


def make_file_name():
    date_list = get_time_info()
    return f"BM Transparency Report: {date_list[0]} Quarter {date_list[1]}"


new_title = make_file_name()
cloned_doc = clone_document(drive_service, file_id, new_title)
print(f'Cloned document ID: {cloned_doc["id"]}')
