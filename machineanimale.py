#!/usr/bin/env python

import datetime
import os
import random
import re
import smtplib

from app_secret import AWS_ACCESS, AWS_SECRET, AWS_S3_BUCKET, \
    GMAIL_ADDR, GMAIL_PW, ROOT_PATH, USERS
import boto
from boto.s3.key import Key as S3Key
import yaml


DATA_TYPES = ['noun', 'adjective']
GMAIL_SMTP = 'smtp.gmail.com'
GMAIL_PORT = 587
NAME_LIMIT = 5
RUN_COUNTS = [1, 1, 1, 1, 2, 0, 1]
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


def date_resolve(date=None):

    """
    Resolve the date passed in to a string represented in the following form:
       3/18/2016 -> "Friday, Mar. 18, 2016"

    Kwargs:
        date (datetime.datetime): the date to resolve, defaulting to None

    Returns:
        str: the date string resolvd from the date in question
    """

    date = date or datetime.datetime.now()
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    months = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.',
              'Jul.', 'Aug.', 'Sept.', 'Oct.', 'Nov.','Dec.']

    day = days[date.weekday()]
    month = months[date.month]
    return '{}, {} {}, {}'.format(day, month, date.day, date.year)


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


def fetch_lists():

    """
    Reaches out to S3 and pulls the current word lists down to the local FS.
    """

    conn = boto.connect_s3(AWS_ACCESS, AWS_SECRET)
    bucket = conn.get_bucket(AWS_S3_BUCKET)
    keys = bucket.list()
    for key in keys:
        if re.search('list.yaml', key.key):
            k = S3Key(bucket)
            k.key = key.key
            k.get_contents_to_filename(os.path.join(ROOT_PATH, key.key))


def fetch():

    """
    Reads in word lists and dispatches n animals to each person defined
    in USERS. Messages are sent via SMS proxied through carrier email domains.

    If it is Sunday, each user's word lists, as well as the animal list, are
    retrieved from S3, which creates a week-long update cycle.
    """

    if datetime.datetime.now().weekday() == 6:
        fetch_lists()

    #mail_client = email_client()

    with open(os.path.join(ROOT_PATH, SHARED_LIST)) as animal_file:
        animals = yaml.load(animal_file)['animal']

    for user in USERS.values():

        with open(os.path.join(ROOT_PATH, user['source']), 'r') as in_file:
        p    data = yaml.load(in_file)

        nicknames = [animal(animals, data, random.choice(DATA_TYPES))
                     for n in range(NAME_LIMIT)]

        body = '\n'.join(map(lambda p: ' '.join(p), nicknames))
        print body
        return
        #mail_client.sendmail(GMAIL_ADDR, user['email_target'], body)


if __name__ == '__main__':

    run_count = RUN_COUNTS[datetime.datetime.now().weekday()]
    for i in range(run_count):
        fetch()

