import numpy as np
import pandas as pd 
import requests
import sys
import logging
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
        # Other parameters that might be needed                                     [ ]
        # What should this class do beside fetching the data from garmin connect    [ ]
        # Do a separate config class                                                [ ]
        # Error handling class, improve                                             [ ]


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

        except GarminException as err:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(err.error_codes[err.msg], error_line))
            return None

        except Exception as err:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(err.error_codes[err.msg], error_line))
            return None


class GarminException(Exception):
    """
    Class to handle exceptions
    """
    error_codes = {
        '1': "No data available",
        '2': ""
    }

    def __init__(self, code):
        self.code = code
        self.msg = str(code)


if __name__ == "__main__":
    url = 'https://livetrack.garmin.com/services/session/d6af5bdc-80c9-4055-ada3-0080368795bc/trackpoints?requestTime=1598336514853&from=1598307873965'
    test = GarminFetcher(url=url)         
    df = test.fetch_data()
    print(df)
