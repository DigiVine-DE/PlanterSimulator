import numpy as np

class Way:
    """
    This class creates a graph list from a graph matrix. The graph matrix contains correlation
    between cells, whereas the graph list the indices of the correlations.
    """
    def __init__(self, graph_matrix):
        self.__graph_matrix = graph_matrix
        self.__graph_list = self.transfer(self.__graph_matrix)

    def transfer(self, matrix):
        return ([list([int(t + 1) for t in np.argwhere(matrix[y] == 1)]) for y in range(matrix.shape[0])])

    def DFS_Algorithm(self, vertex = 1, path = []):
        path.append(vertex)
        for neighbor in self.__graph_list[vertex-1]:
            if neighbor not in path:
                path = self.DFS_Algorithm(neighbor, path)
        return path
   
    def BFS_Algorithm(self, out=[1]):
        for i in self.__graph_list[0]:
            out.append(i)
        
        for nodes in out:
            if len(out) == len(self.__graph_list):
                return out
            for cell in self.__graph_list[nodes-1]:
                if cell in out:
                    pass
                else:
                    out.append(cell)
