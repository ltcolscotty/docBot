from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

from quarterHandler import get_time_info

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
    copied_file = {"name": new_title, 'parents': ['1TLZ7-Sbq5FMtu5d5M6WOXJd6YRPVqpHc']}
    return service.files().copy(fileId=file_id, body=copied_file).execute()


def make_file_name():
    date_list = get_time_info()
    return f"BM Transparency Report: {date_list[0]} Quarter {date_list[1]}"


file_id = "1IQINeVut1mcGqyufKICer3y5ZWoY3MIJLnlnB3FSDXU"
new_title = make_file_name()
cloned_doc = clone_document(drive_service, file_id, new_title)
print(f'Cloned document ID: {cloned_doc["id"]}')
