import math
import random
import time
from collections import deque
from copy import deepcopy
from heapq import heappop, heappush, nsmallest

import numpy as np

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


def manhattan_distance(state):  # Day la tong chi phi cua tat ca cac 1,2,3,... de ve vi tri chinh xac cua no o state hien tai
    distance = 0
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            if value != 0:
                target_x, target_y = divmod(value - 1, 3)
                distance += abs(target_x - i) + abs(target_y - j)
    return distance


def misplaced_tiles(state):
    mis_state = np.array(GOAL_STATE) - np.array(state)
    count = 0
    for i in range(3):
        for j in range(3):
            value = mis_state[i][j]
            if value != 0:
                count += 1
    return count


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


def simulated_annealing(start_state, initial_temp=10000, cooling_rate=0.995, min_temp=1, max_iterations=12000):
    current = start_state
    path = {hst(current): None}
    temperature = initial_temp
    iteration = 0
    while temperature > min_temp and iteration < max_iterations:
        if is_goal(current):
            return re_path(path, current)
        neighbors = generate_children(current)
        if not neighbors:
            break
        neighbor = random.choice(neighbors)
        delta = manhattan_distance(current) + misplaced_tiles(current) - manhattan_distance(neighbor) - misplaced_tiles(neighbor)
        if delta > 0 or random.random() < math.exp(-delta / temperature):
            neighbor_hst = hst(neighbor)
            if neighbor_hst not in path:
                path[neighbor_hst] = current
            current = neighbor
        temperature *= cooling_rate
        iteration += 1
    return None


def beam_search(start_state, k=2):
    beam = [(manhattan_distance(start_state), start_state)]
    path = {hst(start_state): None}
    visited = set()
    visited.add(hst(start_state))
    while beam:
        new_beam = []
        for _ in range(len(beam)):
            _, current = heappop(beam)
            if is_goal(current):
                return re_path(path, current)
            for child in generate_children(current):
                child_hst = hst(child)
                if child_hst not in visited:
                    visited.add(child_hst)
                    path[child_hst] = current
                    heappush(new_beam, (manhattan_distance(child), child))
        beam = nsmallest(k, new_beam)
        if not beam:
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


