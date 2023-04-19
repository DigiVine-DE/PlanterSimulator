import requests, json
from datetime import datetime
from urllib.request import urlopen

def assert_api_token_empty(api_token):
    assert api_token.strip() != "", "api_token needs to be specified!"
    print(f'api token has value: {api_token}')

def assert_base_url_empty(base_url):
    assert base_url.strip() != "", "base_url needs to be specified!"
    print(f'base url has value: {base_url}')


def get_field(field_id, planter_run, base_url='', api_token=''):
    # check if api-token is empty
    assert_api_token_empty(api_token)

    # check if base url is empty
    assert_base_url_empty(base_url)

    # the link to the json file with fields
    url_to_geojson_fields_data = "{}field?api-token={}".format(base_url, api_token)
    # invoke the url and store the response
    response = urlopen(url_to_geojson_fields_data)
    # parse the response to json
    fields_and_plant_runs = json.loads(response.read())
    # for object_in_data in fields_and_plant_runs:
    #     print(object_in_data)
    #     print('')

    last_planter_run_id = 0
    planter_run_id = -1

    row_number = 1
    previous_x = None

    for tmp_field in fields_and_plant_runs:
        if tmp_field['properties']['id'] == field_id:
            field = tmp_field
            print('got it')

    # take just one field just for try out
    # field = fields_and_plant_runs[len(fields_and_plant_runs)-3]

    # take the id of the field
    field_id = field['properties']['id']
    print("The field id is " + str(field_id))
    # some other number not sure for what
    field_number = field['properties']['number']
    field_name = field['properties']['name']
    # take the coordinates
    coordinates_for_one_field = field['geometry']['coordinates'][0][0]
    print(planter_run)

    if planter_run == 0:
        '''create a new planter run '''
        print('creating a new planter run')
        planter_run_id = create_new_planter_run(field_id, base_url=base_url, api_token=api_token)
    else:
        '''work with an existing planter run'''
        planter_run_id = planter_run
        print('will be using an existing field')

    print('planter run id: %d ' % planter_run_id)

    return field_number, field_name, planter_run_id, coordinates_for_one_field

def create_new_planter_run(field_id, user_id=234, terminal_id=345, base_url='', api_token=''):
    # check if api-token is empty
    assert_api_token_empty(api_token)

    # check if base url is empty
    assert_base_url_empty(base_url)

    url_to_new_plant_run = base_url + 'field/{}/planter?api-token={}'.format(field_id, api_token)
    print(url_to_new_plant_run)

    planter_run_json_object = {"type": "FeatureCollection", "features": [], "properties": {"field_id": int(field_id), "user_id": int(user_id), "terminal_id": int(terminal_id)}}
    print(planter_run_json_object)

    request_response = requests.post(url_to_new_plant_run, data=json.dumps(planter_run_json_object))
    print(request_response)
    return request_response.json()["id"]

def delete_plants(field_id, plant_run_id, id_from, id_to, base_url='', api_token=''):
    # check if api-token is empty
    assert_api_token_empty(api_token)

    # check if base url is empty
    assert_base_url_empty(base_url)

    how_many_deleted = 0
    for plant_id in range(id_from, id_to):
        url_to_new_plant_run = base_url + 'field/{}/planter/{}/plant/{}?api-token={}'.format(
            field_id, plant_run_id, plant_id, api_token)
        print(url_to_new_plant_run)
        request_response = requests.delete(url_to_new_plant_run)
        print(request_response)
        how_many_deleted += 1
    print('deleted %d plants ' % how_many_deleted)

#fetches all the plant ids for given field_id and plant_run and then deletes it
def delete_all_plants(field_id, plant_run_id, base_url='', api_token=''):
    # check if api-token is empty
    assert_api_token_empty(api_token)

    # check if base url is empty
    assert_base_url_empty(base_url)

    url_to_all_plants = base_url + 'field/{}/planter/{}/plant?api-token={}'.format(
        field_id, plant_run_id, api_token)
    request_response = requests.get(url_to_all_plants)
    plants = request_response.json()
    plant_ids = [x["properties"].get("id") for x in plants]

    while len(plant_ids) != 0:
        print(plant_ids)
        for plant_id in plant_ids:
            url_to_new_plant_run = base_url + 'field/{}/planter/{}/plant/{}?api-token={}'.format(
                field_id, plant_run_id, plant_id, api_token)
            print(url_to_new_plant_run)
            request_response = requests.delete(url_to_new_plant_run)
            print(request_response)
        request_response = requests.get(url_to_all_plants)
        plants = request_response.json()
        plant_ids = [x["properties"].get("id") for x in plants]

