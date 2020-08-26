from tabulate import tabulate
import sys
from GMAIL.email_fetch import GoogleEmailFetch, GmailException
from GARMIN.garmin import GarminException, GarminFetcher
import os

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

try:    
    cred_path = '/home/edgar/Desktop/Projects/credentials_gmail.json'
    token_path = '/home/edgar/Desktop/Projects/token.pickle'
    gmail = GoogleEmailFetch(cred_path=cred_path, token_path=token_path)
    messages, max_time = gmail.get_email_content()

    print(messages[max_time].get('complete_link'))
    url = messages[max_time].get('complete_link')
    session_id = messages[max_time].get('session_id')
    test = GarminFetcher(url=url, session_id=session_id)       
    df = test.fetch_data()

    fig, ax = plt.subplots(1, 1)

    def animate(i):
        """
        Real time plot of the data bein queried
        """
        global test

        df = test.fetch_data()

        if len(df) > 100: 
            temp_df = df.tail(100)
        else:
            temp_df = df
        
        ax.clear()
        ax.plot(temp_df['timestamp'], temp_df['hb'], color='indianred', linewidth=2)  
        ax.tick_params(rotation=90, axis='x')
        ticks = [datetime.strftime(datetime.fromtimestamp(x), '%H:%M:%S') for x in ax.get_xticks()]
        ax.set_xticklabels(ticks)
        ax.grid() 

    ani = animation.FuncAnimation(fig, animate, interval=5000)
    plt.show()
    # print(tabulate(df, headers='keys', tablefmt='fancy_grid'))
except Exception as e:
    print(str(e))