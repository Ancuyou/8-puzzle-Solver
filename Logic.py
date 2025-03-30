import random
import time
from collections import deque
from heapq import heappop, heappush

GOAL_STATE = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]


def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j


def generate_children(state):
    x, y = find_blank(state)
    children = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = [row[:] for row in state]
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            children.append(new_state)
    return children


def is_goal(state):
    return state == GOAL_STATE


def hst(state):  # hashable state
    return tuple(map(tuple, state))


def uhst(state):  # unhashable state
    return list(map(list, state))


def hill_simp(start_state):
    path = {hst(start_state): None}
    current = start_state
    while True:
        current_h = manhattan_distance(current)
        improved = False
        children = generate_children(current)
        random.shuffle(children)
        for child in children:
            child_h = manhattan_distance(child)
            if child_h < current_h:
                path[hst(child)] = current
                current = child
                improved = True
                break
        if not improved:
            break
        if is_goal(current):
            return re_path(path, current)
    return None


def hill_climbing_steepest(start_state):
    path = {hst(start_state): None}
    current = start_state
    while True:
        current_h = manhattan_distance(current)
        best_neighbor = None
        best_neighbor_h = current_h
        for child in generate_children(current):
            child_h = manhattan_distance(child)
            if child_h < best_neighbor_h:
                best_neighbor = child
                best_neighbor_h = child_h
        if best_neighbor is not None and best_neighbor_h < current_h:
            path[hst(best_neighbor)] = current
            current = best_neighbor
            if is_goal(current):
                return re_path(path, current)
        else:
            break
    return None


def hill_climbing_stochastic(start_state):
    path = {hst(start_state): None}
    current = start_state
    while True:
        current_h = manhattan_distance(current)
        improved_neighbors = []
        weights = []
        for child in generate_children(current):
            child_h = manhattan_distance(child)
            if child_h < current_h:
                improved_neighbors.append(child)
                weights.append(current_h - child_h)
        if improved_neighbors:
            chosen = random.choices(improved_neighbors, weights=weights, k=1)[0]
            path[hst(chosen)] = current
            current = chosen
            if is_goal(current):
                return re_path(path, current)
        else:
            break
    return None


def bfs(start_state):
    queue = deque([start_state])
    visited = set()
    visited.add(hst(start_state))
    path = {hst(start_state): None}
    while queue:
        current = queue.popleft()
        if is_goal(current):
            return re_path(path, current)
        for child in generate_children(current):
            child_hst = hst(child)
            if child_hst not in visited:
                visited.add(child_hst)
                queue.append(child)
                path[child_hst] = current
    return None


def ucs(start_state):
    pq = []
    heappush(pq, (0, start_state))
    visited = {}
    visited[hst(start_state)] = 0
    path = {hst(start_state): None}
    while pq:
        cost, current = heappop(pq)
        if is_goal(current):
            return re_path(path, current)
        for child in generate_children(current):
            child_hst = hst(child)
            new_cost = cost + 1
            if child_hst not in visited or new_cost < visited[child_hst]:
                visited[child_hst] = new_cost
                heappush(pq, (new_cost, child))
                path[child_hst] = current
    return None


def deepening(state, depth, visited, path):  # dept là độ sâu còn lại mà ta có thể xuống, xuống một bậc thì depth giảm một
    if is_goal(state):
        return re_path(path, state)
    if depth == 0:
        return None
    for child in generate_children(state):
        child_hst = hst(child)
        if child_hst not in visited:
            visited.add(child_hst)
            path[child_hst] = state
            result = deepening(child, depth - 1, visited, path)
            if result:
                return result
            path.pop(child_hst)
    return None


def iddfs(start_state, max_depth=50):
    depth = 0
    while depth <= max_depth:
        visited = set()
        visited.add(hst(start_state))
        path = {hst(start_state): None}
        result = deepening(start_state, depth, visited, path)
        if result:
            return result
        depth += 1
    return None


