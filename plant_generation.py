import datetime, math, geopy, geopy.distance, numpy as np
from shapely.geometry import Polygon, Point
from haversine import haversine, Unit


class PlantGeneration:
    '''
    This class generates a mapping between the coordinates of the polygon and a prespecified grid structure with fixed grid cell size in mm.
    More specifically a polygon with coordinate boundaries is sent, the coordinates are adequately split in a grid structure,
    later transformed into a matridx of 1s and 0s.
    '''
    def __init__(self, field_id, planter_run, field_number, field_name, planter_run_id, coordinates_for_field):
        # Distance between crops is in METERS
        self.distance_between_crops_horizontal = 1
        self.distance_between_crops_vertical = 1
        # Distance in mm
        self.distance_rows = 2000
        self.distance_plants = 1000
        self.field_id = field_id
        self.planter_run = planter_run
        self.field_number = field_number
        self.field_name = field_name
        self.planter_run_id = planter_run_id
        self.coordinates_for_field = coordinates_for_field

        # added
        self.row_number = 1
        self.previous_x = -1

        self.read_plant()

    def read_plant(self):
        # create geojson polygon
        geojson_field_polygon = Polygon(self.coordinates_for_field)
        self.node_edge_point = []
        # for x,y in zip(x_scaled,y_scaled):
        #     print(str(x) + "," + str(y))
        #     node_edge_point.append([x,y])

        coordinates_for_one_field = np.array(self.coordinates_for_field)
        print('coordinates')
        print(coordinates_for_one_field)

        # take the minimum and the maximum coordinate of the field
        min_x = min(coordinates_for_one_field[:,0])
        min_y = min(coordinates_for_one_field[:,1])
        max_x = max(coordinates_for_one_field[:,0])
        max_y = max(coordinates_for_one_field[:,1])
        # take the index of the minimum and the maximum x and use them later on for calculating the width in meters
        min_x_index = np.where(coordinates_for_one_field[:,0] == min_x)[0][0]
        max_x_index = np.where(coordinates_for_one_field[:,0] == max_x)[0][0]
        # take the index of the minimum and the maximum y and use them later on for calculating the height in meters
        min_y_index = np.where(coordinates_for_one_field[:,1] == min_y)[0][0]
        max_y_index = np.where(coordinates_for_one_field[:,1] == max_y)[0][0]

        print('min_x_index %d ; max_x_index %d ' % (min_x_index.item(), max_x_index.item()))
        print('min x:%f, min y:%f - max x:%f,max-y:%f' % (min_x,min_y,max_x,max_y))
        print('complete min_x '+ str(coordinates_for_one_field[min_x_index]))
        print('complete max_x' + str(coordinates_for_one_field[max_x_index]))

        # get the width and the height of the field
        width = max_x - min_x
        height = max_y - min_y

        print('width' + str(width))
        print('height'+ str(height))
        print('field size' + str(min_x + width))

        # using the vincenity distance
        vincenity_distance_width = geopy.distance.distance(coordinates_for_one_field[min_x_index], coordinates_for_one_field[max_x_index]).meters
        vincenity_distance_height = geopy.distance.distance(coordinates_for_one_field[min_y_index], coordinates_for_one_field[max_y_index]).meters
        print('vincenty distance width ' + str(vincenity_distance_width) + 'vincenty distance height ' + str(vincenity_distance_height))

        # using the haversine distance
        haversine_distsance_width = haversine(coordinates_for_one_field[min_x_index], coordinates_for_one_field[max_x_index], unit=Unit.METERS)
        haversine_distsance_height = haversine(coordinates_for_one_field[min_y_index], coordinates_for_one_field[max_y_index], unit=Unit.METERS)
        print('harverstein distance width ' + str(haversine_distsance_width) + 'harverstein distance height ' + str(haversine_distsance_height))
        # TODO Comment: Vincenity seems to be more precise so this is our choice for calculating the distance


        # divide the width/height of the field with the distance between crops to get the num of crops per line
        num_points_for_x_axis = math.ceil(vincenity_distance_width / self.distance_between_crops_horizontal)
        num_points_for_y_axis = math.ceil(vincenity_distance_height / self.distance_between_crops_vertical)
        # print geojson Polygon
        print(geojson_field_polygon)

        # x = np.linspace(min_x, min_x + width, num_points_for_x_axis)
        x = np.linspace(min_x, max_x, num_points_for_x_axis)

        # y = np.linspace(min_y, min_y + height, num_points_for_y_axis)
        y = np.linspace(min_y, max_y, num_points_for_y_axis)
        # x and y coordinates

        print(x)
        print()
        print(y)
        # exit(1)
        coords = [[], []]

        # rhis is the part where we normalize
        self.adj_matrix = np.zeros([x.shape[0], y.shape[0]])
        self.coordinate_matrix = [[Point()] * y.shape[0] for _ in range(x.shape[0])]
        self.time_for_plant_matrix = np.zeros([x.shape[0], y.shape[0]])

        first_plant_planting = True
        self.speed_of_tractor = 1.3 # the speed of the tractor is in seconds (or it represents the time for moving from one to the other plant)
        self.time_needed_for_planting = 8 # the time needed for planting the plant (in seconds)
        current_time = datetime.datetime.today().timestamp()
        # with this variable we'll regulate the correct order of planting
        # once a row/column is full the tractor needs to continue from the same position
        even_plant = True
        increase_by = 1
        tmp_plants_for_time = []
        tmp_plants_for_time_position = []


        i_int = 0
        np.set_printoptions(threshold=np. inf)
        for i in x:
            j_int = 0
            for j in y:
                point = Point((i, j))
                if geojson_field_polygon.contains(point):
                    coords[0].append(i - min_x)
                    coords[1].append(j - min_y)
                    self.adj_matrix[i_int][j_int] = 0
                    # if this is the first plant that is planted take the current time
                    if first_plant_planting:
                        current_time = 1 #datetime.datetime.today().timestamp()
                        self.time_for_plant_matrix[i_int][j_int] = current_time
                        first_plant_planting = False

                    # if it is an even plant then just store the data
                    if even_plant == False:
                        tmp_plants_for_time_position.append([i_int, j_int])
                        tmp_plants_for_time.append(increase_by)
                    else:
                        self.time_for_plant_matrix[i_int][j_int] = increase_by * (self.speed_of_tractor + self.time_needed_for_planting) + current_time
                    increase_by += 1

                else:
                    self.adj_matrix[i_int][j_int] = 1
                # always adding the points, need to do a double check to remove the points
                # that are not in the field, i.e., remove all points for which adj_matrix returns 1
                self.coordinate_matrix[i_int][j_int] = point
                j_int += 1
            i_int += 1

            for tmp_pos, elem in enumerate(tmp_plants_for_time_position):
                time_for_position_reverse = tmp_plants_for_time[len(tmp_plants_for_time)-tmp_pos-1]
                self.time_for_plant_matrix[elem[0]][elem[1]] = time_for_position_reverse * (self.speed_of_tractor + self.time_needed_for_planting) + current_time

            even_plant = not even_plant
            tmp_plants_for_time_position = []
            tmp_plants_for_time = []


    def get_coordinate(self, i,j):
        point = self.coordinate_matrix[i][j]
        return point
