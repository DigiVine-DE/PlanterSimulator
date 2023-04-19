import numpy as np

class Graph:
    """
    Creation of the graph matrix containing the interconnections between the boustrophedon cells.
    """
    def __init__(self, matrix, cell_number):
        self.__matrix = matrix
        self.__cell_number = cell_number - 1

        self.__graph_matrix = np.full((self.__cell_number, self.__cell_number), 0)
        self.__line_number = 0

        self.__line_one = []
        self.__line_two = []

    def __get_next_lines(self):
        """
        Increases the position of both lines
        """
        self.__line_number = self.__line_number + 1

        if self.__line_number >= self.__matrix.shape[1]:
            self.__line_one = self.__line_two
        else:
            self.__line_one = self.__matrix[:, self.__line_number - 1]
            self.__line_two = self.__matrix[:, self.__line_number]

    def graph(self):
        while self.__line_number < (self.__matrix.shape[1]-1):
            self.__get_next_lines()
            not_equal = np.where(self.__line_one != self.__line_two)
            pack = np.array(list(zip(self.__line_one[not_equal], self.__line_two[not_equal])))
            pack = np.unique(pack, axis=0)
            for x1,x2 in pack:
                if not (x1 == 1 or x2 == 1):# Check if needed or (self.__graph_matrix[x1 - 2][x2 - 2] == 1)):
                    self.__graph_matrix[x1 - 2][x2 - 2] = 1
                    self.__graph_matrix[x2 - 2][x1 - 2] = 1
        return self.__graph_matrix