import boustrophedon, graph, way, numpy as np
from additional_methods import create_timestamp_for_plant_generation, create_ordered_list_points, animate
from api_methods import save_caller, get_field
from plant_generation import PlantGeneration

def plant_trees(field_id, planter_run, base_url='', api_token=''):
    # The arguments required for executing the method

    # Reading of one specific run
    field_number, field_name, planter_run_id, coordinates_for_one_field = get_field(field_id, planter_run, base_url=base_url, api_token=api_token)
    pg = PlantGeneration(field_id, planter_run, field_number, field_name, planter_run_id, coordinates_for_one_field)

    # Matrix composed of 1s and 0s, 1 denotes an obstacle and 0 a field
    matrix = pg.adj_matrix
    node_edge_point = pg.node_edge_point
    # Currently no in-field obsticles
    node_barrier_point = []
    mc = boustrophedon.Boustrophedon(matrix)
    # Matrix with numbers representing cell decomposition, 1s irepresent obsticales, the other numbers are shiffted + 1 from the visualization
    matrix = mc.final_decomposition()
    # Cell number is the max number of cells present in the cell docomposition
    graph_result = graph.Graph(matrix, mc.cell_number)
    # Nb_cells x Nb_cells interconnection between cells represent through the matrix, at position A_01 = 1 if 1st cell has a connection to 2nd same at A_10 = 1
    matrix_dependencies = graph_result.graph()
    print("Matrix dependencies or graph matrix" + str(matrix_dependencies))

    way_result = way.Way(matrix_dependencies)
    # Order of the cells that need to be visited
    sequence = way_result.DFS_Algorithm()
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

    save_caller(pg, ordered_list_points, base_url=base_url, api_token=api_token)
