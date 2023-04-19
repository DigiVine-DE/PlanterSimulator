import numpy as np
from itertools import groupby

class Boustrophedon:
    """
    Calculates the points of individual cells (Boustrophedon decomposition) and returns them in the shortest order, so that the path for the robot is the shortest.
    The input is a matrix (environment) with obstacles. The output is a matrix with different numbers per each cell and 1 for obsticles.
    """
    def __init__(self, matrix):
        self.__matrix = matrix
        self.__edge_space = 1   # representation of an obstacle in a matrix
        self.__free_space = 0   # representation of the clearing area
        self.update(start=True)


    def update(self, start = False):
        """
        Updates the status of both lines after checking them in the final_decomposition function
        """
        self.__line_number = 0 if start else self.__line_number + 1 # coordinates of the obstacle being searched
        if not start:
            self.__get_next_lines()
        else:
            # from the first one
            self.__line_one = []  # field in the previous step of the inspected line
            self.__line_two = []  # the field of the line being checked
            self.__cell_number = 1  # the highest cell
            self.__pervious_cell_list = []  # the order of the cells in the previous step

        self.__obstacles_one = 0 if start else self.number_of_obstacles(self.__line_one) # number of obstacles in line one
        self.__obstacles_two = 0 if start else self.number_of_obstacles(self.__line_two) # number of obstacles in line two (currently being searched)

        self.__obstacles_one_list = [] if start else self.coordinate_of_obstacles(self.__line_one) # coordinates of obstacles in line one
        self.__obstacles_two_list = [] if start else self.coordinate_of_obstacles(self.__line_two) # coordinates of obstacles in line two

        self.__cell_one = self.__obstacles_one - 1 # number of local cells in line one
        self.__cell_two = self.__obstacles_two - 1 # number of local cells in line two

        self.__cell_one_list = [] if start else self.coordinate_of_cells(self.__line_one) # coordinates of local cells in line 1
        self.__cell_two_list = [] if start else self.coordinate_of_cells(self.__line_two) # coordinates of local cells in line 2

        self.__delta_of_obstacles = self.__obstacles_two - self.__obstacles_one
        self.__discontinuity = [] if start else self.discontinuous_sets(self.__obstacles_one_list, self.__obstacles_two_list) # an obstacle number (in line 2) that is not continuous with the obstacles from line one
        self.__relative_continuity = False if start else self.relative_continuity(self.__obstacles_one_list, self.__obstacles_two_list) # True - each obstacle in line two is continuous with one of the obstacles in line one
        self.__absolute_continuity = False if start else self.absolute_continuity(self.__obstacles_one_list, self.__obstacles_two_list) # True - the first (line 1) is continuous with the first (line2) obstacle, the second with the second ...

        self.__state = {
                "Beginning": ( self.__obstacles_two >= 1 and self.__cell_one == 0),
                "MoreObst_Discont": ( self.__obstacles_two >= self.__obstacles_one and self.__cell_one != 0 and not self.__relative_continuity),
                "MoreObst_RelContin": ( self.__obstacles_two >= self.__obstacles_one and self.__cell_one != 0 and self.__relative_continuity),
                "EquObst_AbsContin":    (self.__obstacles_one == self.__obstacles_two and self.__absolute_continuity and self.__cell_two != 0 ),
                "LessObst": (self.__obstacles_two < self.__obstacles_one),
                "End": (self.__obstacles_one != 0 and self.__obstacles_two == 0)
                }

    @property
    def cell_number(self):
        return self.__cell_number

    def __get_next_lines(self):
        """
        Increases the position of both lines
        """
        if self.__line_number >= self.__matrix.shape[1]:
            self.__line_one = self.__line_two
        else:
            self.__line_one = self.__matrix[:, self.__line_number - 1]
            self.__line_two = self.__matrix[:, self.__line_number]


    def number_of_obstacles(self, list):
        """
        Returns the number of obstacles in a sheet field
        """
        nonduplicates = [key for key, _group in groupby(list)]
        return nonduplicates.count(1)

    def coordinate_of_element(self, list, obstacle):
        return_list = []
        sublist = []

        number = 0
        control_one = False
        control_two = False

        for i in list:
            control_two = control_one
            control_one = (i == self.__edge_space) if obstacle else (i != self.__edge_space)

            if (control_one and (not control_two)):
                sublist.append(number)

            elif ((not control_one) and control_two):
                sublist.append(number - 1)
                return_list.append(sublist)
                sublist = []

            number = number + 1

        if obstacle:
            sublist.append(number - 1)
            return_list.append(sublist)

        return return_list

    def coordinate_of_obstacles(self,list):
        """
        Returns the field of extreme coordinates of all obstacles in the sheet field
        """

        return self.coordinate_of_element(list, obstacle=True)

    def coordinate_of_cells(self, list):
        """
        Returns the field of the extreme coordinates of all cells in the sheet field
        """

        return self.coordinate_of_element(list, obstacle=False)


    def check_connection(self, list_one, list_two, i, j):
        return (((list_one[i][0] <= list_two[j][0]) and (list_two[j][0] <= list_one[i][1])) or
               ((list_one[i][0] <= list_two[j][1]) and (list_two[j][1] <= list_one[i][1]))) or \
               (((list_two[j][0] <= list_one[i][0]) and (list_one[i][0] <= list_two[j][1])) or
               ((list_two[j][0] <= list_one[i][1]) and (list_one[i][1] <= list_two[j][1])))


    def absolute_continuity(self, list_one, list_two):
        """
        Checks whether the second line (list_two) is absolutely continuous with line one (list_one)
        """
        if len(list_one) != len(list_two):
            return False
        else:
            iterator = 0
            while(iterator < len(list_two)):
                if not self.check_connection(list_one, list_two, iterator, iterator):
                    return False
                iterator = iterator + 1
        return True



    def connection_sublist(self, list_one, list_two):
        connection = []
        sublist = []

        for i in range(len(list_one)):
            for j in range(len(list_two)):
                if self.check_connection(list_one, list_two, i, j):
                    sublist = [i, j]
                if sublist != []:
                    connection.append(sublist)
                    sublist = []
        return connection, sublist


    def check_loop(self, len_list, connection, elem):
        loop = True
        for i in range(len_list):
            for j in range(len(connection)):
                if i == connection[j][elem]:
                    loop = True
                    break
                else:
                    loop = False

            if not loop:
                break
        return loop


    def relative_continuity(self, list_one, list_two):
        """
        Checks whether the second line is relatively continuous with line one
        """

        connection, sublist = self.connection_sublist(list_one, list_two)
        loop1 = self.check_loop(len(list_one), connection, 0)
        loop2 = self.check_loop(len(list_two), connection, 1)
        return (loop1 and loop2)

    def discontinuous_sets(self, list_one, list_two):
        """
        Returns obstacles (their position within a line) in a line that are discontinuous
        """

        connection, sublist = self.connection_sublist(list_one, list_two)

        discontinuity = []
        set = True
        for i in range(len(list_two)):
            for j in range(len(connection)):
                if i == connection[j][1]:
                    set = True
                    break
                else:
                    set = False

            if(not set):
                discontinuity.append(i)

        return discontinuity

    def fill_cell(self, number_of_cell, fill):
        """
        Fills the local cell (number of cell -to from above) with the number (fill)
        """
        for i in range(self.__cell_two_list[number_of_cell][1] - self.__cell_two_list[number_of_cell][0] + 1):
            self.__matrix[self.__cell_two_list[number_of_cell][0] + i][self.__line_number] = fill


    def is_cell_continuity(self, cellone, celltwo):
        return (( (cellone[0] <= celltwo[0]) and (celltwo[0] <= cellone[1])) or ( (cellone[0] <= celltwo[1]) and (celltwo[1] <= cellone[1])) )\
                    or (( (celltwo[0] <= cellone[0]) and (cellone[0] <= celltwo[1])) or ( (celltwo[0] <= cellone[1]) and (cellone[1]<= celltwo[1])) )

    def final_decomposition(self):
        """
        Performs Boustrophedon decomposition (divides space into cells)
        """
        while(self.__line_number < self.__matrix.shape[1]-1):
            self.update()

            if(self.__state["EquObst_AbsContin"]):            #
                for i in range(len(self.__pervious_cell_list)):
                    self.fill_cell(i, self.__pervious_cell_list[i])
            elif(self.__state["MoreObst_Discont"]):       # More or less obstacles that are discontinuous
                one = True
                sec = False
                actual = []
                num = 0

                for i in range(1, self.__obstacles_two):
                    sec = one
                    one = True
                    for j in self.__discontinuity:          # I find a discontinuity here
                        if i == j:
                            one = False
                            break

                    if sec and one:       # if the first and second obstacles in line two are continuous
                        if(self.is_cell_continuity(self.__cell_one_list[num], self.__cell_two_list[i-1])):
                            jump = 0
                            for k in range(num, self.__cell_one):
                                if(self.__cell_two_list[i-1][1] >= self.__cell_one_list[k][0]):
                                    jump = jump + 1

                            if jump == 1:
                                self.fill_cell(i-1, self.__pervious_cell_list[num])
                                actual.append(self.__pervious_cell_list[num])
                            else:

                                self.__cell_number = self.__cell_number + 1
                                self.fill_cell(i-1, self.__cell_number)
                                actual.append(self.__cell_number)

                            num = num + jump

                        elif self.__cell_two_list[i-1][1] < self.__cell_one_list[num][0]:
                            self.__cell_number = self.__cell_number + 1
                            actual.append(self.__cell_number)               # assigns it to a new list
                            self.fill_cell(i-1, self.__cell_number)

                    else:   # when two consecutive obstacles are not continuous
                        self.__cell_number = self.__cell_number + 1     # assigns a new cell
                        actual.append(self.__cell_number)               # assigns it to a new list
                        self.fill_cell(i-1, self.__cell_number)         #  And fill it

                        for k in range(num, self.__cell_one):
                            if(self.__cell_two_list[i-1][1] >= self.__cell_one_list[k][0]):
                                num = num + 1

                self.__pervious_cell_list = actual

            elif self.__state["MoreObst_RelContin"]:   # more obstacles that are relatively continuous
                disc_cell = self.discontinuous_sets(self.__cell_one_list, self.__cell_two_list)
                discontinuous_cell = False

                for i in range(self.__cell_two):
                    discontinuous_cell = False
                    for j in disc_cell:
                        if(i == j):
                            discontinuous_cell = True
                            break
                        # else:
                        #     discontinuous_cell = False

                    if discontinuous_cell:
                        self.__cell_number = self.__cell_number + 1
                        self.__pervious_cell_list.insert(i, self.__cell_number)
                        self.fill_cell(i, self.__pervious_cell_list[i])
                    else:
                        self.fill_cell(i, self.__pervious_cell_list[i])

            elif self.__state["LessObst"]: # fewer obstacles
                one = True
                sec = False
                actual = []
                num = 0
                add = 0

                for i in range(1,self.__obstacles_two):
                    newadd = 0
                    sec = one
                    one = True
                    for j in self.__discontinuity:  # finds a connection
                        if(i == j):
                            one = False
                            break
                        # else:
                        #     one = True

                    for k in range(num, len(self.__cell_one_list)):
                        cell = self.__cell_one_list[k]
                        if(cell[1] < self.__cell_two_list[i-1][0]):
                            if(add + 1 <= (self.__cell_one - self.__cell_two)):
                                add = add + 1
                                newadd = newadd + 1

                    if (sec and one):
                        end_obst = 0
                        for obst in self.__obstacles_one_list:
                            if( obst[0] > self.__obstacles_two_list[i-1][1] and obst[1] < self.__obstacles_two_list[i][0]  ):
                                end_obst = end_obst + 1
                                if( obst[0] > self.__obstacles_two_list[i][1]):
                                    break

                        if end_obst == 0:
                            num = num + newadd
                            self.fill_cell(i-1, self.__pervious_cell_list[num])  # i-1 because I'm filling in a cell and it has one lower number
                            actual.append(self.__pervious_cell_list[num])
                            num = num + 1
                            end_obst = 0
                        else:
                            num = num + newadd + end_obst + 1
                            self.__cell_number = self.__cell_number + 1
                            self.fill_cell(i-1, self.__cell_number)
                            actual.append(self.__cell_number)
                            end_obst = 0

                    else:
                        self.__cell_number = self.__cell_number + 1
                        actual.append(self.__cell_number)
                        self.fill_cell(i-1, self.__cell_number)


                        for k in range(num, self.__cell_one):
                            if(self.__cell_two_list[i-1][1] >= self.__cell_one_list[k][0]):
                                num = num + 1
            

                self.__pervious_cell_list = actual

            elif self.__state["Beginning"]:        # initial provisions
                if self.__cell_two >= 1:
                    for i in range(self.__cell_two):
                        self.__cell_number = self.__cell_number + 1
                        self.__pervious_cell_list.append(self.__cell_number)
                        self.fill_cell(i, self.__cell_number)

        return self.__matrix