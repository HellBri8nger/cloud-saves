from __future__ import print_function
import os.path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

creds = None
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1uX0hX6VXYZB5eZKQ6aGS4zF5jqj0k8ye'
Location = SAVE_LOCATION_HERE

l = 1

def authenticate():
    global creds
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

def create_folder(name, parent_id):
    drive = build('drive', 'v3', credentials=creds)
    folder_metadata = {
        'name': name,
        'parents': [parent_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.files().create(body=folder_metadata, fields='id').execute()
    print(f'Created folder "{name}" with ID: {folder.get("id")}')

def upload_file(file_path, folder_id):
    drive = build('drive', 'v3', credentials=creds)
    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path)
    file = drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'Uploaded file "{file_name}" with ID: {file.get("id")}')

def upload_folder(folder_path, parent_id):
    global l
    folder_name = os.path.basename(folder_path)
    create_folder(folder_name, parent_id)
    folder_id = get_folder_id(folder_name, parent_id)
    if l==1:
        with open("id.txt", 'w') as f:
            f.write(folder_id)

    l+=1
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            upload_file(item_path, folder_id)
        elif os.path.isdir(item_path):
            upload_folder(item_path, folder_id)

def get_folder_id(folder_name, parent_id):
    drive = build('drive', 'v3', credentials=creds)
    query = f"name='{folder_name}' and trashed = false and parents in '{parent_id}' and mimeType = 'application/vnd.google-apps.folder'"
    results = drive.files().list(q=query, fields='files(id)').execute().get('files', [])
    if not results:
        return None
    return results[0]['id']

def deleteprevious():
    authenticate()
    drive = build('drive','v3',credentials=creds)
    try:
        with open('id.txt','r') as f:
            folder_id = f.read()
        drive.files().delete(fileId=folder_id, supportsAllDrives=True).execute()

    except Exception as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

def main():
    #authenticate()
    upload_folder(Location, FOLDER_ID)

if __name__ == '__main__':
    deleteprevious()
    main()
