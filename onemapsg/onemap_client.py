from requests_toolbelt.multipart.encoder import MultipartEncoder
import time
import requests
import json

class OneMapClient():
    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.url_base = "https://www.onemap.gov.sg"

        self.expiry = 0
        self.token = None

    def get_token(self, email=None, password=None):
        if email is None:
            email = self.email
        if password is None:
            password = self.password

        json_data = {"email":email, "password":password}
        response = requests.post(
            self.url_base + "/api/auth/post/getToken",
            json=json_data,
            headers={"Content-Type":"application/json"}
        )

        response_data = json.loads(response.text)

        if response.ok:
            self.token = response_data['access_token']
            self.expiry = int(response_data['expiry_timestamp'])
        else:
            print("TOKEN REFRESH FAILED!")

        return self.token, self.expiry

    def check_expired_and_refresh_token(self):
        if time.time() - self.expiry > -10:
            token, expiry = self.get_token()
            print("REFRESHING TOKEN. NEW EXPIRY:", expiry)
            return True, token, expiry
        else:
            return False, self.token, self.expiry

    def query_api(self, endpoint, param_dict):
        '''General OneMap API query with token.'''
        self.check_expired_and_refresh_token()[0]

        try:
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint

            param_dict['token'] = self.token

            return json.loads(requests.get(self.url_base + endpoint,
                                           params=param_dict).text)
        except Exception as e:
            print(e)
            return

    def search(self, search_val, return_geom=True, get_addr_details=True, page_num=1):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        try:
            if return_geom:
                return_geom = "Y"
            else:
                return_geom = "N"

            if get_addr_details:
                get_addr_details = "Y"
            else:
                get_addr_details = "N"

            return json.loads(requests.get(self.url_base + "/api/common/elastic/search",
                                           params={'searchVal': search_val,
                                                   'returnGeom': return_geom,
                                                   'getAddrDetails': get_addr_details,
                                                   'pageNum': page_num}).text)
        except Exception as e:
            print(e)
            return

    def reverse_geocode_SVY21(self, coordinates, buffer=10, address_type="All", other_features=False):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            if other_features:
                other_features = "Y"
            else:
                other_features = "N"

            if buffer > 500:
                buffer = 500
            if buffer < 0:
                buffer = 0

            location = "{},{}".format(coordinates[0], coordinates[1])

            return json.loads(requests.get(self.url_base + "/api/public/revgeocodexy",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'location': location,
                                                   'buffer': buffer,
                                                   'addressType': address_type,
                                                   'otherFeatures': other_features}).text)
        except Exception as e:
            print(e)
            return

    def reverse_geocode_WGS84(self, coordinates, buffer=10, address_type="All", other_features=False):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            if other_features:
                other_features = "Y"
            else:
                other_features = "N"

            if buffer > 500:
                buffer = 500
            if buffer < 0:
                buffer = 0

            location = "{},{}".format(coordinates[0], coordinates[1])

            return json.loads(requests.get(self.url_base + "/api/public/revgeocodexy",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'location': location,
                                                   'buffer': buffer,
                                                   'addressType': address_type,
                                                   'otherFeatures': other_features}).text)
        except Exception as e:
            print(e)
            return

    def WGS84_to_EPSG(self, coordinates):
        self.check_expired_and_refresh_token()[0]
        try:
            return json.loads(requests.get(self.url_base + "/api/common/convert/4326to3857",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'latitude': coordinates[0],
                                                   'longitude': coordinates[1]}).text)
        except Exception as e:
            print(e)
            return

    def WGS84_to_SVY21(self, coordinates):
        self.check_expired_and_refresh_token()[0]
        try:
            return json.loads(requests.get(self.url_base + "/api/common/convert/4326to3414",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'latitude': coordinates[0],
                                                   'longitude': coordinates[1]}).text)
        except Exception as e:
            print(e)
            return

    def SVY21_to_EPSG(self, coordinates):
        self.check_expired_and_refresh_token()[0]
        try:
            return json.loads(requests.get(self.url_base + "/api/common/convert/3414to3857",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'X': coordinates[0],
                                                   'Y': coordinates[1]}).text)
        except Exception as e:
            print(e)
            return

    def SVY21_to_WGS84(self, coordinates):
        self.check_expired_and_refresh_token()[0]
        try:
            return json.loads(requests.get(self.url_base + "/api/common/convert/3414to4326",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'X': coordinates[0],
                                                   'Y': coordinates[1]}).text)
        except Exception as e:
            print(e)
            return

    def EPSG_to_SVY21(self, coordinates):
        self.check_expired_and_refresh_token()[0]
        try:
            return json.loads(requests.get(self.url_base + "/api/common/convert/3857to3414",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'X': coordinates[0],
                                                   'Y': coordinates[1]}).text)
        except Exception as e:
            print(e)
            return

    def EPSG_to_WGS84(self, coordinates):
        self.check_expired_and_refresh_token()[0]
        try:
            return json.loads(requests.get(self.url_base + "/api/common/convert/3857to4326",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'X': coordinates[0],
                                                   'Y': coordinates[1]}).text)
        except Exception as e:
            print(e)
            return

    def check_theme_status(self, query_name, date_time):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/themesvc/checkThemeStatus",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'queryName': query_name,
                                                   'dateTime': date_time}).text)
        except Exception as e:
            print(e)
            return

    def get_theme_info(self, query_name):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/themesvc/getThemeInfo",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'queryName': query_name}).text)
        except Exception as e:
            print(e)
            return

    def get_all_themes_info(self, more_info=False):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            if more_info:
                more_info = "Y"
            else:
                more_info = "N"

            return json.loads(requests.get(self.url_base + "/api/public/themesvc/getAllThemesInfo",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'moreInfo': more_info}).text)
        except Exception as e:
            print(e)
            return
        
    def retrieve_theme(self, query_name, extents=None):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            if extents is not None:
                extents = "{},{},{},{}".format(extents[0], extents[1], extents[2], extents[3])

            return json.loads(requests.get(self.url_base + "/api/public/themesvc/retrieveTheme",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'queryName': query_name,
                                                   'extents': extents}).text)
        except Exception as e:
            print(e)
            return

    def get_all_planning_areas(self, year=None):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getAllPlanningarea",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year}).text)
        except Exception as e:
            print(e)
            return

    def get_planning_area_names(self, year=None):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getPlanningareaNames",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year}).text)
        except Exception as e:
            print(e)
            return

    def get_planning_area_bounds(self, coordinates, year=None):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getPlanningarea",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'lat': coordinates[0],
                                                   'long': coordinates[1]}).text)
        except Exception as e:
            print(e)
            return

    def get_economic_statuses(self, year, planning_area, gender=None):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getEconomicStatus",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area,
                                                   'gender': gender}).text)
        except Exception as e:
            print(e)
            return

    def get_education_attendance(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getEducationAttending",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_ethnic_groups(self, year, planning_area, gender=None):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getEthnicGroup",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area,
                                                   'gender': gender}).text)
        except Exception as e:
            print(e)
            return

    def get_household_monthly_work_income(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getHouseholdMonthlyIncomeWork",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_household_sizes(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getHouseholdSize",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_household_structures(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getHouseholdStructure",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_work_income(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getIncomeFromWork",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_industries(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getIndustry",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_language_literacy(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getLanguageLiterate",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_marital_statuses(self, year, planning_area, gender=None):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getMaritalStatus",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area,
                                                   'gender': gender}).text)
        except Exception as e:
            print(e)
            return

    def get_modes_of_transport_to_school(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getModeOfTransportSchool",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_modes_of_transport_to_work(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getModeOfTransportWork",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_occupations(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getOccupation",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_age_groups(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getPopulationAgeGroup",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_religious_groups(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getReligion",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_spoken_languages(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getSpokenAtHome",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_tenancy(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getTenancy",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_dwelling_types(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getTypeOfDwellingHousehold",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_population_by_dwelling_types(self, year, planning_area):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            return json.loads(requests.get(self.url_base + "/api/public/popapi/getTypeOfDwellingPop",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'year': year,
                                                   'planningArea': planning_area}).text)
        except Exception as e:
            print(e)
            return

    def get_route(self, start_coordinates, end_coordinates, route_type):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            start_coordinates = "{},{}".format(start_coordinates[0], start_coordinates[1])
            end_coordinates = "{},{}".format(end_coordinates[0], end_coordinates[1])

            return json.loads(requests.get(self.url_base + "/api/public/routingsvc/route",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'start': start_coordinates,
                                                   'end': end_coordinates,
                                                   'routeType': route_type}).text)
        except Exception as e:
            print(e)
            return

    def get_public_transport_route(self, start_coordinates, end_coordinates, date, time, mode, max_walk_distance=None, num_itineraries=1):
        '''API Documentation: https://www.onemap.gov.sg/apidocs/apidocs'''
        self.check_expired_and_refresh_token()[0]

        try:
            start_coordinates = "{},{}".format(start_coordinates[0], start_coordinates[1])
            end_coordinates = "{},{}".format(end_coordinates[0], end_coordinates[1])

            return json.loads(requests.get(self.url_base + "/api/public/routingsvc/route",
                                           headers={'Authorization': 'Bearer ' + self.token},
                                           params={'start': start_coordinates,
                                                   'end': end_coordinates,
                                                   'routeType': 'pt',
                                                   'date': date,
                                                   'time': time,
                                                   'mode': mode,
                                                   'maxWalkDistance': max_walk_distance,
                                                   'numItneraries': num_itineraries}).text)

        except Exception as e:
            print(e)
            return

    def generate_static_map(self, layer_chosen, location, zoom, width, height, polygons=None, lines=None, points=None, color=None, fill_color=None):
        '''
        API Documentation: https://www.onemap.gov.sg/apidocs/apidocs

        Polygon Format
        --------------
        Array of Points:{Color Code} | Array of Points:{Color Code}
        Example: [[1.31955,103.84223],[1.31755,103.84223],[1.31755,103.82223],[1.31755,103.81223],[1.31955,103.84223]]:255,255,105

        Line Format
        -----------
        Array of Points:{Color Code}:{Line Thickness} | Array of Points:{Color Code}:{Line thickness}
        Example: [[1.31955,103.84223],[1.31801,103.83224]]:177,0,0:3

        Point Format
        ------------
        [Point, Color Code, Marker Symbol]|[Point, Color Code, Marker Symbol]
        Example: [1.31955,103.84223,"255,255,178","B"]|[1.31801,103.84224,"175,50,0","A"]
        '''
        try:
            if zoom < 11:
                zoom = 11
            if zoom > 19:
                zoom = 19

            if width < 128:
                width = 128
            if width > 512:
                width = 512

            if height < 128:
                height = 128
            if height > 512:
                height = 512

            if type(location) == tuple or type(location) == list:
                return requests.get(self.url_base + "/api/staticmap/getStaticImage",
                                    params={'layerchosen': layer_chosen,
                                            'latitude': location[0],
                                            'longitude': location[1],
                                            'zoom': zoom,
                                            'width': width,
                                            'height': height,
                                            'polygons': polygons,
                                            'lines': lines,
                                            'points': points,
                                            'color': color,
                                            'fillColor': fill_color}).content
            else:
                return requests.get(self.url_base + "/api/staticmap/getStaticImage",
                                    params={'layerchosen': layer_chosen,
                                            'postal': location,
                                            'zoom': zoom,
                                            'width': width,
                                            'height': height,
                                            'polygons': polygons,
                                            'lines': lines,
                                            'points': points,
                                            'color': color,
                                            'fillColor': fill_color}).content

        except Exception as e:
            print(e)
            return

if __name__ == "__main__":
    email = "EMAIL_HERE"
    password = "PASSWORD_HERE"

    Client = OneMapClient(email, password)
