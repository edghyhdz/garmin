from twilio.rest import Client
import os
import logging
import sys

acc_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN_TWILIO')
own_number = os.environ.get('OWN_NUMBER')

class SendMessage(object):
    """

    Sends messages to given phone numbers when an action is flagged
    @param: acc_sid: account sid
    @auth_toke: authorization token
    @phone_list: str: list containing phone numbers to message
    """
    def __init__(self, **kwargs):
        try: 

            needed_kwargs = [
                'acc_sid', 'auth_token', 'phone_list', 'own_number'
                ]

            for key in kwargs:
                if key in 'acc_sid':
                    self.acc_sid = kwargs[key]
                elif key in 'auth_token':
                    self.auth_token = kwargs[key]
                elif key in 'phone_list': 
                    self.phone_list = kwargs[key]
                elif key in 'own_number':
                    self.own_number = kwargs[key]
                else:
                    raise SendMessageException(1)

                idx_pop = needed_kwargs.index(key)

                needed_kwargs.pop(idx_pop)

            # We should have popped out all items
            if needed_kwargs:
                logging.error("Missing kwargs: {}".format(needed_kwargs)) 
                raise SendMessageException(2)
                
            # Have a counter limit for amount of messages to send
            self.message_counter = 0

        except SendMessageException as err:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(err.error_codes[err.msg], error_line))
            return None
    
    def connect_to_client(self):
        """
        Connects to client and returns client method
        """
        try: 
            client = Client(self.acc_sid, self.auth_token)
            return client

        except Exception as err:
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(err, error_line))
            return None
    
    def send_messages(self):
        """
        Sends messages to given numbers in self.phone_list
        """
        client = self.connect_to_client()
        
        try:
            for temp_phone in self.phone_list:
                message = client.messages.create(
                    body='Hello there!',
                    from_='whatsapp:{}'.format(self.own_number),
                    to='whatsapp:{}'.format(temp_phone)
                    )

                logging.info("Sent message, message sid: {}".format(message.sid))
                

        except Exception as err: 
            error_line = sys.exc_info()[-1].tb_lineno
            logging.error("Error: {}. Error line: {}".format(err, error_line))
            return None
    


class SendMessageException(Exception):
    """
    Handles Exceptions for this class
    """

    error_codes = {
        '1': "Not recognized key",
        '2': "Missing kwargs"
    }

    def __init__(self, code):
        self.code = code
        self.msg = str(code)
