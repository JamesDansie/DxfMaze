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
        lines = dxf_msp.query('LINE[{}]'.format(query_str))
        polylines = dxf_msp.query('LWPOLYLINE[{}]'.format(query_str))
        
        # *********** end of dxf import ***************

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
        # Sorting verical lines by their x position and 
        # horizontal lines by their y position
        lines_vertical.sort(key=lambda x1: x1.Position1[0], reverse=False)
        lines_horizontal.sort(key=lambda x1: x1.Position1[1], reverse=False)


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

        print('Start time was: ', (t1 - t0))
        t_total_0 = 0
        t_total_1 = 0
        t_total_2 = 0

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
                    _intersect_lines_binary_vert(lines_vertical, (prev.Position[0], prev.Position[1]), (curr.Position[0], curr.Position[1])) == False and
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
                        _intersect_lines_binary_horiz(
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

        print('Making nodes took ', t_total_0)
        print('Making horizontal edges took ', t_total_1)
        print('Making vertical edges took ', t_total_2)
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

            # marking start and end point
            dxf_msp.add_circle(path[0].Position, 36, dxfattribs={'layer': 'E-B-FURR', 'color':5})
            dxf_msp.add_circle(path[-1].Position, 36, dxfattribs={'layer': 'E-B-FURR', 'color':7})

            # adding a line for each pair of points
            for i in range (1, len(path)):
                # Colors: 1: Red, 3: Green, 4: Teal, 5: Blue, 6: Maroon, 7: Black
                dxf_msp.add_line(path[i-1].Position, path[i].Position, dxfattribs={'layer': 'E-B-FURR', 'color':1})

            dxf_doc.saveas(output_file)

# given a pos1 and pos2 that is changing vertically (delta in y)
# this will check for intersection with horizontal lines (delta in x)
def _intersect_lines_binary_horiz(lines, pos1, pos2):
    # Making sure that pos1 is smaller than pos2
    tmp1 = pos1
    tmp2 = pos2
    if(pos1[1] > pos2[1]):
        pos1 = tmp2
        pos2 = tmp1

    # Gets us in the ball park
    starting_index = binary_horiz(lines, pos1[1], pos2[1], .2)

    if(starting_index == -1):
        return False
    
    # Gets all the lines in range between pos1 and pos2
    new_lines = []
    new_lines.append(lines[starting_index])
    lower_bounds = upper_bounds = starting_index

    while(lines[lower_bounds].Position1[1] > pos1[1] and lower_bounds >= 0):
        new_lines.append(lines[lower_bounds])
        lower_bounds -= 1

    while(lines[upper_bounds].Position1[1] < pos2[1] and upper_bounds < len(lines)-1 ):
        new_lines.append(lines[upper_bounds])
        upper_bounds += 1

    # Check for intersection
    ans = _intersect_lines(new_lines, pos1, pos2)
    return ans

# give a pos1 and pos2 that is changing horizontally (delta in x)
# this will check for intersection with vertical lines (delta in y)
def _intersect_lines_binary_vert(lines, pos1, pos2):
    tmp1 = pos1
    tmp2 = pos2

    if(pos1[0] > pos2[0]):
        pos1 = tmp2
        pos2 = tmp1

    # Gets us in the ball park
    starting_index = binary_vert(lines, pos1[0], pos2[0], .2)

    if(starting_index == -1):
        return False
    
    # Gets all the lines in range between pos1 and pos2
    new_lines = []
    new_lines.append(lines[starting_index])
    lower_bounds = upper_bounds = starting_index

    while(lines[lower_bounds].Position1[0] > pos1[0] and lower_bounds >= 0):
        new_lines.append(lines[lower_bounds])
        lower_bounds -= 1

    while(lines[upper_bounds].Position1[0] < pos2[0] and upper_bounds < len(lines)-1 ):
        new_lines.append(lines[upper_bounds])
        upper_bounds += 1

    # Check for intersection
    ans = _intersect_lines(new_lines, pos1, pos2)
    return ans
    
# Finds the indext of a line in the range of pos1 and pos +/- a delta
# Searches with a binary search
def binary_vert(lines, pos1x, pos2x, delta):
    lower = 0
    upper = len(lines)-1

    while(lower <= upper):
        mid = int((lower + upper)/2)
        # print('mid point is ',mid)

        if(lines[mid].Position1[0] > (pos1x - delta) and lines[mid].Position2[0] < (pos2x + delta)):
            return mid
        elif(pos1x > lines[mid].Position1[0]):
            lower = mid + 1
        else:
            upper = mid - 1
    return -1

# Finds the indext of a line in the range of pos1 and pos +/- a delta
# Searches with a binary search
def binary_horiz(lines, pos1x, pos2x, delta):
    lower = 0
    upper = len(lines)-1

    while(lower <= upper):
        mid = int((lower + upper)/2)
        # print('mid point is ',mid)

        if(lines[mid].Position1[1] > (pos1x - delta) and lines[mid].Position2[1] < (pos2x + delta)):
            return mid
        elif(pos1x > lines[mid].Position1[1]):
            lower = mid + 1
        else:
            upper = mid - 1
    return -1

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
