from tabulate import tabulate
import sys
import os
import logging
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
from datetime import datetime

# Own libraries
from GARMIN.garmin import GarminException, GarminFetcher
from TWILIO.send_message import SendMessageException, SendMessage
from GMAIL.email_fetch import GmailException, GoogleEmailFetch

matplotlib.use('TkAgg')

# TODO: 
# Add a CONFIG CLASS!                               [ ]
# Add exception class for both classess             [ ]
# Initialize environment variables from code        [ ]
# API Calls to start script                         [ ]
# Plotly dashboard                                  [ ]

# Distances to reach and update phonelist via twilio
distance_covered = [1.5, 5, 10, 15, 21, 40]

# Env variables ##
# Gmail
cred_path = os.environ.get('CRED_PATH_GMAIL')
token_path = os.environ.get('TOKEN_PATH_GMAIL')

# Twilio
acc_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN_TWILIO')
own_number = os.environ.get('OWN_NUMBER')
phone_to_send = os.environ.get("TEST_NUMBER")

#DB User ID
public_user_id = os.environ.get("DB_USER_ID")

# Check that all env variables are exported correctly -> none of them should return None
env_variables = [cred_path, token_path, acc_sid, auth_token, own_number, phone_to_send]

class EnvVarException(Exception):
    """
    Class to handle exceptions for the Main function
    """
    error_codes = {
        '0': "CRED_PATH_GMAIL",
        '1': "TOKEN_PATH_GMAIL",
        '2': "ACCOUNT_SID",
        '3': "AUTH_TOKEN_TWILIO",
        '4': "OWN_NUMBER",
        '5': "TEST_NUMBER",
    }

    def __init__(self, code):
        self.code = code
        self.msg = str(code)

try:   

    for k, var in enumerate(env_variables):
        if not var:
            logging.error("At least one variable returned None")
            raise EnvVarException(k)

    # Initialize gmail fetch class
    gmail = GoogleEmailFetch(cred_path=cred_path, token_path=token_path)
    # Get email content and most recent garmin email
    messages, max_time = gmail.get_email_content()
    # Get email date 
    email_date = datetime.fromtimestamp(max_time/1000).date()
    logging.info("Email date: {}".format(email_date))

    # While email is not that from today's date do not continue
    # delay = 60 # seconds
    # while True:
    #     logging.info("Querying email folder again")
    #     messages, max_time = gmail.get_email_content()
    #     email_date = datetime.fromtimestamp(max_time/1000).date()
    #     logging.info("Email date: {}".format(email_date))
    #     if email_date == datetime.now().date():
    #         logging.info("Found email!")
    #         break
    #     sleep(delay)

    # Get url from garmin, to be send with an sms to the users on phone_list list
    url_garmin = gmail.complete_link

    # Get link where json data is fetched
    logging.info(messages[max_time].get('complete_link'))
    url = messages[max_time].get('complete_link')

    # Get session id -> to be used to save csv files with heart bit and distance data
    session_id = messages[max_time].get('session_id')

    # Initilize garminfetcher class
    garmin_fetcher = GarminFetcher(url=url, session_id=session_id, user_id=public_user_id) 

    # Get data (if any)      
    df = garmin_fetcher.fetch_data()

    # Initilaize message class
    message = SendMessage(acc_sid=acc_sid, auth_token=auth_token, own_number=own_number, phone_list=[phone_to_send])

    # Initialize figure to plot real time
    nb_plots = 2
    fig, ax = plt.subplots(nb_plots, 1, figsize=(15, 10), sharex=True)

    # Function to animate realtime plot
    def animate(i, nb_plots=nb_plots):
        """
        Real time plot of the data bein queried
        Temporary function
        """
        global garmin_fetcher
        global distance_covered

        try: 
            df = garmin_fetcher.fetch_data()

            if len(df) > 100: 
                temp_df = df.tail(300)
            else:
                temp_df = df
            
            heart_rate = temp_df['hb'].iloc[-1]
            current_distance = temp_df['distance'].iloc[-1]
            
            idx_pop = None
            for dis in distance_covered:
                if dis < current_distance:
                    idx_pop = distance_covered.index(dis)
                    distance_covered.pop(idx_pop)
                    logging.info("Popping out: {}".format(dis))
                    logging.info("Distances to go: {}".format(distance_covered))
                    message.send_messages(
                        "Edgar has covered {} km already!\n Check his race under: {}".format(
                            current_distance, url_garmin))
                    break
                
             # if heart_rate > 80: 
                # message.send_messages("Your heart rate is: {}. Nice!!".format(heart_rate))
                # Stop it from sending more
                # message.message_counter = 10

            for k, concept in zip(range(0, nb_plots), ('hb', 'distance')):
                ax[k].clear()
                ax[k].plot(temp_df['timestamp'], temp_df[concept], color='indianred', linewidth=2)  
                ax[k].tick_params(rotation=90, axis='x')
                ticks = [datetime.strftime(datetime.fromtimestamp(x), '%H:%M:%S') for x in ax[k].get_xticks()]
                ax[k].set_xticklabels(ticks)
                ax[k].grid()
            
        except Exception as e:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(e, error_line))

    ani = animation.FuncAnimation(fig, animate, interval=5000)
    plt.show()

except EnvVarException as e:
    error_line = sys.exc_info()[-1].tb_lineno
    logging.error("Variable  <{}> was not initilized. Error line: {}".format(e.error_codes[e.msg], error_line))

except Exception as e:
    error_line = sys.exc_info()[-1].tb_lineno
    logging.error("Error: {}. Error line: {}".format(e, error_line))