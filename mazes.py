from __future__ import division 
import ezdxf

class Maze:
    class Node:
        def __init__(self, position):
            self.Position = position
            self.Neighbors = [None, None, None, None]

    def __init__(self, input_file):
    
        # ****** Getting data from Dxf *********
        # Importing the dxf
        print("Loading Dxf")
        dxf_doc = ezdxf.readfile(input_file)
        dxf_msp = dxf_doc.modelspace()

        unfrozen_layers = []
        for layer in dxf_doc.layers:
            if(layer.is_frozen() == False):
                unfrozen_layers.append(layer)

        unfrozen_layers_names = []
        for layer in unfrozen_layers:
            # print(layer.dxf.name)
            # print(layer.is_frozen())
            unfrozen_layers_names.append('layer == "' + layer.dxf.name + '"')

        query_str = ' | '.join(unfrozen_layers_names)
        # print(query_str)
        # print('LINE[{}]'.format(query_str))

        # Lines are only from unfrozen layers
        lines = dxf_msp.query('LINE[{}]'.format(query_str))

        # uncomment to see lines
        # for e in lines:
        #     _print_entity(e)
        
        # *********** end of dxf import ***************

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
            
        lines_horizontal = []
        lines_vertical = []
        lines_diagnoal = []

        for line in lines:
            if(_isHoriz(line.dxf.start, line.dxf.end)):
                lines_horizontal.append(line)
            elif(_isVert(line.dxf.start, line.dxf.end)):
                lines_vertical.append(line)
            elif(_isDiag(line.dxf.start, line.dxf.end)):
                lines_diagnoal.append(line)

        print('there are ', len(lines),' lines ')
        print('there are ', len(lines_horizontal), 'horizontal lines')
        print('there are ', len(lines_vertical), 'vertical lines')
        print('there are ', len(lines_diagnoal), 'diagonal lines')

        # ***** testing zone below *****

        # Testing for intersection and line direction
        test_node1 = Maze.Node((2700, 0))
        test_node2 = Maze.Node((2800, 3500))
        test_line = lines[0]

        print(test_line.dxf.start)
        print(test_line.dxf.end)
        print(test_node1.Position)
        print(test_node2.Position)

        print('does it intersect? ',_intersect(
            (test_node1.Position[0], test_node1.Position[1]),
            (test_node2.Position[0], test_node2.Position[1]),
            (test_line.dxf.start[0], test_line.dxf.start[1]),
            (test_line.dxf.end[0], test_line.dxf.end[1])
            ))

        print('is horizontal? ',_isHoriz(
            (test_node1.Position[0], test_node1.Position[1]),
            (test_node2.Position[0], test_node2.Position[1])
        ))

        print('is vert? ',_isVert(
            (test_node1.Position[0], test_node1.Position[1]),
            (test_node2.Position[0], test_node2.Position[1])
        ))

        print('is diagonal? ',_isDiag(
            (test_node1.Position[0], test_node1.Position[1]),
            (test_node2.Position[0], test_node2.Position[1])
        ))

def _print_entity(e):
    print("LINE on layer: %s\n" % e.dxf.layer)
    print("start point: %s\n" % e.dxf.start)
    print("end point: %s\n" % e.dxf.end)

# from; https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
def _ccw(pos1, pos2, pos3):
    return (pos3[1] - pos1[1]) * (pos2[0] - pos1[0]) > (pos2[1] - pos1[1]) * (pos3[0] - pos1[0])

def _intersect(pos1, pos2, pos3, pos4):
    return _ccw(pos1, pos3, pos4) != _ccw(pos2, pos3, pos4) and _ccw(pos1, pos2, pos3) != _ccw(pos1, pos2, pos4)

def _xdiff(pos1, pos2):
    return pos1[0] - pos2[0]

def _ydiff(pos1, pos2):
    return pos1[1] - pos2[1]

def _isHoriz(pos1, pos2):
    return abs(_xdiff(pos1, pos2)) > .1 and abs(_ydiff(pos1, pos2)) < 0.1

def _isVert(pos1, pos2):
    return abs(_xdiff(pos1, pos2)) < .1 and abs(_ydiff(pos1, pos2)) > 0.1

def _isDiag(pos1, pos2):
    return abs(_xdiff(pos1, pos2)) > .1 and abs(_ydiff(pos1, pos2)) > 0.1
