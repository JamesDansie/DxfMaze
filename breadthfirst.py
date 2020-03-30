from collections import deque

def solve(maze):
    start = maze.start
    end = maze.end

    visited_nodes = set()
    queue = deque([start])
    count = 0
    parent = {}

    while queue:
        count += 1
        curr = queue.pop()
        visited_nodes.add(curr)

        if curr == end:
            print('Found the end')
            print('Checked {} nodes'.format(count))
            return backtrace(parent, start, end)
            break

        for neighbor in curr.Neighbors:
            if neighbor != None:
                if(neighbor not in visited_nodes):
                    parent[neighbor] = curr
                    queue.appendleft(neighbor)
                    visited_nodes.add(neighbor)

    print('No solution found')
    print('Checked {} nodes'.format(count))
    return 'answer?'

# from; https://stackoverflow.com/questions/8922060/how-to-trace-the-path-in-a-breadth-first-search
def backtrace(parent, start, end):
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    return path