import json
import os
import logging


class Configuration:
    """
        Configuration class loads test configuration from the json file in the
        config folder
    """
    path = '../../config'

    def __init__(self, file_name):
        """
        Constructor

        :param file_name: Name of the file to load the configuration from
        :return:
        """
        self.logger = logging.getLogger(__name__)
        self.file_config = Configuration.load_json_file_config(os.path.join(
            Configuration.config_path(), file_name))

    @staticmethod
    def load_json_file_config(path):
        """
        Load the json object from json file

        :param path: Path of the json file
        :return:
        """
        with open(path, 'rt') as f:
            file_config = json.load(f)
        return file_config

    @staticmethod
    def config_path():
        """
        Path to the 'config' folder

        :return:
        """
        return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            Configuration.path)

    def get_user_auth_headers(self, user):
        """
        Base auth headers associated to the user in the config file

        :param user: username
        :return:
        """
        if user is None:
            raise RuntimeError("User cannot be None")

        return self.file_config[user]

    def get_url(self, path):
        """
        Generate url given the path name

        :param path: Path name
        :return:
        """
        if path is None:
            raise RuntimeError("path cannot be None")

        url = self.file_config['url'] + self.file_config[
            'version'] + self.file_config['path'][path]

        return url