def dfs(start_state, max_depth=100):
    stack = [(start_state, 0)]
    visited = set()
    visited.add(hst(start_state))
    path = {hst(start_state): None}
    while stack:
        current, depth = stack.pop()
        if is_goal(current):
            return re_path(path, current)
        if depth < max_depth:
            for child in generate_children(current):
                child_hst = hst(child)
                if child_hst not in visited:
                    visited.add(child_hst)
                    stack.append((child, depth + 1))
                    path[child_hst] = current
    return None


def manhattan_distance(state):  # Day la tong chi phi cua tat ca cac 1,2,3,... de ve vi tri chinh xac cua no o state hien tai
    distance = 0
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            if value != 0:
                target_x, target_y = divmod(value - 1, 3)
                distance += abs(target_x - i) + abs(target_y - j)
    return distance


def gbfs(start_state):
    pq = []
    heappush(pq, (manhattan_distance(start_state), start_state))
    visited = set()
    visited.add(hst(start_state))
    path = {hst(start_state): None}
    while pq:
        _, current = heappop(pq)
        if is_goal(current):
            return re_path(path, current)
        for child in generate_children(current):
            child_hst = hst(child)
            if child_hst not in visited:
                visited.add(child_hst)
                heappush(pq, (manhattan_distance(child), child))
                path[child_hst] = current
    return None


def A_star(start_state):
    pq = []
    heappush(pq, (manhattan_distance(start_state), start_state))
    visited = set()
    visited.add(hst(start_state))
    path = {hst(start_state): None}
    while pq:
        _, current = heappop(pq)
        if is_goal(current):
            return re_path(path, current)
        for child in generate_children(current):
            child_hst = hst(child)
            if child_hst not in visited:
                visited.add(child_hst)
                heappush(pq, (manhattan_distance(child) + 1, child))
                path[child_hst] = current
    return None


def ida_search(path, g, threshold):
    current = path[-1]
    f = g + manhattan_distance(current)
    if f > threshold:
        return f
    if is_goal(current):
        return list(path)
    minimum = float("inf")
    for child in generate_children(current):
        if any(hst(child) == hst(p) for p in path):
            continue
        path.append(child)
        temp = ida_search(path, g + 1, threshold)
        if isinstance(temp, list):
            return temp
        if temp < minimum:
            minimum = temp
        path.pop()
    return minimum


def ida_star(start_state):
    threshold = manhattan_distance(start_state)
    path = [start_state]
    while True:
        temp = ida_search(path, 0, threshold)
        if isinstance(temp, list):
            return temp
        if temp == float("inf"):
            return None
        threshold = temp


def solution_time(start_state, algo_type):
    start_time = time.time()
    if algo_type == "dfs":
        solution = dfs(start_state)
        end_time = time.time()
    elif algo_type == "bfs":
        solution = bfs(start_state)
        end_time = time.time()
    elif algo_type == "ucs":
        solution = ucs(start_state)
        end_time = time.time()
    elif algo_type == "iddfs":
        solution = iddfs(start_state)
        end_time = time.time()
    elif algo_type == "gbfs":
        solution = gbfs(start_state)
        end_time = time.time()
    elif algo_type == "A_star":
        solution = A_star(start_state)
        end_time = time.time()
    elif algo_type == "ida_star":
        solution = ida_star(start_state)
        end_time = time.time()
    elif algo_type == "hill_simp":
        solution = hill_simp(start_state)
        end_time = time.time()
    elif algo_type == "hill_steepest":
        solution = hill_climbing_steepest(start_state)
        end_time = time.time()
    elif algo_type == "hill_stochastic":
        solution = hill_climbing_stochastic(start_state)
        end_time = time.time()
    execution_time = end_time - start_time
    return solution, execution_time


def re_path(path, state):
    steps = []
    while state is not None:
        steps.append(state)
        state = path[hst(state)]
    return steps[::-1]


if __name__ == "__main__":
    start_state = [[2, 6, 5], [8, 7, 0], [4, 3, 1]]
    solution = hill_simp(start_state)
    if solution:
        print("Đã tìm thấy lời giải!")
        for step in solution:
            for row in step:
                print(row)
            print()
    else:
        print("Không tìm thấy lời giải!")
