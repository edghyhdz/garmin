"""This is the main script to run GarminFetcher class together
with the SendMessage and GoogleEmailFetch classes.

It fetches from gmail link sent by garmin's LiveTrack, where it then starts the
GarminFetcher class to continously fetch details of garmin event.

It uses the SendMessage class that is connected to Twilio, to send messages depending
certain running distances being covered."""

import sys
import os
import logging
from datetime import datetime
from time import sleep
import signal
# Own libraries
from GARMIN.garmin import GarminFetcher
from TWILIO.send_message import SendMessage
from GMAIL.email_fetch import GoogleEmailFetch
from API.api import Events, db

# TODO:
# NEED TO RESTART DB -> MODIFIED TABLE EVENTS       [X]
# Make <event_type> an arg variable for API REQUEST [X]
# Add a CONFIG CLASS!                               [ ]
# Add exception class for both classess             [ ]
# Initialize environment variables from code        [X]
# API Calls to start script                         [X]
# Plotly dashboard                                  [ ]


class MainException(Exception):
    """
    Class to handle exceptions for the main script function
    """
    error_codes = {
        '0': "CRED_PATH_GMAIL",
        '1': "TOKEN_PATH_GMAIL",
        '2': "ACCOUNT_SID",
        '3': "AUTH_TOKEN_TWILIO",
        '4': "OWN_NUMBER",
        '5': "TEST_NUMBER",
        '6': "One script is already running"
    }

    def __init__(self, code):
        self.code = code
        self.msg = str(code)

def main(): # pylint: disable-msg=too-many-locals
    """This is the main script to run GarminFetcher class together
    with the SendMessage and GoogleEmailFetch classes.

    It fetches from gmail link sent by garmin's LiveTrack, where it then starts the
    GarminFetcher class to continously fetch details of garmin event.

    It uses the SendMessage class that is connected to Twilio, to send messages depending
    certain running distances being covered.
    @returns: garmin fetcher
    """

    try:
        # Check if env variables where initialized correctly
        for k, var in enumerate(ENV_VARIABLES):
            if not var:
                logging.error("At least one variable returned None")
                raise MainException(k)

        # Initialize gmail fetch class
        gmail = GoogleEmailFetch(cred_path=CRED_PATH, token_path=TOKEN_PATH)
        # Get email content and most recent garmin email
        messages, max_time = gmail.get_email_content()
        # Get email date
        email_date = datetime.fromtimestamp(max_time/1000).date()
        logging.info("Email date: %s", email_date)

        # While email is not that from today's date do not continue
        delay = 20 # seconds
        while True:
            logging.info("Querying email folder again")
            messages, max_time = gmail.get_email_content()
            email_date = datetime.fromtimestamp(max_time/1000).date()
            logging.info("Email date: %s", email_date)
            if email_date == datetime.now().date():
                logging.info("Found email!")
                break
            sleep(delay)

        # Get url from garmin, to be send with an sms to the users on phone_list list
        url_garmin = gmail.complete_link

        # Get link where json data is fetched
        logging.info(messages[max_time].get('complete_link'))
        url = messages[max_time].get('complete_link')

        # Get session id -> to be used to save csv files with heart bit and distance data
        session_id = messages[max_time].get('session_id')

        # Initilize garminfetcher class
        garmin_fetcher = GarminFetcher(
            url=url,
            session_id=session_id,
            user_id=PUBLIC_USER_ID,
            event_type=EVENT_TYPE
            )

        start_script = garmin_fetcher.check_ongoing_event()

        # Start script only if ongoing event is false
        if not start_script:
            logging.info("Start script: %s", start_script)
            raise MainException(6)

        # Get data (if any)
        garmin_fetcher.fetch_data()

        # Initilaize message class if enable_message is True
        if ENABLE_MESSAGE:
            message = SendMessage(
                acc_sid=ACC_SID,
                auth_token=AUTH_TOKEN,
                own_number=OWN_NUMBER,
                phone_list=[PHONE_TO_SEND]
                )

        return garmin_fetcher

    except MainException as err:
        error_line = sys.exc_info()[-1].tb_lineno
        # Related to started code
        if err.msg == "6":
            event = Events.query.filter_by(session_id=garmin_fetcher.session_id).first()
            session_id_db = event.session_id
            logging.error("Error: %s. Event session id: %s. Error line: %s", *(
                err.error_codes[err.msg], session_id_db, error_line))
        else:
            error_message = "Variable %s was not initialized. Error line: %s"
            logging.error(error_message, *(err.error_codes[err.msg], error_line))

    except Exception as err: # pylint: disable=broad-except
        error_line = sys.exc_info()[-1].tb_lineno
        logging.error("Error: %s. Error line: %s", *(err, error_line))

    except KeyboardInterrupt:
        logging.info("Shuting down app with KeyboardInterrupt")
        event = Events.query.filter_by(session_id=garmin_fetcher.session_id).first()
        event.ongoing_event = False
        event.finished_date = datetime.now()
        db.session.commit()

# Catch linux signal when terminating a proccess with the API
def signal_term_handler(signal, frame):
    """
    Detects whether there was a SIGTERM signal to terminate task
    """
    logging.info('got SIGTERM')
    event = Events.query.filter_by(session_id=GARMIN_FETCHER.session_id).first()
    event.ongoing_event = False
    event.finished_date = datetime.now()
    db.session.commit()
    sys.exit(0)

def keyboard_interrupt_update():
    """
    updates db in case of KeyboardInterrupt
    """
    event = Events.query.filter_by(session_id=GARMIN_FETCHER.session_id).first()
    event.ongoing_event = False
    event.finished_date = datetime.now()
    db.session.commit()

if __name__ == "__main__":
    # Catches kill signal when using API stop_event call
    signal.signal(signal.SIGTERM, signal_term_handler)

    # Check if there are args, else EVENT_TYPE=0
    # Event type 0: Normal, 1: Run, 2: Cycling
    if len(sys.argv) > 1:
        EVENT_TYPE = sys.argv[1]
        logging.info("Passed event type: %s", EVENT_TYPE)
    else:
        EVENT_TYPE = 0

    # Distances to reach and update phonelist via twilio
    DISTANCE_COVERED = [1.5, 5, 10, 15, 21, 40]

    # Env variables ##
    # Gmail
    CRED_PATH = os.environ.get('CRED_PATH_GMAIL')
    TOKEN_PATH = os.environ.get('TOKEN_PATH_GMAIL')

    # Twilio
    ENABLE_MESSAGE = True # Whether messaging class should be initilized or not
    ACC_SID = os.environ.get('ACCOUNT_SID')
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN_TWILIO')
    OWN_NUMBER = os.environ.get('OWN_NUMBER')
    PHONE_TO_SEND = os.environ.get("TEST_NUMBER")

    #DB User ID
    PUBLIC_USER_ID = os.environ.get("DB_USER_ID")

    # Check that all env variables are exported correctly -> none of them should return None
    ENV_VARIABLES = [CRED_PATH, TOKEN_PATH, ACC_SID, AUTH_TOKEN, OWN_NUMBER, PHONE_TO_SEND]

    # Run main script
    GARMIN_FETCHER = main()

    # Keep running
    KEEP_RUNNIG = True
    while KEEP_RUNNIG:
        try:
            GARMIN_FETCHER.fetch_data()
            logging.info("THIS IS THE SESSIONID: %s", GARMIN_FETCHER.session_id)
            sleep(5)
        except KeyboardInterrupt:
            logging.info("Shuting down app with KeyboardInterrupt")
            keyboard_interrupt_update()
            KEEP_RUNNIG = False
