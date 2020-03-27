import ezdxf
import time
# from mazes import Maze
from factory import SolverFactory
import argparse

def solve(factory, method, input_file, output_file):
    # Import the dxf
    print("Loading Dxf")
    dxf_doc = ezdxf.readfile(input_file)
    dxf_msp = dxf_doc.modelspace()

    unfrozen_layers = []
    for layer in dxf_doc.layers:
        if(layer.is_frozen() == False):
            unfrozen_layers.append(layer)

    unfrozen_layers_names = []
    for layer in unfrozen_layers:
        print(layer.dxf.name)
        print(layer.is_frozen())
        unfrozen_layers_names.append('layer == "' + layer.dxf.name + '"')

    query_str = ' | '.join(unfrozen_layers_names)
    print(query_str)
    print('LINE[{}]'.format(query_str))

    lines = dxf_msp.query('LINE[{}]'.format(query_str))

        # entity query for all LINE entities in modelspace
    for e in lines:
        print_entity(e)

    

    print("Creating Graph/Maze")
    # maze = Maze(dxf_doc)
    
def print_entity(e):
        print("LINE on layer: %s\n" % e.dxf.layer)
        print("start point: %s\n" % e.dxf.start)
        print("end point: %s\n" % e.dxf.end)

def main():
    sf = SolverFactory()
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--method", nargs='?', const=sf.Default, default=sf.Default,
                        choices=sf.Choices)
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    args = parser.parse_args()

    solve(sf, args.method, args.input_file, args.output_file)

if __name__ == "__main__":
    main()