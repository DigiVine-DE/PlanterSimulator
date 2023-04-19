from api_methods import delete_plants
import argparse
field_id = 42
plant_run_id = 12
id_from = 13000
id_to = 14000


# The arguments required for executing the method
parser = argparse.ArgumentParser()
parser.add_argument('--api-token', default="", help='The token for the api.')
parser.add_argument('--base-url', default="", help='The url of the api.')
args = parser.parse_args()

delete_plants(field_id, plant_run_id, id_from, id_to, base_url=args.base_url, api_token=args.api_token)
