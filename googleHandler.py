from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

import quarterHandler
from doc_config import file_id
from doc_config import folder_id

# link to file to clone
file_id = file_id
folder_id = folder_id

# Set up Google API stuff
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


# Define functions
def clone_document(service, file_id, new_title):
    copied_file = {"name": new_title, "parents": [folder_id]}
    return service.files().copy(fileId=file_id, body=copied_file).execute()


def file_exists(service, file_name):
    query = f"name='{file_name}' and trashed=false"
    results = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    files = results.get("files", [])
    return len(files) > 0


def get_file_id_by_name(service, file_name):
    """
    Should be run in conjunction with file_exists
    """
    query = f"name='{file_name}' and trashed=false"

    try:
        results = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="files(id, name)",
                pageSize=1,  # Limit to 1 result
            )
            .execute()
        )

        files = results.get("files", [])

        if not files:
            print(f"No file found with name: {file_name}")
            return None
        else:
            return files[0]["id"]

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


# Docs service functions
def replace_text(document_id, old_text: str, new_text: str):
    """
    Args:
        - document_id: String
        - old_text: String
        - new_text: String

    Returns:
        - result: batchUpdate
    """
    requests = [
        {
            "replaceAllText": {
                "containsText": {"text": old_text, "matchCase": True},
                "replaceText": new_text,
            }
        }
    ]
    result = (
        docs_service.documents()
        .batchUpdate(documentId=document_id, body={"requests": requests})
        .execute()
    )
    return result


cur_quarter_name = quarterHandler.make_file_name()


if not file_exists(drive_service, cur_quarter_name):
    cloned_doc = clone_document(drive_service, file_id, cur_quarter_name)
    print(f'Cloned document ID: {cloned_doc["id"]}')

time_info = quarterHandler.get_time_info()
document_id = get_file_id_by_name(drive_service, cur_quarter_name)

# make changes
result = replace_text(document_id, "quarterholder", time_info[0])
result = replace_text(document_id, "yearholder", str(time_info[1]))
