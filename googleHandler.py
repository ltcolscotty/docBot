from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os

import quarterHandler
import robloxHandler
import doc_config


# link to file to clone
file_id = doc_config.file_id
folder_id = doc_config.folder_id

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
def clone_document(file_id, new_title):
    service = drive_service
    copied_file = {"name": new_title, "parents": [folder_id]}
    return service.files().copy(fileId=file_id, body=copied_file).execute()


def file_exists(file_name, folder_id):
    service = drive_service
    query = f"name='{file_name}' and trashed=false and '{folder_id}' in parents"
    results = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    files = results.get("files", [])

    if len(files) > 0:
        print("Files Found")
    else:
        print("Files not found")

    return len(files) > 0


def get_file_id_by_name(file_name, folder_id):
    """
    Should be run in conjunction with file_exists
    """
    query = f"name='{file_name}' and trashed=false and '{folder_id}' in parents"
    service = drive_service

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


async def run_doc_update(dm_count, sdm_count):
    """
    Updates quarterly transparency report

    currently meant to be called in bot.py
    """
    print("Starting document update!")

    cur_quarter_name = quarterHandler.make_file_name()
    print(f"Running: {cur_quarter_name}")

    if not file_exists(drive_service, cur_quarter_name, doc_config.folder_id):
        cloned_doc = clone_document(drive_service, file_id, cur_quarter_name)
        print(f'Cloned document ID: {cloned_doc["id"]}')

    time_info = quarterHandler.get_time_info()
    document_id = get_file_id_by_name(
        drive_service, cur_quarter_name, doc_config.folder_id
    )
    roles = await robloxHandler.get_role_count(doc_config.mod_group)

    # make changes
    print("Updating GMT Counts")
    result = replace_text(document_id, "quarterholder", time_info[0])
    result = replace_text(document_id, "yearholder", str(time_info[1]))
    result = replace_text(document_id, "bomCount", str(roles["Board of Moderation"]))
    result = replace_text(document_id, "admCount", str(roles["Administrator"]))
    result = replace_text(document_id, "supCount", str(roles["Supervisor"]))
    result = replace_text(document_id, "sgmCount", str(roles["Senior Moderator"]))
    result = replace_text(document_id, "gmCount", str(roles["Moderator"]))

    print("Updating DMT Counts")

    result = replace_text(document_id, "sdmCount", str(sdm_count[0]))
    result = replace_text(document_id, "dmCount", str(dm_count[0]))

    print("Finished Update")


def get_file_link(folder_id, file_name):
    service = drive_service
    # Search for the file in the specified folder
    query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
    results = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name, webViewLink)")
        .execute()
    )
    files = results.get("files", [])

    if not files:
        print(f"No file named '{file_name}' found in the specified folder.")
        return None

    # Get the first file that matches (assuming file names are unique in the folder)
    file = files[0]

    # Return the webViewLink
    return file.get("webViewLink")


def find_previous_docs(folder_id):
    service = drive_service
    query = f"'{folder_id}' in parents and trashed = false"
    request = (
        service.files()
        .list(
            q=query,
            spaces="drive",
            fields="files(name, createdTime)",
            orderBy="createdTime desc",
            pageSize=10,
        )
        .execute()
    )
    files = request.get("files", [])

    output_dict = {}

    for file in files:
        file_name = file["name"]
        output_dict[file_name] = get_file_link(service, folder_id, file_name)

    return output_dict


def move_file(file_name, start_folder, destination_folder):
    service = drive_service
    try:
        # Search for the file in the source folder
        query = (
            f"name = '{file_name}' and '{start_folder}' in parents and trashed = false"
        )
        results = (
            service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )
        files = results.get("files", [])

        if not files:
            print(f"File '{file_name}' not found in the specified folder.")
            return None

        file_id = files[0]["id"]

        # Move the file to the new folder
        file = (
            service.files()
            .update(
                fileId=file_id,
                addParents=destination_folder,
                removeParents=start_folder,
                fields="id, parents",
            )
            .execute()
        )

        print(
            f"File '{file_name}' (ID: {file_id}) moved to folder with ID: {destination_folder}"
        )
        return file.get("parents")

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    

def document_search(file_name):
    service = drive_service


def make_announcement(document_id, title="", content=""):
    """
    TODO:
    - add new announcementTitleHolder on a new line in bold
    - add a new announcementHolder in a line below
    """
    replace_text(document_id, "announcementTitleHolder", title)
    replace_text(document_id, "announcementHolder", content)


def check_string_in_doc(document_id, search_string):
    service = docs_service
    # Retrieve the document content
    doc = service.documents().get(documentId=document_id).execute()

    # Extract text from the document
    document_content = doc.get('body').get('content')
    text = ''
    for element in document_content:
        if 'paragraph' in element:
            for paragraph_element in element['paragraph']['elements']:
                if 'textRun' in paragraph_element:
                    text += paragraph_element['textRun']['content']

    # Check if the search string exists in the extracted text
    if search_string in text:
        print(f"The string '{search_string}' was found in the document.")
    else:
        print(f"The string '{search_string}' was not found in the document.")


def search_file_in_folder(folder_id, file_name):
    query = f"'{folder_id}' in parents and name = '{file_name}'"
    service = drive_service
    
    try:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType)'
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print(f"No file named '{file_name}' found in the specified folder.")
            return None
        else:
            print(f"File found: {files[0]['name']} (ID: {files[0]['id']})")
            return files[0]
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None