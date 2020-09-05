import numpy as np
import pandas as pd 
import requests
import sys
import logging
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib

# Own libraries
from API.api import *

matplotlib.use('TkAgg')

now = datetime.strftime(datetime.now(), "%Y_%m_%d")
file_name_conf = "log_{}.log".format(now)

logging.basicConfig(
    format='%(levelname)s: %(asctime)s - %(message)s [%(filename)s:%(lineno)s - %(funcName)s()]',
    datefmt='%d-%b-%y %H:%M:%S', 
    level=logging.INFO,
    handlers=[
        logging.FileHandler(file_name_conf),
        logging.StreamHandler()
    ]
)


class GarminFetcher(object):
    """
    From a given url, it will fetch the data from LiveTrack from garmin
    The url will be obtained when the activity starts
    """
    def __init__(self, url, session_id, user_id, event_type):
        self.event_type: int = event_type
        self.user_id: str = user_id
        self.session_id: str = session_id
        self.start_script: bool = True
        self.url: str = url
        self.df: pd.DataFrame = pd.DataFrame()
        self.df_path: str = './'
        self.df_name: str = "{}_{}_.csv".format(session_id, now)
        self.df_full_path: str = os.path.join(self.df_path, self.df_name)
        self.json_name: str = "{}_{}_.json".format(session_id, now)
        self.json_full_path: str = os.path.join(self.df_path, self.json_name)
        self.current_row_length: int = 0
        self.data: list = None

        # TODO: 
        # Other parameters that might be needed                                             [ ]
        # What should this class do beside fetching the data from garmin connect            [ ]
        # Do a separate config class                                                        [ ]
        # Error handling class, improve                                                     [ ]
        # Include method to check whether data downloaded its at it most updated version    [ ]
        # Data frame name should include url identifier (more than one even/day)            [ ]
        # db zu tun stuff, get user id depending on who send request?                       [X]
        # Add possibility to run with or without API request                                [X]

    def fetch_data(self):
        """
        This method will fetch the data from a given url and further process it
        @param: self.url: url to fetch data from garmin
        @return: data frame containing data already processed
        """
        
        try: 
            res = requests.get(self.url)
            data = res.json()

            data_all = []
            for item in data.get('trackPoints'):
                time = item.get('dateTime')
                hb = item.get('fitnessPointData').get('heartRateBeatsPerMin')
                distance = item.get('fitnessPointData').get('distanceMeters')
                try: 
                    distance = float(distance)/1000
                except Exception as e:
                    distance = 0
                    
                data_all.append((time, hb, distance))
            df = pd.DataFrame(data_all, columns=['t', 'hb', 'distance'])

            df['date'] = [datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.000Z") for x in df['t']]
            df['timestamp'] = [x.timestamp() for x in df['date']]
            self.df = df.sort_values(by='timestamp')

            # To be saved as rawdata
            self.data = data

            if self.df.empty:
                raise GarminException(1)
            else:
                self.check_file()
                return self.df

        except GarminException as err:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(err.error_codes[err.msg], error_line))
            return None

        except Exception as e:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(str(e), error_line))
            return None
    
    def check_file(self) -> tuple:
        """
        Checks whether downloaded file is at its most updated version 
        """
        file_exists = os.path.exists(self.df_full_path)
        saved_file = False
        
        if file_exists: 
            temp_df = pd.read_csv(self.df_full_path, index_col=0)
            self.current_row_length = len(temp_df)
            logging.info("Current size: {}".format(self.current_row_length))
            logging.info("New size: {}".format(len(self.df)))
            if len(self.df) > self.current_row_length: 
                # Save file if newest queried data 
                # has more records than preivous one
                self.save_file()
                saved_file = True
            else:
                saved_file = False
                # Overwrite with most updated df with one saved on t - 1 
                self.df = temp_df
                logging.info("Did not save file. Taking previous df version as current one")
        else: 
            self.save_file()
            logging.info("Created file: {} from scratch".format(self.df_full_path))
        return saved_file

    def save_file(self):
        """
        Saves file with a given name 
        """
        
        self.df.to_csv(self.df_full_path)
        logging.info("Saved file: {}".format(self.df_full_path))

        with open(self.json_full_path, 'w') as file:
            json.dump(self.data, file)
        logging.info("Saved json file: {}".format(self.df_full_path))
        
        event = Events.query.filter_by(session_id=self.session_id).first()

        # Create new record in events table
        if not event:
            starting_date = self.df['date'].tolist()[-1]
            new_event = Events(
                user_id=self.user_id, 
                session_id=self.session_id,
                ongoing_event=True, 
                data_path=self.df_full_path,
                event_type=self.event_type,
                starting_date=starting_date)

            db.session.add(new_event)
            db.session.commit()
            logging.info("Commited to db, saved path")
        else:
            event.ongoing_event = True
            db.session.commit()
    
    def check_ongoing_event(self):
        """
        Checks whether there is an ongoing event recorded on the DB
        """
        is_ongoing = None
        event = Events.query.filter_by(session_id=self.session_id).first() 

        if event:
            is_ongoing = event.ongoing_event

        # If it's ongoing then do not start script
        # If its not ongoing but event exists then start script
        if is_ongoing:
            self.start_script = False
        else:
            self.start_script = True

        return self.start_script

class GarminException(Exception):
    """
    Class to handle exceptions from GarminFetcher class
    """
    error_codes = {
        '1': "No data available",
        '2': ""
    }

    def __init__(self, code):
        self.code = code
        self.msg = str(code)


if __name__ == "__main__":
    from tabulate import tabulate
    import sys
    url = 'garmin_url'
    test = GarminFetcher(url=url, session_id='test')         
    df = test.fetch_data()