#fetches all the plant ids for given field_id, plant_run in a given row and then deletes it
def delete_all_plants_in_a_row(field_id, plant_run_id, row, base_url='', api_token=''):
    # check if api-token is empty
    assert_api_token_empty(api_token)

    # check if base url is empty
    assert_base_url_empty(base_url)

    url_to_all_plants = base_url + 'field/{}/planter/{}?api-token={}'.format(
            field_id, plant_run_id, api_token)
    request_response = requests.get(url_to_all_plants)
    plants = request_response.json()
    plants = plants["features"]
    plant_ids = [x["properties"].get("id") for x in plants if x["properties"].get("row_number") == row]
    print(plant_ids)

    for plant_id in plant_ids:
        url_to_new_plant_run = base_url + 'field/{}/planter/{}/plant/{}?api-token={}'.format(
                    field_id, plant_run_id, plant_id, api_token)
        print(url_to_new_plant_run)
        request_response = requests.delete(url_to_new_plant_run)
        print(request_response) 

def send_planting_point_to_warehouse(point_pos_x, point_pos_y, field_id, field_name, plant_run_id, row_distance,
                                     plant_distance, row_number, tractor_speed, base_url='', api_token=''):
    # check if api-token is empty
    assert_api_token_empty(api_token)

    # check if base url is empty
    assert_base_url_empty(base_url)

    url_to_new_plant_run = base_url + 'field/{}/planter/{}/plant?api-token={}'.format(field_id, plant_run_id, api_token)
    print(url_to_new_plant_run)

    # create the json object representing the plant
    planter_run_json_object = {"type": "Feature",
                               "geometry": {
                                    "bbox": [],
                                    "coordinates": [point_pos_x, point_pos_y],
                                    "type": "Point"
                                  },
                               "properties": {
                                   "import_key": field_name + "-test",
                                   "row_distance": row_distance,
                                   "plant_distance": plant_distance,
                                   "deviation": 12.3456789012345,
                                   "row_number": row_number,
                                   "speed": tractor_speed,
                                   "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                   "height": 123000}
                               }

    print(planter_run_json_object)
    # send the request
    request_response = requests.post(url_to_new_plant_run, data=json.dumps(planter_run_json_object))
    print(request_response)
    return request_response


def save_caller(plant_generation_given_field_dimensions, ordered_list_points, base_url='', api_token=''):
    # check if api-token is empty
    assert_api_token_empty(api_token)

    # check if base url is empty
    assert_base_url_empty(base_url)

    for i in range(len(ordered_list_points)):
        xi = ordered_list_points[i][0]
        yi = ordered_list_points[i][1]

        field_point = plant_generation_given_field_dimensions.get_coordinate(xi, yi)

        print(xi)
        # check if the plant is in a different row
        if field_point.x != plant_generation_given_field_dimensions.previous_x:
            plant_generation_given_field_dimensions.row_number = plant_generation_given_field_dimensions.row_number + 1
            print('DIFFERENT')
        else:
            print('NOT DIFFERENT')

        # change the previous x position
        plant_generation_given_field_dimensions.previous_x = field_point.x

        # store the point in the warehouse
        send_planting_point_to_warehouse(field_point.x, field_point.y,
                                         field_id=plant_generation_given_field_dimensions.field_id,
                                         field_name=plant_generation_given_field_dimensions.field_name,
                                         plant_run_id=plant_generation_given_field_dimensions.planter_run_id,
                                         row_distance=plant_generation_given_field_dimensions.distance_rows,
                                         plant_distance=plant_generation_given_field_dimensions.distance_plants,
                                         tractor_speed=plant_generation_given_field_dimensions.speed_of_tractor,
                                         row_number=plant_generation_given_field_dimensions.row_number,
                                         base_url=base_url,
                                         api_token=api_token)
