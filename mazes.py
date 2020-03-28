from __future__ import division 
import ezdxf

class Maze:
    class Node:
        def __init__(self, position):
            self.Position = position
            self.Neighbors = [None, None, None, None]
            # Neighbor[0] is up
            # Neighbor[1] is right
            # Neighbor[2] is down
            # Neighbor[3] is left

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

        xmin = xmax = lines[0].dxf.start[0]
        ymin = ymax = lines[0].dxf.start[0]

        for line in lines:
            xmin = min(xmin, line.dxf.start[0], line.dxf.end[0])
            xmax = max(xmax, line.dxf.start[0], line.dxf.end[0])
            ymin = min(ymin, line.dxf.start[1], line.dxf.end[1])
            ymax = max(ymax, line.dxf.start[1], line.dxf.end[1])

            # Sorting lines in vertical, horizontal and diagonal
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
        print('the min pt is ({},{})'.format(xmin, ymin))
        print('the max pt is ({},{})'.format(xmax, ymax))

        # Starting and ending points
        # Eventually replace with user prompts 

        xstart = 120
        ystart = 230
        xend = 256
        yend = 128
        self.start = None
        self.end = None

        # ******* Making Nodes/Graph **********

        # Rounding to the nearest ft, this will make sure the start and end node positions are included.
        xmin_ft = xcounter_ft = round(xmin/12)
        ymin_ft = ycounter_ft = round(ymin/12)
        xmax_ft = round(xmax/12)
        ymax_ft = round(ymax/12)
        node_increment_ft = 1
        nodes = []

        print('xcounter: ',xcounter_ft,' xmax ',xmax_ft)

        while ycounter_ft < ymax_ft:
        
            xcounter_ft = xmin_ft
            nodes_row = []
            prev = None

            while xcounter_ft < xmax_ft:                
                curr = Maze.Node((xcounter_ft, ycounter_ft))
                print(curr.Position)
                dxf_msp.add_circle(curr.Position, 0.3)
                # curr adds the previous node to the left
                
                if(
                    prev != None and 
                    _intersect_lines(lines_vertical, curr.Position, prev.Position) and
                    _intersect_lines(lines_diagnoal, curr.Position, prev.Position)
                    ):
                    # the previous node to the left adds the current node to the right if there's no walls in the way
                    curr.Neighbors[3] = prev
                    prev.Neighbors[1] = curr
                    dxf_msp.add_line(curr.Position, prev.Position)

                # if(ycounter_ft != ymin_ft):


                if(xcounter_ft == xstart and ycounter_ft == ystart):
                    #found start node
                    self.start = curr
                elif(xcounter_ft == xend and ycounter_ft == yend):
                    #found end node
                    self.end = curr

                nodes_row.append(curr)
                prev = curr
                xcounter_ft += node_increment_ft

            nodes.append(nodes_row)
            ycounter_ft += node_increment_ft

        dxf_doc.save()
        dxf_doc.saveas('nodes.dxf')
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

        print('intersect horizontal lines? ', _intersect_lines(
            lines_horizontal,
            test_node1.Position,
            test_node2.Position
        ))

def _intersect_lines(lines, pos1, pos2):
    for line in lines:
        if(_intersect(
            (line.dxf.start[0], line.dxf.start[1]),
            (line.dxf.end[0], line.dxf.end[1]),
            pos1, pos2
        )): return True
    return False

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
