from tabulate import tabulate
import sys
import os
# os.path.append("~/Desktop/Projects/Garmin_tekst/garmin/")
# from GMAIL.email_fetch import GoogleEmailFetch, GmailExckeption
from GARMIN.garmin import GarminException, GarminFetcher
from TWILIO.send_message import SendMessageException, SendMessage
from GMAIL.email_fetch import GmailException, GoogleEmailFetch

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
from datetime import datetime
matplotlib.use('TkAgg')

# TODO: 
# Add a CONFIG CLASS!                               [ ]
# Add exception class for both classess             [ ]
# Change track points from garmin_link              [ ]
# Make a real main function, as well as plot funct  [ ]
# Make main task more ORGANIZED FAST!               [ ]

distance_covered = [1.5, 5, 10, 15, 21, 40]

try:    
    cred_path = '/home/edgar/Desktop/Projects/credentials_gmail.json'
    token_path = '/home/edgar/Desktop/Projects/token.pickle'
    gmail = GoogleEmailFetch(cred_path=cred_path, token_path=token_path)
    messages, max_time = gmail.get_email_content()
    url_garmin = gmail.complete_link
    
    print(messages[max_time].get('complete_link'))
    url = messages[max_time].get('complete_link')
    session_id = messages[max_time].get('session_id')
    test = GarminFetcher(url=url, session_id=session_id)       
    df = test.fetch_data()

    # Messages part
    acc_sid = os.environ.get('ACCOUNT_SID')
    auth_token = os.environ.get('AUTH_TOKEN_TWILIO')
    own_number = os.environ.get('OWN_NUMBER')
    phone_to_send = os.environ.get("TEST_NUMBER")
    message = SendMessage(acc_sid=acc_sid, auth_token=auth_token, own_number=own_number, phone_list=[phone_to_send])

    fig, ax = plt.subplots(1, 2)

    def animate(i):
        """
        Real time plot of the data bein queried
        Temporary function
        """
        global test
        global distance_covered

        try: 
            df = test.fetch_data()

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
                    print("Popping out: {}".format(dis))
                    print("Distances to go: {}".format(distance_covered))
                    message.send_messages(
                        "Edgar has covered {} km already! Check his race under: {}".format(
                            current_distance, url_garmin))
                    break
                
             # if heart_rate > 80: 
                # message.send_messages("Your heart rate is: {}. Nice!!".format(heart_rate))
                # Stop it from sending more
                # message.message_counter = 10

            ax[0].clear()
            ax[1].clear()
            ax[0].plot(temp_df['timestamp'], temp_df['hb'], color='indianred', linewidth=2)  
            ax[0].tick_params(rotation=90, axis='x')
            ticks = [datetime.strftime(datetime.fromtimestamp(x), '%H:%M:%S') for x in ax[0].get_xticks()]
            ax[0].set_xticklabels(ticks)
            ax[0].grid()

            ax[1].plot(temp_df['timestamp'], temp_df['distance'], color='indianred', linewidth=2)  
            ax[1].tick_params(rotation=90, axis='x')
            ticks = [datetime.strftime(datetime.fromtimestamp(x), '%H:%M:%S') for x in ax[1].get_xticks()]
            ax[1].set_xticklabels(ticks)
            ax[1].grid()


        except Exception as e:
            print(e)
    ani = animation.FuncAnimation(fig, animate, interval=5000)
    plt.show()
    # print(tabulate(df, headers='keys', tablefmt='fancy_grid'))
except Exception as e:
    print(str(e))