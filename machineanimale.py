#!/usr/bin/env python

import datetime
import os
import random
import re

import yaml

from app_secret import ANIMAL_LIST_URL, PLAYERS, ROOT_PATH
import email_util
import util

DATA_TYPES = ['noun', 'adjective']
DURATION = 5
RUN_FREQUENCY = [1, 1, 1, 1, 2, 0, 1]


class Player(object):

    def __init__(self, player_info, animals):
        self.name, self.dropbox_file, self.sms_mail = player_info
        self.animals = animals
        self.data = retrieve_data(util.dropbox_file(self.dropbox_file))
        self.data_types = ['noun', 'adjective']
        self._opponent = None

    @property
    def opponent(self):
        return self._opponent

    @opponent.setter
    def opponent(self, value):
        self._opponent = value

    def animal(self):

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

        animal = random.choice(self.animals)
        # random.shuffle(self.animals)
        # animal = self.animals.pop()

        data_type = random.choice(self.data_types)
        data = [d for d in self.data[data_type]]

        random.shuffle(data)
        datum = data.pop()
        self.data[data_type] = [d for d in data]

        if data_type == 'noun':
            nickname = '{} {}'.format([animal, datum])
        else:
            nickname = '{} {}'.format([datum, animal])

        return nickname.replace('_', ' ')


    def play(self):

        """

        """

        for i in range(DURATION):
            self.generated_animals.append(self.animal())

        util.log_name_choices(self.opponent.name, self.generated_animals)
        self.send_animals()

    def send_animals(self):

        """

        """

        body = '\n'.join(self.generated_animals)

        smtp_client = email_util.client()
        smtp_client.sendmail(GMAIL_ADDR, self.opponent.sms_mail, body)
        smtp_client.quit()

        self.sent_animals = [a for a in self.generated_animals]
        self.generated_animals = []


if __name__ == '__main__':

    for i in range(RUN_COUNTS[datetime.datetime.now().weekday()]):
        """
        Reads in word lists and dispatches n animals to two players defined
        in PLAYERS. Messages are sent via SMS through carrier email domains.
        """

        animals = util.retrieve_data(ANIMAL_LIST_URL)['animals']

        players = map(lambda p: Player(p, animals), random.sample(PLAYERS,2))
        players[0].opponent = players[1]
        players[1].opponent = players[0]

        for i in range(RUN_FREQUENCY[datetime.datetime.now().weekday()]):
            for player in players:
                player.play()
