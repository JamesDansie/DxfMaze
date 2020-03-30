from collections import deque

def solve(maze):
    start = maze.start
    end = maze.end

    visited_nodes = set()
    queue = deque([start])
    count = 0

    while queue:
        count += 1
        curr = queue.pop()
        visited_nodes.add(curr)

        if curr == end:
            print('Found the end')
            break

        for neighbor in curr.Neighbors:
            if neighbor != None:
                if(neighbor not in visited_nodes):
                    queue.appendleft(neighbor)
                    visited_nodes.add(neighbor)

    print('No solution found')
    return 'answer?'