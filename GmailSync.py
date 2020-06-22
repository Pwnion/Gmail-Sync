from time import sleep
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def setup():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Setup new token.pickle
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def last_history_id(service, user_id, start_history_id="1"):
    """List History of all changes to the user's mailbox.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        start_history_id: Only return Histories at or after start_history_id.

    Returns:
        A list of mailbox changes that occurred after the start_history_id.
    """
    try:
        history = (service.users().history().list(userId=user_id,
                                                  startHistoryId=start_history_id,
                                                  fields="nextPageToken, historyId").execute())
        while 'nextPageToken' in history:
            page_token = history['nextPageToken']
            history = (service.users().history().list(userId=user_id,
                                                      startHistoryId=start_history_id,
                                                      fields="nextPageToken, historyId",
                                                      pageToken=page_token).execute())
        return history['historyId']
    except errors.HttpError as error:
        print("An error occurred:", error)


def main(sleep_duration):
    """Fetches mailbox data every sleep_duration second(s)"""
    service = build('gmail', 'v1', credentials=setup())

    history_id = last_history_id(service, "me")
    print(history_id)

    while True:
        sleep(sleep_duration)
        history_id = last_history_id(service, "me", history_id)


if __name__ == '__main__':
    main(2)
