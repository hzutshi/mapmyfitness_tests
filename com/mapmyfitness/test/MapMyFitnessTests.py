import json
from pyvows import Vows, expect
from com.mapmyfitness.Configuration import Configuration
from com.mapmyfitness.RouteHelper import RouteHelper
from com.mapmyfitness.UserHelper import UserHelper


@Vows.batch
class MapMyFitnessTests(Vows.Context):

    def topic(self):
        return Configuration('config_test.json')

    class AsAUserIWantTo(Vows.Context):

        def topic(self, configuration):
            return UserHelper(configuration)

        def verify_authenticated_user_info(self, topic):
            user = topic.get_authenticated_user('TestUser1')
            expect(user).Not.to_be_null()
            expect(user['first_name']).to_be_like('Hema')

        def verify_user_id(self, topic):
            expect(topic.get_user_id('TestUser1')).to_equal(63639234)

        class UpdateUserInfo(Vows.Context):

            def topic(self, user_helper):
                data = dict()
                data['last_name'] = 'Zutshi'
                data['weight'] = 50
                user_helper.update_user('TestUser1', user_data=data)
                return user_helper

            def verify_updated_user_info(self, topic):
                user = topic.get_authenticated_user('TestUser1')
                expect(user).Not.to_be_null()
                expect(user['last_name']).to_be_like('Zutshi')
                expect(int(user['weight'])).to_equal(49)

    class AsAUserIWouldLikeTo(Vows.Context):

            def topic(self, configuration):
                return RouteHelper(configuration)

            def add_a_route(self, topic):
                expect(topic.add_route_to_user(
                    'TestUser1', 'Night_Route')).Not.to_be_null()

            class GetUpdatedRouteList(Vows.Context):

                def topic(self, route_helper):
                    ids = RouteHelper.get_route_id_list_from_response(
                        route_helper.get_routes_for_user(
                            'TestUser1', additional_parameters={'limit': '1000'}
                        ))
                    route_info = dict()
                    route_info['route_helper'] = route_helper
                    route_info['route_ids'] = ids

                    return route_info

                def verify_route_got_added(self, topic):
                    for id in topic['route_ids']:
                        route = json.loads(
                            topic['route_helper'].get_route_by_id(
                                'TestUser1', id, detailed=True))
                        print route['description']
                        if 'test route around cedar park' in route['description']:
                            expect(True).to_be_true()
                            return

                    expect(True).Not.to_be_true()

                def add_another_route(self, topic):
                    expect(topic['route_helper'].add_route_to_user(
                        'TestUser1', 'Night_Route_Sammamish')).Not.to_be_null()

                class GetUpdatedRouteList(Vows.Context):

                    def topic(self, route_helper):
                        ids = RouteHelper.get_route_id_list_from_response(
                            route_helper['route_helper'].get_routes_for_user(
                                'TestUser1', additional_parameters={
                                    'limit': '1000'}))
                        route_helper['route_ids'] = ids

                        return route_helper

                    def verify_route_got_added(self, route_helper):
                        for id in route_helper['route_ids']:
                            route = json.loads(
                                route_helper['route_helper'].get_route_by_id(
                                    'TestUser1', id, detailed=True))

                            if 'test route around Sammamish' in \
                                    route['description']:
                                expect(True).to_be_true()
                                return

                        expect(True).Not.to_be_true()

                    def delete_existing_route(self, route_helper):
                        id = route_helper['route_ids'][0]
                        expect(route_helper['route_helper'].delete_route_by_id(
                            'TestUser1', id)).to_be_true()
                        route_helper['deleted_id'] = id

                    class GetUpdatedRouteList(Vows.Context):

                        def topic(self, route_helper):
                            ids = RouteHelper.get_route_id_list_from_response(
                                route_helper['route_helper'].get_routes_for_user(
                                    'TestUser1', additional_parameters={'limit':'1000'}))

                            route_helper['route_ids'] = ids

                            return route_helper

                        def verify_route_got_deleted(self, route_helper):
                            expect(route_helper['route_ids']).Not.to_include(
                                route_helper['deleted_id'])