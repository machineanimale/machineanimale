#!/usr/bin/env python

import datetime
import os
import random
import re
import smtplib
import urllib2

import yaml

from app_secret import ANIMAL_LIST_URL, AWS_ACCESS, AWS_SECRET, AWS_S3_BUCKET,\
                       GMAIL_ADDR, GMAIL_PW, PLAYERS, ROOT_PATH

DATA_TYPES = ['noun', 'adjective']
GMAIL_SMTP = 'smtp.gmail.com'
GMAIL_PORT = 587
LOG_PATH = os.path.join(ROOT_PATH, 'log', 'machine_animale.log')
NAME_LIMIT = 5
RUN_COUNTS = [1, 1, 1, 1, 2, 1, 1]
SHARED_LIST = 'animal_list.yaml'


def animal(animals, user_data, data_type):

    """
    Returns an animal name given a list of animals, a user's data, and
    a data type, either noun or adjective.

    Args:
        animals (list[str]): a list of animals to choose from
        user_data (dict): the user's noun/adjective dictionary
        data_type (str): the type of word to select, either 'noun' or 'adj'

    Returns:
        str: the animal's name, in the form of either:
            'animal noun' (i.e., hawk missle)
            'adjective animal' (i.e., instrumental squid)
    """

    animal = random.choice(animals)
    datum = random.choice(user_data[data_type])
    if data_type == 'noun':
        nickname = [animal, datum]
    else:
        nickname = [datum, animal]

    return map(lambda s: s.replace('_', ' '), nickname)


def cache_yaml(yaml_dict, file_name):

    """
    Caches a list of YAML data in case it cannot be retrieved from
    Dropbox due to a network issue.

    Args:
        yaml_dict (dict): the dictionary object to be cached
        file_name (str): the basename of the cache file, without ext.

    Returns:
        bool: whether the cache operation succeeded.
    """

    file_name = file_name.split('/')[1]
    file_destination = os.path.join(ROOT_PATH, '{}.yaml'.format(file_name))
    try:
        with open(file_destination, 'w') as out:
            yaml.dump(yaml_dict, out)
        return True
    except IOError as e:
        return False


def dropbox_file(url):

    """
    Downloads a file and returns it as a dict object.

    Args:
        url (str): the url to download

    Returns:
        dict: the dictionary represented by the YAML file
    """

    dropbox_url = 'https://www.dropbox.com/s/{}.yaml?dl=1'.format(url)
    req = urllib2.urlopen(dropbox_url)
    return yaml.load(req.read())


def email_client():

    """
    Returns an smtplib.SMTP client object to be used with the email relay.
    Uses Gmail's SMTP server (with TLS) and login authentication.

    Returns:
        smtplib.SMTP: the mail client
    """
    smtp_client = smtplib.SMTP(GMAIL_SMTP, GMAIL_PORT)
    smtp_client.starttls()
    smtp_client.login(GMAIL_ADDR, GMAIL_PW)
    return smtp_client


def log_name_choices(player, choices):

    """
    Utility method to log the chosen names for later retrieval.

    Args:
        player (str): the name of the player for whom names were chosen
        choices (list[str]): the names sent to the player
    """

    with open(LOG_PATH, 'a') as log_file:
       timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
       args = [timestamp, player, ';'.join(map(lambda c: ' '.join(c), choices))]
       log_file.write('type=animals, date={}, player={}, value={}\n'.format(*args))


def retrieve_data(link):

    """
    Retrieves data for a given link from Dropbox, if possible.
    If not, it returns the local cache file, if possible.
    If not, the program explodes, since there is no data.

    Args:
        link (str): the url_stub for the file to be fetched

    Returns:
        dict: the dict object represented by the link arg
    """

    try:
        data = dropbox_file(link)
        cache_yaml(data, link)
        return data
    except Exception as e:
        print str(e)
        return retrieve_cached_yaml(link)


def retrieve_cached_yaml(file_name):

    """
    Retrieves cached YAML from disk. Used in the event that fetching the file
    from Dropbox fails due to some error, such as network issues.

    Args:
        file_name (str): the name of the file to retrieve

    Returns:
        dict: the dict represented by the YAML at the file's location
    """

    file_name = file_name.split('/')[1]
    file_location = os.path.join(ROOT_PATH, '{}.yaml'.format(file_name))
    with open(file_location, 'r') as in_file:
        yaml_dict = yaml.load(in_file)

    return yaml_dict


if __name__ == '__main__':

    for i in range(RUN_COUNTS[datetime.datetime.now().weekday()]):
        """
        Reads in word lists and dispatches n animals to two players defined
        in PLAYERS. Messages are sent via SMS through carrier email domains.
        """

        animals = retrieve_data(ANIMAL_LIST_URL)['animals']
        mail_client = email_client()

        for player in random.sample(PLAYERS, 2):
            link, email_target = player
            player_name = link.split('_')[1]
            data = retrieve_data(link)

            player_animals = [animal(animals, data, random.choice(DATA_TYPES))
                              for n in range(NAME_LIMIT)]

            log_name_choices(player_name, player_animals)

            body = '\n'.join(map(lambda p: ' '.join(p), player_animals))
            mail_client.sendmail(GMAIL_ADDR, email_target, body)
