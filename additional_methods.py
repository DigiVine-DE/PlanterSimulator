import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
import numpy as np
import math, geopy

def animate(matrix, ordered_list_points):
    # This is a trick for the coloring.
    matrix = matrix.astype('float')
    nx = np.shape(matrix)[0]
    ny = np.shape(matrix)[1]
    fig = plt.figure()
    data = np.zeros((nx, ny))
    # hack
    # cmap = plt.cm.gray
    # cmap.set_bad((1, 0, 0, 1))
    im = plt.imshow(matrix, cmap='winter')  # , cmap=cmap)
    plt.axis('off')

    def init():
        im.set_data(matrix)

    def animate(i):
        xi = ordered_list_points[i][0]
        yi = ordered_list_points[i][1]
        # matrix[xi, yi] = None
        matrix[xi, yi] = np.nan
        im.set_data(matrix)
        # print('time ordered')
        # print(matrix_for_time[i])
        return im

    anim = FuncAnimation(fig, animate, init_func=init, frames=len(ordered_list_points),
                         interval=1)
    plt.show()

    # if save_animation:
    #     f = r"animation.mp4" # this is for MP4
    #     writergif = animation.FFMpegWriter(fps=60) # this is for MP4
    #     anim.save(f, writer=writergif)


def create_ordered_list_points(sequence, matrix):
    ordered_list_points = []
    for s in sequence:
        # ids = matrix[matrix == s]
        x, y = np.where((matrix == (s + 1)))
        # ids = np.where(np.all(matrix == s))
        print("=========" + str(s) + "=========")
        x_y_zip = zip(x, y)
        # x_y = [list(a) for a in zip(x, y)]
        x_y = []
        # print(x_y)
        x_y_dict = dict()
        y_x_dict = dict()
        for x_i, y_i in x_y_zip:
            x_y.append(list([x_i, y_i]))
            # this is if we want to go through the xs first
            y_s = []
            if x_i in x_y_dict:
                y_s = x_y_dict[x_i]
            y_s.append(y_i)
            x_y_dict[x_i] = y_s
            # this is if we want to go through the y_s first
            x_s = []
            if y_i in y_x_dict:
                x_s = y_x_dict[y_i]
            x_s.append(x_i)
            y_x_dict[y_i] = x_s

        go_x = True
        if go_x:
            coordinates_dict = x_y_dict
        else:
            coordinates_dict = y_x_dict

        direction = True
        ordered_key_coordinates = [key for key in coordinates_dict]

        for ordered_key_coordinate in ordered_key_coordinates:
            other_coordinates = coordinates_dict[ordered_key_coordinate]
            other_coordinates.sort(reverse=direction)
            for other_coordinate in other_coordinates:
                if go_x:
                    ordered_list_points.append([ordered_key_coordinate, other_coordinate])
                else:
                    ordered_list_points.append([other_coordinate, ordered_key_coordinate])
            direction = not direction

    return ordered_list_points

def create_timestamp_for_plant_generation(plant_generation_given_field_dimensions, list_of_points, tractor_speed, planting_speed):
    time_for_planting_plant = []
    # this is the time when the first plant was planted
    current_time = 1 #datetime.datetime.today().timestamp()
    # the total time for planting
    total_time = 0
    # the last point that was covered
    previous_point = None
    for pos_point, point_in_matrix in enumerate(list_of_points):
        point = plant_generation_given_field_dimensions.get_coordinate(point_in_matrix[0], point_in_matrix[1])
        point = (point.x, point.y)
        if total_time == 0:
            time_for_planting_plant.append(current_time)
            total_time = current_time
        else:
            added_traveling_time = 0
            # distance_between_points = plant_generation_given_field_dimensions.geopy.distance.distance(previous_point, point).meters
            distance_between_points = geopy.distance.distance(previous_point, point).meters
            if distance_between_points > 2*plant_generation_given_field_dimensions.distance_between_crops_vertical \
                    or distance_between_points > 2*plant_generation_given_field_dimensions.distance_between_crops_horizontal:
                crops_distance = plant_generation_given_field_dimensions.distance_between_crops_horizontal
                # if the distance between the plants is larger than the usual plants distance then we need to take into account the time
                # needed for traveling
                added_traveling_time = math.ceil(distance_between_points / crops_distance) * (tractor_speed)

            total_time = total_time + (tractor_speed + planting_speed) + added_traveling_time
            time_for_planting_plant.append(total_time)

        previous_point = point

    return time_for_planting_plant

def get_coordinate(coordinate_matrix, i,j):
    point = coordinate_matrix[i][j]
    return point

def print_field_format(file_name, adj_matrix):
    f_w = open(file_name + ".txt", "w")
    for j in range(adj_matrix.shape[1]):
        for i in range(adj_matrix.shape[0]):
            if adj_matrix[i][j] == 1:
                f_w.write(" ")
            else:
                f_w.write("-")
        f_w.write("\n")
    f_w.close()
    print(adj_matrix)


def plot_sample_execution(width, height, coords, geojson_field_polygon,min_x, min_y, coordinate_matrix, adj_matrix):
    plt.xlim([-100, width + 100])
    plt.ylim([-100, height + 100])

    x = coords[0]
    y = coords[1]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.add_patch(Rectangle((0, 0), width, height, fc='None', ec='g', lw=1))

    graph, = plt.plot([], [], 'o')

    def animate(i):
      graph.set_data(x[:i+1], y[:i+1])
      return graph

    # plt.plot(width, height)
    # these are the actual boundaries
    plt.plot(geojson_field_polygon.exterior.xy[0] - np.array(min_x),
             geojson_field_polygon.exterior.xy[1] - np.array(min_y))


    # here we draw the points
    scat = plt.scatter(coords[0], coords[1], s=0.1, c='r')
    ani = FuncAnimation(fig, animate)
    plt.show()

    '''
        go over the actual points as coordinates that 
        are in the polygon representing the field 
    '''
    how_many = 0
    set_of_points = set()
    for pos_x in range(len(coordinate_matrix)):
        for pos_y in range(len(coordinate_matrix[0])):
            if adj_matrix[pos_x][pos_y] == 0: # this check says that the point is actualy in the field, so if adj_matrix returns 0 the point is in the field
                point_taken = get_coordinate(pos_x, pos_y)
                # print(point_taken)
                set_of_points.add(str(point_taken.x) + '-' + str(point_taken.y))
                how_many += 1

    print('Total num of points: %d ' % how_many)
    print('Total num of points in set: %d ' % len(set_of_points))
    print('Total num of x coordinates: %d' % len(coords[0]))
    print('Total num of y coordinates: %d' % len(coords[1]))
    # HTML(ani.to_html5_video())
    get_coordinate(coordinate_matrix, 0,0)
