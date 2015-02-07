import json
import logging
import os
import requests
from com.mapmyfitness.Configuration import Configuration

from com.mapmyfitness.MmfBase import MmfBase
from com.mapmyfitness.UserHelper import UserHelper


class RouteHelper(MmfBase):
    """
        Route API helper library
    """
    def __init__(self, config):
        """
        Constructor

        :param config: Test Configuration object to use
        :return:
        """
        MmfBase.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.configuration = config
        self.user_helper = UserHelper(config)
        self.route = 'Route'
        self.route_json_file = 'route.json'

    def get_route_by_id(self, user_name, route_id, detailed=False,
                        response_data_format='json'):
        """
        Get route detail given the route_id and the user the route is associated
        to

        :param user_name: Username to use in order to retrieve auth info
        associated to the user from the Configuration object
        :param route_id: Unique route id associated to the route
        :param detailed: Boolean indicating whether a detailed information on
        the route is sought. Defaults to false
        :param response_data_format: The format in which the response is sought.
        Defaults to json
        :return: Returns the json response containing the route details
        """
        parameters = dict()
        parameters['detailed'] = detailed
        parameters['format'] = response_data_format

        try:
            url = self.configuration.get_url(self.route)+"%s/" % route_id
            response = requests.get(
                url, headers=self.configuration.get_user_auth_headers(
                    user_name), params=parameters)

            self.logger.info(response.content)

            if response.ok:
                return response.content
            else:
                self.logger.exception(response.content)
                return None
        except requests.HTTPError as e:
            self.logger.exception(e.message)
            return None

    def get_routes_for_user(self, user_name, additional_parameters=None):
        """
        Get all routes associated for a given user

        :param user_name: Username to use in order to retrieve auth info
        associated to the user from the Configuration object
        :param additional_parameters: Any additional query parameters that needs
        to be added to the query as filters as per the API

        :return:Returns the json response containing the route details
        """
        user_id = self.user_helper.get_user_id(user_name)
        parameters = dict()
        parameters['user'] = user_id

        if additional_parameters:
            for key, value in additional_parameters.iteritems():
                parameters[key] = value

        try:
            response = requests.get(
                self.configuration.get_url(self.route),
                headers=self.configuration.get_user_auth_headers(user_name),
                params=parameters)

            self.logger.info(response.content)

            if response.ok:
                return response.content
            else:
                self.logger.exception(response.content)
                return None
        except requests.HTTPError as e:
            self.logger.exception(e.message)
            return None

    def add_route_to_user(self, user_name, route_entry_in_json):
        """
        Adds a given route and associates it with the given user

        :param user_name: Username to use in order to retrieve auth info
        associated to the user from the Configuration object
        :param route_entry_in_json: route name as mentioned in the route.json
        present under the config directory
        :return: Returns the json response containing the route details as
        entered in the database
        """
        route_info = self.get_route_data_from_json(route_entry_in_json)
        try:
            response = requests.post(
                self.configuration.get_url(self.route),
                data=route_info,
                headers=self.configuration.get_user_auth_headers(user_name))

            self.logger.info(response.content)

            if response.ok:
                return json.loads(response.content)
            else:
                self.logger.exception(response.content)
                return None
        except requests.HTTPError as e:
            self.logger.exception(e.message)
            return None

    def update_route_details(self, user_name, route_id, route_details):
        """
        Updates a given route and associates it with the given user

        :param user_name: Username to use in order to retrieve auth info
        associated to the user from the Configuration object
        :param route_id: Unique route id associated to the route
        :param route_details: route details represented as a dict object to be
        converted into a json object and added to API payload
        :return: Returns the json response containing the route details as
        entered in the database
        """
        if route_details:
            route_details = json.loads(route_details)
        else:
            self.logger.exception("Route details cannot be None")
            return None

        try:
            url = self.configuration.get_url(self.route)+"%s/" % route_id
            self.logger.debug(url)
            response = requests.put(
                url, data=route_details,
                headers=self.configuration.get_user_auth_headers(user_name))

            self.logger.info(response.content)

            if response.ok:
                return json.loads(response.content)
            else:
                self.logger.exception(response.content)
                return None
        except requests.HTTPError as e:
            self.logger.exception(e.message)
            return None

    def delete_route_by_id(self, user_name, route_id):
        """
        Deletes a route given the unique route_id and the username the route
        is associated to
        :param user_name: Username to use in order to retrieve auth info
        associated to the user from the Configuration object
        :param route_id: Unique route id associated to the route
        :return: Returns True for successful route deletion. False otherwise
        """
        try:
            url = self.configuration.get_url(self.route)+"%s/" % route_id
            self.logger.debug(url)
            response = requests.delete(
                url,
                headers=self.configuration.get_user_auth_headers(user_name))

            self.logger.info(response.content)

            if response.ok:
                self.logger.info(response.status_code)
                return True
            else:
                self.logger.exception(response.content)
                return False
        except requests.HTTPError as e:
            self.logger.exception(e.message)
            return False

    @staticmethod
    def get_route_detail_list_from_response(response):
        return json.loads(response)['_embedded']['routes']

    @staticmethod
    def get_route_id_list_from_response(response):
        route_ids = []
        routes = RouteHelper.get_route_detail_list_from_response(response)
        for route in routes:
            route_ids.append(int(route['_links']['self'][0]['id']))
        return route_ids

    def get_route_data_from_json(self, route_entry_in_json):
        """
        Helper method to retrieve route data from the 'route.json' file
        :param route_entry_in_json: route name entry in json file
        :return:
        """
        if route_entry_in_json is not None:
            path = os.path.join(self.configuration.config_path(),
                                self.route_json_file)
            if os.path.exists(path):
                file_config = Configuration.load_json_file_config(path)
                try:
                    return json.dumps(file_config[route_entry_in_json])
                except KeyError as e:
                    self.logger.exception(
                        "Key %s not found. Error %s" % (
                            route_entry_in_json, e.message))
                    return None
            else:
                self.logger.exception("Route data file not found")
                return None
        else:
            raise RuntimeError("Route entry name cannot be none")