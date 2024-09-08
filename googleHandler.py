from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

saf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys', 'docs_credentials.json')

SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/documents'
          ]
SERVICE_ACCOUNT_FILE = saf

