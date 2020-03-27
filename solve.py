import ezdxf
import time
# from mazes import mazes
from factory import SolverFactory
import argparse

def solve(factory, method, input_file, output_file):
    # Import the dxf
    print("Loading Dxf")
    doc = ezdxf.readfile(input_file)

    # From ezdxf tutorial
    # iterate over all entities in modelspace
    msp = doc.modelspace()
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