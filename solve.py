import time
from mazes import Maze
from factory import SolverFactory
import argparse

def solve(factory, method, input_file, output_file):
    
    print("Creating Graph/Maze")
    t0 = time.time()
    maze = Maze(input_file, output_file)
    t1 = time.time()
    total_time = t1 - t0
    print("Time to make maze: ", total_time, "\n")

    # Create and run solver
    [title, solver] = factory.createsolver(method)
    print("Starting Solve:", title)

    t0 = time.time()
    results = solver(maze)
    t1 = time.time()
    total_time = t1 - t0
    print("Time to solve maze: ", total_time, "\n")
    # print(results)

    # Render and save the returned path/solution
    t0 = time.time()
    maze.render(results, input_file, output_file)
    t1 = time.time()
    total_time = t1 - t0
    print("Time to render path: ", total_time, "\n")


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