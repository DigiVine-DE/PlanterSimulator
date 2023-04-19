# Boustrophedon Cellular Decomposition

This repository contains a basic Coverage Path Planning, with the task of determining a path that passes over all points of a polygon or 3d space while avoiding obstacles.
This task is quite useful to many robotic applications, such as vacuuming robots or autonomous vehicles.
The main goal is to limit the number of times a vehicle passes over an already visited region.
The algorithm implemented for this purpose is Boustrophedon Cell Decomposition (BCD).

This project can be started with **start_bcd** and it performs the following steps, for which the mentioned classes are used.

1. Given a field/polygon, we split the field into a grid like format with cells of a prespecified size (class **PlantGeneration**).

2. Using the BCD the polygon is transformed into cells such that each cell will not contain any obstacle.
All of the cells together constitute the collision-free part of the polygon.
The algorithm creates a matrix with different numbers for the different cells, 1s represent obsticles (class **Boustrophedon**).

3. The vehicle has to traverse one cell entirely before going to the other cell.
But in order to decide on which cell to go to, we need of ordering of the cells.
Using the cell numbers we can formulate a graph from the connections between the cells (class **Graph**).

4. Once we have interconnections between the cells, we can use any algorithm for traversal to find some order to traverse the cells. Currently we have the Breath and Depth first search.
As we can see in the end we have the order of the cells which the vehicle will follow (class **Way**).

When calling `start_bcd.py` the api token and base url can be specified as parameters:

- `python start_bcd.py --api-token 'API-TOKEN' --base-url 'BASE-URL'`

Parts of the code are adapted from https://gitlab.com/Mildoor/boustrophedon.

# Downloading Requirements

To download the required dependencies using **conda** use the provided `project_env.yml` file. 
The `plant_generator` environment can be installed as:

- `conda env create -f project_env.yml`

To activate the installed environment use:

- `conda activate plant-generator`

To deactivate the environment use:
- `conda deactivate`

(If you do not have conda installed, use **pip** to manually install all the libraries from the `project_env.yml` file)
