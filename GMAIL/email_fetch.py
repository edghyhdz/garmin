from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import numpy as np
import pandas as pd
import sys
import base64
from bs4 import BeautifulSoup as bs
import re



import logging
# Some code was taken from the official Gmail API website

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GoogleEmailFetch(object):
    """
    This class will fetch emails from gmail
    """
    def __init__(self, **kwargs):
        try: 
            for key in kwargs:
                if key in 'cred_path':
                    self.cred_path = kwargs[key]
                elif key in 'token_path':
                    self.token_path = kwargs[key]
                else:
                    raise GmailException(1)
        except GmailException as err:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(err.error_codes[err.msg], error_line))
            return None
        
        self.regex_pattern_link = r'session\/(.*)\/token'
        self.garmin_link = 'https://livetrack.garmin.com/services/session/{0}/trackpoints?requestTime={1}&from={2}'

        # TODO: 
        # Add more structure to the Exception class         [ ]
        # Add more CONFIG CLASS!                            [ ]
        # Change track points from garmin_link              [ ]

    def connect(self):
        """
        Connects using credentials or token created
        """

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.cred_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)

        return service
        # Call the Gmail API
        # results = service.users().labels().list(userId='me').execute()
        # labels = results.get('labels', [])
    
    def email_ids(self, label_list=['Label_4725329219109390222']) -> list:
        """
        This method returns emails 
        """
        service = self.connect()
        # messages = service.users().messages()
    
        messages = service.users().messages().list(userId='me', labelIds=label_list,
                                               maxResults=500).execute()

        message_ids = []
        for msg in messages.get('messages'):
            msg_id = msg.get('id')
            message_ids.append(msg_id)


        return message_ids
    
    def get_link(self, mail_body):
        """
        Helper function to work with get_email_content() method
        It gets the link where the race/session from garmin is being broadcasted
        """

        soup = bs(mail_body, 'lxml')
        href = soup.find('a', attrs={'title': 'Follow Me'}).get('href')

        session_id = re.search(self.regex_pattern_link, href).group(1)

        return session_id


    def get_email_content(self):
        """
        Gets email content
        """
        email_ids = self.email_ids()
        service = self.connect()
        messages = service.users().messages()

        items_email = {}
        for id_mail in email_ids: 
            temp_message = messages.get(userId='me', id=id_mail, format='full').execute()
            content = temp_message['payload']['body']['data']
            mail_body = base64.urlsafe_b64decode(content).decode('utf-8')
            arrival_date = temp_message.get('internalDate')
            arrival_date = int(arrival_date)/1000

            # Get with soup or so the link we need
            link = self.get_link(mail_body)
            items_email[arrival_date] = link

        return items_email

    
    def get_labels(self):
        """
        Gets labels from all filters on gmail
        """

        service = self.connect()
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        return labels
        
class GmailException(Exception):
    """
    Class to handle exceptions from GarminFetcher class
    """
    error_codes = {
        '1': "Not recognized key",
        '2': ""
    }

    def __init__(self, code):
        self.code = code
        self.msg = str(code)


if __name__ == "__main__":
    cred_path = '/home/edgar/Desktop/Projects/credentials_gmail.json'
    token_path = '/home/edgar/Desktop/Projects/token.pickle'
    gmail = GoogleEmailFetch(cred_path=cred_path, token_path=token_path)
    messages = gmail.get_email_content()
    print(messages)