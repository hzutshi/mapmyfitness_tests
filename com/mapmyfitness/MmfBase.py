import os
from com.mapmyfitness.Configuration import Configuration
from logging import config

import json
import logging
from collections import namedtuple


class MmfBase(object):
    """
        Test Base class
    """
    def __init__(self):
        """
        Constructor

        :return:
        """
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _json_object_hook(d):
        return namedtuple('X', d.keys(), rename=True)(*d.values())

    @staticmethod
    def json2obj(data):
        """
        Converts a json object to python object with dict keys as attributes

        :param data: json data to be used for conversion
        :return:
        """
        return json.loads(data, object_hook=MmfBase._json_object_hook)

    @staticmethod
    def setup_logging(
            default_path=None, file_name='logging.json',
            default_level=logging.INFO, env_key='LOG_CFG'):
        """
        Setup logging using the supplied parameters

        :param default_path: Defaults to None. Setup looks for logging.json
        file under the 'config' folder

        :param default_level: Set to INFO
        :param env_key:
        :return:
        """
        path = default_path
        value = os.getenv(env_key, None)

        if value:
            path = value
        if path is None:
            path = os.path.join(Configuration.config_path(), file_name)
        if os.path.exists(path):
            file_config = Configuration.load_json_file_config(path)
            config.dictConfig(file_config)
        else:
            logging.basicConfig(level=default_level)
