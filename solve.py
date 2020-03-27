import time
from mazes import Maze
from factory import SolverFactory
import argparse

def solve(factory, method, input_file, output_file):
    
    print("Creating Graph/Maze")
    t0 = time.time()
    maze = Maze(input_file)
    t1 = time.time()
    total_time = t1 - t0
    print("Time to make maze: ", total_time, "\n")
    

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