import datetime
import os
import urllib2

import yaml

from app_secret import ROOT_PATH


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
        print '-------------{}---------------'.format(link)
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


def log_name_choices(player, choices):

    """
    Utility method to log the chosen names for later retrieval.

    Args:
        player (str): the name of the player for whom names were chosen
        choices (list[str]): the names sent to the player
    """

    log_path = os.path.join(ROOT_PATH, 'log', 'machine_animale.log')
    if not os.path.exists(os.path.dirname(log_path)):
        os.makedirs(os.path.dirname(log_path))

    with open(log_path, 'a') as log_file:
       timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
       args = [timestamp, player, ';'.join(map(lambda c: ' '.join(c), choices))]
       log_file.write('type=animals, date={}, player={}, value={}\n'.format(*args))
