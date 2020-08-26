from tabulate import tabulate
import sys
from GMAIL.email_fetch import GoogleEmailFetch, GmailException
from GARMIN.garmin import GarminException, GarminFetcher
import os

try:    
    cred_path = '/home/edgar/Desktop/Projects/credentials_gmail.json'
    token_path = '/home/edgar/Desktop/Projects/token.pickle'
    gmail = GoogleEmailFetch(cred_path=cred_path, token_path=token_path)
    messages, max_time = gmail.get_email_content()

    print(messages[max_time].get('complete_link'))
    url = messages[max_time].get('complete_link')
    session_id = messages[max_time].get('session_id')
    # url = 'https://livetrack.garmin.com/services/session/98ace7a3-27b2-4198-8077-4e286e63c75f/trackpoints?requestTime=1598423101349&from=1598387200372'
    test = GarminFetcher(url=url, session_id=session_id)       
    # test.df_full_path = os.path.join(test.df_path, "{}.csv".format(session_id))
    df = test.fetch_data()
    # print(tabulate(df, headers='keys', tablefmt='fancy_grid'))
except Exception as e:
    print(str(e))