from __future__ import division 
from math import floor
import ezdxf
import time

class Maze:
    class Node:
        def __init__(self, position):
            self.Position = position
            self.Neighbors = [None, None, None, None]
            # Neighbor[0] is up
            # Neighbor[1] is right
            # Neighbor[2] is down
            # Neighbor[3] is left

        def __repr__(self):
            return '({0}, {1})'.format(self.Position[0], self.Position[1])

    class Line:
        def __init__(self, position1, position2):
            self.Position1 = position1
            self.Position2 = position2

        def __repr__(self):
            return '({0}, {1})'.format(self.Position1, self.Position2)

    def __init__(self, input_file, output_file):
        t0 = time.time()
        # ****** Getting data from Dxf *********
        # Importing the dxf
        print("Loading Dxf")
        dxf_doc = ezdxf.readfile(input_file)
        dxf_msp = dxf_doc.modelspace()
        units_dic = {
            0:	'Unitless',
            1:	'Inches',
            2:	'Feet',
            3:	'Miles',
            4:	'Millimeters',
            5:	'Centimeters',
            6:	'Meters',
            7:	'Kilometers',
            8:	'Microinches',
            9:	'Mils',
            10:	'Yards',
            11:	'Angstroms',
            12:	'Nanometers',
            13:	'Microns',
            14:	'Decimeters',
            15:	'Decameters',
            16:	'Hectometers',
            17:	'Gigameters',
            18:	'Astronomical units',
            19:	'Light years',
            20:	'Parsecs',
            21:	'US Survey Feet',
            22:	'US Survey Inch',
            23:	'US Survey Yard',
            24:	'US Survey Mile'
            }

        unfrozen_layers = []
        for layer in dxf_doc.layers:
            if(layer.is_frozen() == False):
                unfrozen_layers.append(layer)

        unfrozen_layers_names = []
        for layer in unfrozen_layers:
            unfrozen_layers_names.append('layer == "' + layer.dxf.name + '"')

        query_str = ' | '.join(unfrozen_layers_names)

        # Lines are only from unfrozen layers
        # polylines = dxf_msp.query('LWPOLYLINE')
        lines = dxf_msp.query('LINE[{}]'.format(query_str))
        polylines = dxf_msp.query('LWPOLYLINE[{}]'.format(query_str))
        
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
        lines_diagonal = []

        xmin = xmax = lines[0].dxf.start[0]
        ymin = ymax = lines[0].dxf.start[0]

        for line in lines:
            xmin = xcounter = min(xmin, line.dxf.start[0], line.dxf.end[0])
            ymin = ycounter = min(ymin, line.dxf.start[1], line.dxf.end[1])
            xmax = max(xmax, line.dxf.start[0], line.dxf.end[0])
            ymax = max(ymax, line.dxf.start[1], line.dxf.end[1])

            new_line = Maze.Line(line.dxf.start, line.dxf.end)
            # Sorting lines in vertical, horizontal and diagonal
            if(_isHoriz(line.dxf.start, line.dxf.end)):
                lines_horizontal.append(new_line)
            elif(_isVert(line.dxf.start, line.dxf.end)):
                lines_vertical.append(new_line)
            elif(_isDiag(line.dxf.start, line.dxf.end)):
                lines_diagonal.append(new_line)

        for polyline in polylines:
            points = polyline.get_points()
            for i in range(1, len(points)):
                new_line = Maze.Line(points[i-1], points[i])

                xmin = xcounter = min(xmin, new_line.Position1[0], new_line.Position2[0])
                ymin = ycounter = min(ymin, new_line.Position1[1], new_line.Position2[1])
                xmax = max(xmax, new_line.Position1[0], new_line.Position2[0])
                ymax = max(ymax, new_line.Position1[1], new_line.Position2[1])

                if(_isHoriz(new_line.Position1, new_line.Position2)):
                    lines_horizontal.append(new_line)
                elif(_isVert(new_line.Position1, new_line.Position2)):
                    lines_vertical.append(new_line)
                elif(_isDiag(new_line.Position1, new_line.Position2)):
                    lines_diagonal.append(new_line)

        print('there are: ',len(polylines),' polylines')
        print('there are ', len(lines),' lines ')
        print('there are ', len(lines_horizontal), 'horizontal lines')
        print('there are ', len(lines_vertical), 'vertical lines')
        print('there are ', len(lines_diagonal), 'diagonal lines')
        print('the min pt is ({},{})'.format(xmin, ymin))
        print('the max pt is ({},{})'.format(xmax, ymax))
        see_nodes_str = input("Would you like to see nodes and edges? (y/N)")
        self.see_nodes_bool = True if 'y' in see_nodes_str.lower() else False
        print('the drawing units are {}'.format(units_dic[dxf_doc.header['$INSUNITS']]))

        # ******* Making Nodes/Graph **********
    
        ycounter_int = 0
        node_count = 0

        inc = input("What is maze resolution in feet? (default is 5ft)")
        inc_int = 5 if len(inc) < 1 else int(inc)
        # converting from feet to inches
        node_increment = inc_int * 12
        nodes = []

        # Starting and ending points
        # Eventually replace with user prompts 
        # converting from feet to inches
        xstart_str = input("What is the starting x position in inches? (default is 122feet)")
        ystart_str = input("What is the starting y position in inches? (default is 230 feet)")
        xend_str = input("What is the ending x position in inches? (default is 257 feet)")
        yend_str = input("What is the ending y position in inches? (default is 130 feet)")

        xstart = 122*12 if len(xstart_str) < 1 else int(xstart_str)
        ystart = 230*12 if len(ystart_str) < 1 else int(ystart_str)
        xend = 257*12 if len(xend_str) < 1 else int(xend_str)
        yend = 130*12 if len(yend_str) < 1 else int(yend_str)

        self.start = None
        self.end = None

        # Rounding starting points to nearest node position
        # Should make this into a helper function
        xcorrection = (xstart - xmin) % node_increment
        ycorrection = (ystart - ymin) % node_increment

        xstart -= xcorrection
        ystart -= ycorrection

        xcorrection = (xend - xmin) % node_increment
        ycorrection = (yend - ymin) % node_increment

        xend -= xcorrection
        yend -= ycorrection

        print('Start point: (',xstart,ystart,')')
        print('End point: (',xend,yend,')')

        t1 = time.time()
        # How to make this faster?
        # Looks like the time is coming from the if statements for intersecting lines. Not sure which is slowest
        # looks like horizontal is the slowest, but vert is pretty similar. Horizontal is maybe a bit slower since it
        # has to go to the nodes array. The larger problem is that it is O(n) for the number of lines
        # if we sort the lines and use a binary search then it would be O(log(n)) and a lot faster.
        # will have to think for a bit on how to implement that. 
        print('Start time was: ', (t1 - t0))
        t_total_0 = 0
        t_total_1 = 0
        t_total_2 = 0
        t_total_horiz = 0
        t_total_vert = 0
        t_total_diag = 0
        # print('xcounter: ',xcounter,' xmax ',xmax)
        while ycounter < ymax:
        
            xcounter = xmin
            nodes_row = []
            prev = None
            xcounter_int = 0

            while xcounter < xmax:
                t0 = time.time()
                curr = Maze.Node((xcounter, ycounter))
                node_count += 1
                # print(curr.Position)
                if(self.see_nodes_bool):
                    dxf_msp.add_circle((curr.Position[0], curr.Position[1]), 2, dxfattribs={'layer': 'E-B-FURR'})
                # curr adds the previous node to the left
                t1 = time.time()
                
                if(
                    prev != None and 
                    _intersect_lines(lines_vertical, (curr.Position[0], curr.Position[1]), (prev.Position[0], prev.Position[1])) == False and
                    _intersect_lines(lines_diagonal, (curr.Position[0], curr.Position[1]), (prev.Position[0], prev.Position[1])) == False
                    ):
                    # the previous node to the left adds the current node to the right if there's no walls in the way
                    curr.Neighbors[3] = prev
                    prev.Neighbors[1] = curr
                    if(self.see_nodes_bool):
                        dxf_msp.add_line((curr.Position[0], curr.Position[1]), (prev.Position[0], prev.Position[1]), dxfattribs={'layer': 'E-B-FURR', 'color':3})
                t2 = time.time()
                if(ycounter != ymin):
                    if(
                        _intersect_lines(
                            lines_horizontal, 
                            (curr.Position[0], curr.Position[1]), 
                            (nodes[ycounter_int-1][xcounter_int].Position[0], nodes[ycounter_int-1][xcounter_int].Position[1])) 
                        == False and
                        _intersect_lines(
                            lines_diagonal, 
                            (curr.Position[0], curr.Position[1]), 
                            (nodes[ycounter_int-1][xcounter_int].Position[0], nodes[ycounter_int-1][xcounter_int].Position[1])) == False
                        ):
                        # if there's no walls between the current node and the node below, then add an edge
                        # up is 0, down is 2
                        curr.Neighbors[2] = nodes[ycounter_int-1][xcounter_int]
                        nodes[ycounter_int-1][xcounter_int].Neighbors[0] = curr
                        if(self.see_nodes_bool):
                            dxf_msp.add_line(
                                (curr.Position[0], curr.Position[1]), 
                                (nodes[ycounter_int-1][xcounter_int].Position[0], nodes[ycounter_int-1][xcounter_int].Position[1]), 
                                dxfattribs={'layer': 'E-B-FURR', 'color':3})

                        # ********** time test section *******
                        if(prev != None):
                            t4 = time.time()
                            _intersect_lines(lines_vertical, (curr.Position[0], curr.Position[1]), (prev.Position[0], prev.Position[1]))

                            t5 = time.time()
                            _intersect_lines(
                                lines_horizontal, 
                                (curr.Position[0], curr.Position[1]), 
                                (nodes[ycounter_int-1][xcounter_int].Position[0], nodes[ycounter_int-1][xcounter_int].Position[1])) 

                            t6 = time.time()
                            _intersect_lines(
                                lines_diagonal, 
                                (curr.Position[0], curr.Position[1]), 
                                (nodes[ycounter_int-1][xcounter_int].Position[0], nodes[ycounter_int-1][xcounter_int].Position[1]))
                            t7 = time.time()

                            t_total_vert += (t5 - t4)
                            t_total_horiz += (t6 - t5)
                            t_total_diag += (t7 - t6)
                        
                t3 = time.time()

                if(xcounter == xstart and ycounter == ystart):
                    #found start node
                    print('found start node')
                    self.start = curr
                    # dxf_msp.add_circle((curr.Position[0], curr.Position[1]), 36, dxfattribs={'layer': 'E-B-FURR'})

                elif(xcounter == xend and ycounter == yend):
                    #found end node
                    print('found end node')
                    self.end = curr
                    # dxf_msp.add_circle((curr.Position[0], curr.Position[1]), 36, dxfattribs={'layer': 'E-B-FURR'})

                nodes_row.append(curr)
                prev = curr
                xcounter += node_increment
                xcounter_int +=1

                t_total_0 += (t1 - t0)
                t_total_1 += (t2 - t1)
                t_total_2 += (t3 - t2)

            nodes.append(nodes_row)
            ycounter += node_increment
            ycounter_int +=1

        if(see_nodes_str):
            dxf_doc.saveas(output_file)

        print('Time 0 was: ', t_total_0)
        print('Time 1 was: ', t_total_1)
        print('Time 2 was: ', t_total_2)
        print('Time for horizontal lines was ', t_total_horiz)
        print('Time for vertical lines was ', t_total_vert)
        print('Time for diagonal lines was ', t_total_diag)
        print('Total maze nodes: ',node_count)

    def render(self, path, input_file, output_file):
        if(self.see_nodes_bool):
            dxf_doc = ezdxf.readfile(output_file)
        else:
            dxf_doc = ezdxf.readfile(input_file)
        dxf_msp = dxf_doc.modelspace()

        unfrozen_layers = []
        for layer in dxf_doc.layers:
            if(layer.is_frozen() == False):
                unfrozen_layers.append(layer)

        unfrozen_layers_names = []
        for layer in unfrozen_layers:
            unfrozen_layers_names.append(layer.dxf.name)
        
        # print(unfrozen_layers_names)

        # marking start and end point
        dxf_msp.add_circle(path[0].Position, 36, dxfattribs={'layer': 'E-B-FURR', 'color':5})
        dxf_msp.add_circle(path[-1].Position, 36, dxfattribs={'layer': 'E-B-FURR', 'color':7})

        # adding a line for each pair of points
        for i in range (1, len(path)):
            # Colors: 1: Red, 3: Green, 4: Teal, 5: Blue, 6: Maroon, 7: Black
            dxf_msp.add_line(path[i-1].Position, path[i].Position, dxfattribs={'layer': 'E-B-FURR', 'color':1})

        dxf_doc.saveas(output_file)


def _intersect_lines(lines, pos1, pos2):
    for line in lines:
        if(_intersect(
            (line.Position1[0], line.Position1[1]),
            (line.Position2[0], line.Position2[1]),
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
