import numpy as np
import pandas as pd 
import requests
import sys
import logging
import os
from datetime import datetime

file_name_conf = datetime.strftime(datetime.now(), "log_%Y_%m_%d.log")

logging.basicConfig(
    format='%(levelname)s: %(asctime)s - %(message)s [%(filename)s:%(lineno)s - %(funcName)s()]',
    datefmt='%d-%b-%y %H:%M:%S', 
    level=logging.DEBUG,
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
    def __init__(self, url):
        self.url = url
    
        # TODO: 
        # Other parameters that might be needed                                             [ ]
        # What should this class do beside fetching the data from garmin connect            [ ]
        # Do a separate config class                                                        [ ]
        # Error handling class, improve                                                     [ ]
        # Include method to check whether data downloaded its at it most updated version    [ ]


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
                data_all.append((time, hb))
            df = pd.DataFrame(data_all, columns=['t', 'hb'])

            df['date'] = [datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.000Z") for x in df['t']]
            df['timestamp'] = [x.timestamp() for x in df['date']]
            df = df.sort_values(by='timestamp')

            if df.empty:
                raise GarminException(1)
            else:
                return df

        except GarminException as err:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(err.error_codes[err.msg], error_line))
            return None

        except Exception as e:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(str(e), error_line))
            return None
    
    def check_file(self):
        """
        Checks whether downloaded file is at its most updated version 
        """



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
    url = 'https://livetrack.garmin.com/services/session/98ace7a3-27b2-4198-8077-4e286e63c75f/trackpoints?requestTime=1598423101349&from=1598387200372'
    test = GarminFetcher(url=url)         
    df = test.fetch_data()
    print(df)
