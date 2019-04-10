"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages reservations for hotel rooms and car rentals.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'BookTrip' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
from __future__ import print_function

import json
import datetime
import time
import os
import dateutil.parser
import logging
from botocore.vendored import requests
import sys
import urllib

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

"""
# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on https://www.yelp.com/developers/v3/manage_app
"""
# Call the external API
API_KEY= "SrHaKm69SIfHIZXjD_M9GJMrNUfoqpHhT508oRRFnM18UbSEycvEcOc4EoYJzyUGy2fCqrVXwO_cRLeAei_qellDKnbY5MtcOXbETW_FgyXdLUUSnoDo8ILiysiKXHYx" 

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.


# Defaults for our simple example.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3

def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """
    try:
        return func()
    except KeyError:
        return None



def isvalid_city(city):
    valid_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland', 'manhattan', 'queens', 'brooklyn', 'flushing']
    return city.lower() in valid_cities


def isvalid_cuisine(cuisine):
	valid_cuisines = ['chinese', 'japanese', 'korean', 'spanish', 'american', 'bbq', 'steakhouse', 'bar', 'mexican', 'indian']
	return cuisine.lower() in valid_cuisines


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False



def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }



def validate_requirement(slots):
    location = try_ex(lambda: slots['Location'])
    cuisine = try_ex(lambda: slots['cuisine'])
    dining_date = try_ex(lambda: slots['dining_date'])

    if location and not isvalid_city(location):
        return build_validation_result(
            False,
            'location',
            'We currently do not support {} as a valid destination.  Can please you try a different city?'.format(location)
        )

    if cuisine and not isvalid_cuisine(cuisine):
        return build_validation_result(
            False,
            'cuisine',
            'We currently do not support {} as a valid cuisine.  Can you please try a different cuisine?'.format(cuisine)
        ) 

    if dining_date:
        if not isvalid_date(dining_date):
            return build_validation_result(False, 'dining_date', 'I did not understand your date.  When would you like to have dinner?')
        if datetime.datetime.strptime(dining_date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'dining_date', 'Reservations must be scheduled at least one day in advance.  Can you try a different date?')

    return {'isValid': True}


""" --- Functions that control the bot's behavior --- """


def suggest_dining(intent_request):
    """
    Performs dialog management and fulfillment for suggest a dinner.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """

    location = try_ex(lambda: intent_request['currentIntent']['slots']['location'])
    cuisine = try_ex(lambda: intent_request['currentIntent']['slots']['cuisine'])
    number_people = try_ex(lambda: intent_request['currentIntent']['slots']['number_people'])
    dining_date = try_ex(lambda: intent_request['currentIntent']['slots']['dining_date'])
    dating_time = try_ex(lambda: intent_request['currentIntent']['slots']['dating_time'])
    
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # Load confirmation history and track the current reservation.
    suggestion = json.dumps({
        'location': location,
        'cuisine': cuisine,
        'number_people': number_people,
        'dining_date': dining_date,
        'dating_time': dating_time
    })

    session_attributes['suggestion'] = suggestion

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_requirement(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        session_attributes['suggestion'] = suggestion
        return delegate(session_attributes, intent_request['currentIntent']['slots'])

    logger.debug('suggested dinner under={}'.format(suggestion))

    try_ex(lambda: session_attributes.pop('suggestion'))
    session_attributes['lastConfirmedReservation'] = suggestion

    # Invoke Yelp API
    yelp_response = search(API_KEY, "restaurant", location)
    name = yelp_response['businesses'][0]['name']
    address = yelp_response['businesses'][0]['location']['address1']

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Here are my {} restaurant suggestions for {} people, for {} at {}: 1. {} located at {} '.format(cuisine, number_people, dining_date, location, dating_time, name, address)
        }
    )

def trivial_response(intent_request):
	pass

# --- Intents ---

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return suggest_dining(intent_request)
    elif intent_name == 'GreetingIntent' or intent_name == 'ThankYouIntent':
        return trivial_response(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