def genetic(start_state, population_size=100, generations=10000, mutation_rate=0.1, max_steps=50):
    def create_individual():
        individual = [start_state]
        current = start_state
        for _ in range(max_steps):
            children = generate_children(current)
            if not children:
                break
            next_state = random.choice(children)
            individual.append(next_state)
            current = next_state
        return individual

    def fitness(individual):
        last_state = individual[-1]
        return manhattan_distance(last_state) + misplaced_tiles(last_state)

    def crossover(parent1, parent2):
        cut = random.randint(1, min(len(parent1), len(parent2)) - 1)
        child = parent1[:cut]
        for state in parent2:
            if state not in child:
                child.append(state)
        return child

    def mutate(individual):
        if random.random() < mutation_rate:
            index = random.randint(0, len(individual) - 1)
            moves = generate_children(individual[index])
            if moves:
                individual[index] = random.choice(moves)
        return individual

    population = [create_individual() for _ in range(population_size)]

    for generation in range(generations):
        population = sorted(population, key=fitness, reverse=True)
        for individual in population:
            if is_goal(individual[-1]):
                return individual
        next_generation = population[: population_size // 2]
        while len(next_generation) < population_size:
            parent1, parent2 = random.sample(next_generation, 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            next_generation.append(child)
        population = next_generation
    return None


def and_or_search(start_state):
    path = {hst(start_state): None}
    if is_goal(start_state):
        return re_path(path, start_state)
    or_nodes = deque([start_state])
    visited = set()
    visited.add(hst(start_state))
    while or_nodes:
        current = or_nodes.popleft()
        if is_goal(current):
            return re_path(path, current)
        children = generate_children(current)
        if not children:
            continue
        for child in children:
            child_hst = hst(child)
            if child_hst not in visited:
                visited.add(child_hst)
                path[child_hst] = current
                or_nodes.append(child)
                if is_goal(child):
                    return re_path(path, child)
    return None


def generate_belief_states(start_state, num_states=3):
    belief_states = [start_state]
    while len(belief_states) < num_states:
        random_child = random.choice(generate_children(start_state))
        if hst(random_child) not in map(hst, belief_states):
            belief_states.append(random_child)
    return belief_states


def search_with_partial_observation(belief_states, goal_states, max_steps=50):
    def possible_moves(state):
        moves = []
        x, y = [(ix, iy) for ix, row in enumerate(state) for iy, i in enumerate(row) if i == 0][0]
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                new_state = [row[:] for row in state]
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                moves.append(new_state)
        return moves

    steps = [deepcopy(belief_states)]
    t0 = time.time()
    for step in range(max_steps):
        next_belief = []
        for state in steps[-1]:
            next_belief.extend(possible_moves(state))
        next_belief_unique = []
        for s in next_belief:
            if not any(s == b for b in next_belief_unique):
                next_belief_unique.append(s)
        steps.append(next_belief_unique)
        for s in next_belief_unique:
            if any(s == g for g in goal_states):
                return steps, time.time() - t0
        if not next_belief_unique:
            break
    return steps, time.time() - t0


def search_with_no_observation(belief_states, goal_states, max_steps=20):
    def possible_moves(state):
        moves = []
        x, y = [(ix, iy) for ix, row in enumerate(state) for iy, i in enumerate(row) if i == 0][0]
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                new_state = [row[:] for row in state]
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                moves.append(new_state)
        return moves

    def state_to_tuple(state):
        return tuple(tuple(row) for row in state)

    steps = [deepcopy(belief_states)]
    t0 = time.time()
    for step in range(max_steps):
        next_belief = []
        seen = set()
        for state in steps[-1]:
            for s in possible_moves(state):
                t = state_to_tuple(s)
                if t not in seen:
                    seen.add(t)
                    next_belief.append(s)
        steps.append(next_belief)
        if next_belief and all(any(s == g for g in goal_states) for s in next_belief):
            return steps, time.time() - t0
        if not next_belief:
            break
    return steps, time.time() - t0


csp_cons = {"variables": [(i, j) for i in range(3) for j in range(3)], "domains": {(i, j): list(range(0, 9)) for i in range(3) for j in range(3)}, "constraints": lambda var1, val1, var2, val2: val1 != val2}  # Tọa độ (hàng, cột) cho bảng 3x3  # Giá trị từ 1 đến 8 cho mỗi ô  # Không có số nào lặp lại
csp_simple = {"variables": [(i, j) for i in range(3) for j in range(3)], "domains": {(i, j): list(range(0, 9)) for i in range(3) for j in range(3)}, "constraints": None}


def reconstruct_state(assignment):
    """
    Tái tạo mảng 3x3 từ dictionary assignment.
    Nếu (i,j) không có trong assignment, ta xem như ô đó là 0.
    """
    state = [[0 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            state[i][j] = assignment.get((i, j), 0)
    return state


def compare_state(assignment, start_state):
    """
    So sánh mảng 3x3 vừa tái tạo với start_state.
    Trả về True nếu chúng bằng nhau, ngược lại trả về False.
    """
    return reconstruct_state(assignment) == start_state


def backtracking(csp):
    return backtrack({}, csp)


def backtrack(assignment, csp):
    if len(assignment) == len(csp["variables"]):
        if compare_state(assignment, GOAL_STATE):
            return assignment
        else:
            return None
    unassigned_vars = [var for var in csp["variables"] if var not in assignment]
    random.shuffle(unassigned_vars)  # Shuffle the unassigned variables to introduce randomness
    var = unassigned_vars[0]
    values = csp["domains"][var]
    random.shuffle(values)  # Shuffle the values to introduce randomness
    for value in values:
        if csp["constraints"] is None or is_consistent(assignment, var, value, csp):
            assignment[var] = value
            result = backtrack(assignment, csp)
            if result:
                return result
            del assignment[var]
    return None


def is_consistent(assignment, var, value, csp):
    for other_var in assignment:
        if not csp["constraints"](var, value, other_var, assignment[other_var]):
            return False
    return True


def select_unassigned_variable_mrv(assignment, csp):
    """
    Chọn ô chưa gán có số giá trị khả dụng thỏa điều kiện nhất quán (nếu có ràng buộc)
    nhỏ nhất, tức là ô đó có "Minimum Remaining Values".
    """
    unassigned_vars = [var for var in csp["variables"] if var not in assignment]
    min_var = None
    min_remaining = float("inf")
    for var in unassigned_vars:
        count = 0
        for value in csp["domains"][var]:
            # Nếu không có ràng buộc, hoặc giá trị này thỏa mãn khi gán vào biến
            if csp["constraints"] is None or is_consistent(assignment, var, value, csp):
                count += 1
        if count < min_remaining:
            min_remaining = count
            min_var = var
    return min_var


def backtracking_lcv(assignment, csp):
    # Nếu tất cả các biến đã được gán, kiểm tra kết quả
    if len(assignment) == len(csp["variables"]):
        if compare_state(assignment, GOAL_STATE):  # Bạn có thể thay GOAL_STATE bằng start_state nếu cần
            return assignment
        else:
            return None

    # Chọn biến chưa gán theo MRV (có ít khả năng lựa chọn nhất)
    var = select_unassigned_variable_mrv(assignment, csp)
    # Lấy dãy các giá trị từ domain của biến và trộn ngẫu nhiên để tăng tính ngẫu nhiên
    values = csp["domains"][var][:]
    random.shuffle(values)

    for value in values:
        if csp["constraints"] is None or is_consistent(assignment, var, value, csp):
            assignment[var] = value
            result = backtracking_lcv(assignment, csp)
            if result is not None:
                return result
            del assignment[var]
    return None


def solution_time(start_state, algo_type):
    start_time = time.time()
    end_time = 0
    solution = None
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
    elif algo_type == "beam":
        solution = beam_search(start_state)
        end_time = time.time()
    elif algo_type == "simulated_annealing":
        solution = simulated_annealing(start_state)
        end_time = time.time()
    elif algo_type == "genetic":
        solution = genetic(start_state)
        end_time = time.time()
    elif algo_type == "and_or":
        solution = and_or_search(start_state)
        end_time = time.time()
    elif algo_type == "backtracking":
        solution = backtracking(csp_simple)
        end_time = time.time()
    elif algo_type == "backtracking_constraint_propagation":
        solution = backtracking(csp_cons)
        end_time = time.time()
    elif algo_type == "backtracking_lcv":
        solution = backtracking_lcv({}, csp_cons)
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
    # start_state = [[2, 6, 5], [8, 7, 0], [4, 3, 1]]
    start_state = [[1, 2, 3], [4, 5, 6], [7, 0, 8]]
    solution = backtracking_lcv({}, csp_cons)
    if solution:
        #     print("Đã tìm thấy lời giải!")
        #     for step in solution:
        #         for row in step:
        #             print(row)
        #         print()
        # else:
        #     print("Không tìm thấy lời giải!")
        print(solution)
    else:
        print("Khong tim thay loi giai")
