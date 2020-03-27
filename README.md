# Dxf Reader and Graph Solver
#### Author: James Dansie

This repo is to read in dxf floor plan, then convert it into a maze/graph that can be solved to find paths through.

## Setup
Needs the ezdxf dependency to read images. 
To run from the command line; ```py solve.py ./floorPlans/FloorPlanSample.dxf ./ans/Answer.dxf -m depthfirst```  
This will run a depth first on the combo400.png file. The -m argument is optional. Default is breadth first. Possible choices are; leftturn, breadthfirst, depthfirst, dijkstra, and astar.

### Dependencies
* ezdxf - https://pypi.org/project/ezdxf/

### References/Sources
* Mike Pound's original maze solutions; https://github.com/mikepound/mazesolving
https://www.youtube.com/watch?v=rop0W4QDOUI&feature=youtu.be
* SampleFloorPlan.dxf/dwg is just the sample floor plan that comes with autocad 2020.