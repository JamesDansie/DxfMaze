class Maze:
    class Node:
        def __init__(self, position):
            self.Position = position
            self.Neighbors = [None, None, None, None]

    def __init__(self, dxf_doc):
        



    # okay, so game plan (aka algo)
    # 1) make a list of all horizontal and vertical lines 
    #     1.1) store horiz and vert lines seperate
    #     1.2) keep track of max and min of x,y points
    # 2) prompt the user for a starting and end point
    # 3) start making the maze/graph 
    #     3.2) go through the doc and make a node in 1ft increments from min to max
    #     3.3) make an edge, and check to see if it crosses a line
    #         3.3.1) All horizontal edges check vertical lines, all vertical edges check horizontal lines
    #     3.4) if edge does not cross a line then make the edge, else don't make the edge
    # 4) go solve it!

    # ***** ntesting zone below *****
    # From ezdxf tutorial
    # iterate over all entities in modelspace
    msp = dxf_doc.modelspace()
    for e in msp:
        if e.dxftype() == 'LINE':
            print_entity(e)

    # entity query for all LINE entities in modelspace
    for e in msp.query('LINE'):
        print_entity(e)

    def print_entity(e):
        print("LINE on layer: %s\n" % e.dxf.layer)
        print("start point: %s\n" % e.dxf.start)
        print("end point: %s\n" % e.dxf.end)
