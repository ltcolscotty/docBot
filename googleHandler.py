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
def clone_document(file_id: str, new_title: str):
    """
    Duplicates document and gives it a new title
    Args:
        - file_id: String - target ID
        - new_title: String - name of new document
    """
    service = drive_service
    copied_file = {"name": new_title, "parents": [folder_id]}
    return service.files().copy(fileId=file_id, body=copied_file).execute()


def file_exists(file_name: str, folder_id: str):
    """
    Checks if file exists in folder
    TODO: Check if this is redundant and can be removed
    Args:
        - file_name: String - name of file
        - folder_id: folder to search
    Returns:
        - boolean: file exists in folder
    """
    service = drive_service
    query = f"name='{file_name}' and trashed=false and '{folder_id}' in parents"
    results = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    files = results.get("files", [])

    if len(files) > 0:
        print(f"Files Found in folder: {folder_id}")
    else:
        print(f"Files not found in folder: {folder_id}")

    return len(files) > 0


def get_file_id_by_name(file_name: str, folder_id: str):
    """
    Should be run in conjunction with file_exists
    Args:
        - file_name: Str
        - folder_id
    Returns:
        - Str: file ID or NoneType
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
def replace_text(document_id: str, old_text: str, new_text: str):
    """
    replaces text in given document ID
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


async def run_doc_update(dm_count: int, sdm_count: int):
    """
    Updates quarterly transparency report

    currently meant to be called in bot.py

    Args:
        - dm_count: int
        - sdm_count: int
    """
    print("Starting document update!")

    cur_quarter_name = quarterHandler.make_file_name()
    print(f"Running: {cur_quarter_name}")

    if not file_exists(cur_quarter_name, doc_config.folder_id):
        cloned_doc = clone_document(file_id, cur_quarter_name)
        print(f'Cloned document ID: {cloned_doc["id"]}')

    time_info = quarterHandler.get_time_info()
    document_id = get_file_id_by_name(cur_quarter_name, doc_config.folder_id)
    roles = await robloxHandler.get_role_count(doc_config.mod_group)

    # make changes
    print("Updating GMT Counts")
    replace_text(document_id, "quarterholder", time_info[0])
    replace_text(document_id, "yearholder", str(time_info[1]))
    replace_text(document_id, "bomCount", str(roles["Board of Moderation"]))
    replace_text(document_id, "admCount", str(roles["Administrator"]))
    replace_text(document_id, "supCount", str(roles["Supervisor"]))
    replace_text(document_id, "sgmCount", str(roles["Senior Moderator"]))
    replace_text(document_id, "gmCount", str(roles["Moderator"]))

    print("Updating DMT Counts")

    replace_text(document_id, "sdmCount", str(sdm_count[0]))
    replace_text(document_id, "dmCount", str(dm_count[0]))

    print("Finished Update")


def get_file_link(folder_id: str, file_name: str):
    """
    Gets file link based on folder_id and file_name
    Args:
        - folder_id: String - target folder for search
        - file_name: String - file name
    Returns:
        - link of file_name file
    """
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


def find_previous_docs(folder_id: str):
    """
    lists out documents in a folder
    Args:
        - folder_id: String - target folder ID
    Returns:
        - dictionary: {document_name, file_link}
    """
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
        output_dict[file_name] = get_file_link(folder_id, file_name)

    return output_dict


def move_file(file_name: str, start_folder: str, destination_folder: str):
    """
    Moves file from start folder to destination folder
    Args:
    - file_name: String - Target file name
    - start_folder: String - source folder ID
    - destination_folder: String - destination folder ID
    """
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


def get_folder_from_docname(file_name: str):
    """
    Returns a folder based on a document name that is given
    Args:
        - file_name: String
    Returns:
        - folder_id: String
    """
    if search_file_in_folder(doc_config.folder_id, file_name) is not None:
        return doc_config.folder_id
    elif search_file_in_folder(doc_config.share_folder_id, file_name) is not None:
        return doc_config.share_folder_id
    else:
        return None


def make_announcement(document_id: str, title: str = "", content: str = ""):
    """
    TODO:
    - add new announcementTitleHolder on a new line in bold
    - add a new announcementHolder in a line below
    """
    replace_text(document_id, "announcementTitleHolder", title)
    replace_text(document_id, "announcementHolder", content)


def check_string_in_doc(document_id: str, search_string: str):
    """
    Looks for a string in a document and returns true or false.
    Args:
    - document_id: String target document ID
    - search_string: target string
    Returns:
    - Boolean: does string exist in the document
    """
    service = docs_service
    # Retrieve the document content
    doc = service.documents().get(documentId=document_id).execute()

    # Extract text from the document
    document_content = doc.get("body").get("content")
    text = ""
    for element in document_content:
        if "paragraph" in element:
            for paragraph_element in element["paragraph"]["elements"]:
                if "textRun" in paragraph_element:
                    text += paragraph_element["textRun"]["content"]

    # Check if the search string exists in the extracted text
    return search_string in text


def search_file_in_folder(folder_id: str, file_name: str):
    """
    looks for a file in a folder
    Args:
        - folder_id: Str
        - file_name: Str
    """
    query = f"'{folder_id}' in parents and name = '{file_name}'"
    service = drive_service

    try:
        results = (
            service.files()
            .list(q=query, spaces="drive", fields="files(id, name, mimeType)")
            .execute()
        )

        files = results.get("files", [])

        if not files:
            print(f"No file named '{file_name}' found in the specified folder.")
            return None
        else:
            print(f"File found: {files[0]['name']} (ID: {files[0]['id']})")
            return files[0]
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
