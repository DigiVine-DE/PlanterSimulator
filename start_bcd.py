import boustrophedon, graph, way, argparse, numpy as np
from additional_methods import create_timestamp_for_plant_generation, create_ordered_list_points, animate
from api_methods import save_caller, get_field
from plant_generation import PlantGeneration

# The arguments required for executing the method
parser = argparse.ArgumentParser()
# Some fields you can try 36, 37, 40, 42, 43, 44, 50
parser.add_argument('--field-id', type=int, default='71', help='The id of the field for which the plant will be performed.')
parser.add_argument('--planter-run', type=int, default='0', help='If 0, then a new planter run will be created, else the one specified will be used.')
parser.add_argument('--animate-plant', type=bool, default=False, help='Choice whether to animate the planting.')
parser.add_argument('--store-plant', type=bool, default=True, help='Choice whether to store example plant.')
parser.add_argument('--api-token', default="", help='The token for the api.')
parser.add_argument('--base-url', default="", help='The url of the api.')
args = parser.parse_args()

# Reading of one specific run
field_number, field_name, planter_run_id, coordinates_for_one_field = get_field(args.field_id, args.planter_run,
                                                                                base_url=args.base_url,
                                                                                api_token=args.api_token)
pg = PlantGeneration(args.field_id, args.planter_run, field_number, field_name, planter_run_id, coordinates_for_one_field)

# Matrix composed of 1s and 0s, 1 denotes an obstacle and 0 a field
matrix = pg.adj_matrix
node_edge_point = pg.node_edge_point
# Currently no in-field obsticles
node_barrier_point = []
mc = boustrophedon.Boustrophedon(matrix)
# Matrix with numbers representing cell decomposition, 1s irepresent obsticales, the other numbers are shiffted + 1 from the visualization
matrix = mc.final_decomposition()
print(matrix)
# Cell number is the max number of cells present in the cell docomposition
graph = graph.Graph(matrix, mc.cell_number)
# Nb_cells x Nb_cells interconnection between cells represent through the matrix, at position A_01 = 1 if 1st cell has a connection to 2nd same at A_10 = 1
matrix_dependencies = graph.graph()
print("Matrix dependencies or graph matrix" + str(matrix_dependencies))

way = way.Way(matrix_dependencies)
# Order of the cells that need to be visited
sequence = way.DFS_Algorithm()
print("The sequence is :" + str(sequence))

# Not sure whether this is needed
# final_point = points.Points(matrix, sequence, node_edge_point, node_barrier_point)
# print(final_point)
# Not sure whether this is needed

ordered_list_points = create_ordered_list_points(sequence, matrix)
# for the time
matrix_for_time = create_timestamp_for_plant_generation(pg, ordered_list_points, pg.speed_of_tractor, pg.time_needed_for_planting)
# set the value for the previous x coordinate, used for identifying the rows in the field
pg.previous_x = pg.get_coordinate(ordered_list_points[0][0], ordered_list_points[0][1]).x
print("Num of points: " + str(np.shape(ordered_list_points)))

if args.animate_plant:
    animate(matrix, ordered_list_points)


if args.store_plant:
    save_caller(pg, ordered_list_points, base_url=args.base_url, api_token=args.api_token)

# removed
# mpl.rcParams['animation.ffmpeg_path'] = r'/ffmpeg'
# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir)