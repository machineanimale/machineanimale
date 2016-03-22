#!/usr/bin/env python

import datetime
import os
import random
import re

import yaml

from app_secret import ANIMAL_LIST_URL, GMAIL_ADDR, PLAYERS, ROOT_PATH
import email_util
import util


class Game(object):

    def __init__(self, data_types, animal_count, turn_count):
        self.data_types = data_types
        self.animals_count = animal_count
        self.player_turns = turn_count
        self._players = []

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, player_list):
        self._players = player_list

    def play(self):

        """
        Plays the game. For each player in the game, the player will
        have a turn for each number of turns for the day. In each turn,
        the player will generate a number of animal names, and send them
        to the opponent.
        """

        turns = self.player_turns[datetime.datetime.today().weekday()]
        for player in self.players:
            for turn in range(turns):
                for animal in range(self.animals_count):
                    player.animal()
                player.send()


class Player(object):

    def __init__(self, player_info, animals):
        self.name, self.dropbox_file, self.sms_mail = player_info
        self.animals = animals
        self.data = util.retrieve_data(self.dropbox_file)
        self.data_types = ['noun', 'adjective']
        self.generated_animals = []
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
        data_type = random.choice(self.data_types)
        datum = random.choice(self.data[data_type])

        if data_type == 'noun':
            nickname = '{} {}'.format(animal, datum)
        else:
            nickname = '{} {}'.format(datum, animal)

        self.generated_animals.append(nickname.replace('_', ' '))

    def send(self, reset=True):

        """

        """

        util.log_name_choices(self.opponent.name, self.generated_animals)
        body = '\n'.join(self.generated_animals)

        email_util.send(self.opponent.sms_mail, body)

        if reset:
            self.generated_animals = []


if __name__ == '__main__':

    """
    Reads in word lists and dispatches n animals to two players defined
    in PLAYERS. Messages are sent via SMS through carrier email domains.
    """
    DATA_TYPES = ['adjective', 'noun']
    ANIMAL_COUNT = 5
    TURN_COUNT = [1, 1, 1, 1, 2, 0, 1]

    animals = util.retrieve_data(ANIMAL_LIST_URL)['animals']

    game = Game(DATA_TYPES, ANIMAL_COUNT, TURN_COUNT)

    players = map(lambda p: Player(p, animals), random.sample(PLAYERS,2))
    players[0].opponent = players[1]
    players[1].opponent = players[0]

    game.players = players
    game.play()
