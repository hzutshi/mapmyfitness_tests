import json
import requests
from com.mapmyfitness.Configuration import Configuration
from com.mapmyfitness.MmfBase import MmfBase

import logging


class UserHelper(MmfBase):
    """
        Helper class for User APIs
    """
    def __init__(self, config):
        """
        Constructor

        :param config:  Test Configuration object to use
        :return:
        """
        MmfBase.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.configuration = config
        self.user_id = {}

    def get_authenticated_user(self, user_name):
        """
        Gets the authenticated user information given a user name
        :param user_name: Username to use in order to retrieve auth info
        associated to the user from the Configuration object
        :return:
        """
        try:
            response = requests.get(self.configuration.get_url("AuthenticatedUser"),
                                    headers=self.configuration.get_user_auth_headers(user_name))
            if response.ok:
                user = json.loads(response.content)
            else:
                self.logger.exception(response.content)
                return None
        except requests.HTTPError as e:
            self.logger.exception(e.message)

        return user

    def get_user_id(self, user_name):
        """
        Retrieve the user_id from the authenticated user response
        :param user_name: Username to use in order to retrieve auth info
        associated to the user from the Configuration object
        :return:
        """
        if self.user_id.has_key(user_name):
            return self.user_id[user_name]
        else:
            self.user_id[user_name] = int(
                self.get_authenticated_user(user_name)['id'])
            return self.user_id[user_name]

    def update_user(self, user_name, user_data=None):
        """
        Updates user information given the user data

        :param user_name: Username to use in order to retrieve auth info
        associated to the user from the Configuration object
        :param user_data: User data represented as a dict object to update
        the user information
        :return: Returns True for success. False for failure
        """
        if user_data is not None:
            if isinstance(user_data, dict):
                data = json.dumps(user_data)
            else:
                self.logger.exception('Data needs be of type dict')
                raise RuntimeError('Data needs be of type dict')

        try:
            url = self.configuration.get_url(
                "User")+"/%s/" % self.get_user_id(user_name)
            self.logger.info(url)
            response = requests.put(
                url, data=data,
                headers=self.configuration.get_user_auth_headers(user_name))
            if response.ok:
                self.logger.info(response.content)
                return True
            else:
                self.logger.exception(response.text)
                return False
        except requests.HTTPError as e:
            self.logger.exception(e.message)
            return False