"""Real time plotting for data fetched with GarminFetcher"""

import sys
import logging
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib

matplotlib.use('TkAgg')

class AnimateException(Exception):
    """
    Class to handle exceptions for the main script function
    """
    error_codes = {
        '0': "Missing kwarg",
        '1': ''
    }

    def __init__(self, code):
        self.code = code
        self.msg = str(code)

class AnimateFunc(object):
    """
    Testing class to animate graph
    """

    def __init__(self, ax, distance_covered, url_garmin, nb_plots, garmin_fetcher):
        self.garmin_fetcher: object = garmin_fetcher
        self.distance_covered: list = distance_covered
        self.url_garmin: str = url_garmin
        self.nb_plots: int = nb_plots
        self.ax: plt.axes = ax

    def animate(self, i):
        """
        Animate function
        """
        try: 
            df_garmin_data = self.garmin_fetcher.fetch_data()

            if len(df_garmin_data) > 100:
                temp_df = df_garmin_data.tail(300)
            else:
                temp_df = df_garmin_data

            current_distance = temp_df['distance'].iloc[-1]

            idx_pop = None
            for dis in self.distance_covered:
                if dis < current_distance:
                    idx_pop = self.distance_covered.index(dis)
                    self.distance_covered.pop(idx_pop)
                    logging.info("Popping out: %s", dis)
                    logging.info("Distances to go: %s", self.distance_covered)
                    self.garmin_fetcher.send_messages(
                        "Edgar has covered %s km already!\n Check his race under: %s" % (
                            current_distance, self.url_garmin))
                    break

            # Plot both heart bit and distance plots
            for k, concept in zip(range(0, self.nb_plots), ('hb', 'distance')):
                self.ax[k].clear()
                self.ax[k].plot(
                    temp_df['timestamp'],
                    temp_df[concept],
                    color='indianred',
                    linewidth=2
                    )

                self.ax[k].tick_params(rotation=90, axis='x')

                # Transform x ticks (timestamp) into datetime object and then to date string
                ticks = [
                    datetime.strftime(
                        datetime.fromtimestamp(x), '%H:%M:%S'
                    ) for x in self.ax[k].get_xticks()
                ]

                self.ax[k].set_xticklabels(ticks)
                self.ax[k].grid()

        except AnimateException as err:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: %s. Error line: %s", *(err.error_codes[err.msg], error_line))

        except Exception as err: # pylint: disable=broad-except
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: %s. Error line: %s", *(err, error_line))
