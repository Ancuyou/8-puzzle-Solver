import csv
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
    explored = 0
    while True:
        explored += 1
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
            return re_path(path, current), explored
    return None, explored


def hill_climbing_steepest(start_state):
    path = {hst(start_state): None}
    current = start_state
    explorer = 0
    while True:
        explorer += 1
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
                return re_path(path, current), explorer
        else:
            break
    return None, explorer


def hill_climbing_stochastic(start_state):
    path = {hst(start_state): None}
    current = start_state
    explorer = 0
    while True:
        explorer += 1
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
                return re_path(path, current), explorer
        else:
            break
    return None, explorer


# def simulated_annealing(start_state, initial_temp=10000, cooling_rate=0.995, min_temp=1, max_iterations=12000):
#     current = start_state
#     path = {hst(current): None}
#     temperature = initial_temp
#     iteration = 0
#     while temperature > min_temp and iteration < max_iterations:
#         if is_goal(current):
#             return re_path(path, current)
#         neighbors = generate_children(current)
#         if not neighbors:
#             break
#         neighbor = random.choice(neighbors)
#         delta = manhattan_distance(current) + misplaced_tiles(current) - manhattan_distance(neighbor) - misplaced_tiles(neighbor)
#         if delta > 0 or random.random() < math.exp(-delta / temperature):
#             neighbor_hst = hst(neighbor)
#             if neighbor_hst not in path:
#                 path[neighbor_hst] = current
#             current = neighbor
#         temperature *= cooling_rate
#         iteration += 1
#     return None


def simulated_annealing(start_state, initial_temp=20000, cooling_rate=0.98, min_temp=0.1, max_iterations=20000):

    current = start_state
    path = {hst(current): None}
    temperature = initial_temp
    iteration = 0
    explorer = 0

    while temperature > min_temp and iteration < max_iterations:
        explorer += 1
        if is_goal(current):
            return re_path(path, current), explorer
        neighbors = generate_children(current)
        if not neighbors:
            break
        neighbor = random.choice(neighbors)
        delta = (manhattan_distance(neighbor) + misplaced_tiles(neighbor)) - (manhattan_distance(current) + misplaced_tiles(current))
        if delta <= 0 or random.random() < math.exp(-delta / temperature):
            neighbor_hst = hst(neighbor)
            if neighbor_hst not in path:
                path[neighbor_hst] = current
            current = neighbor
        temperature *= cooling_rate
        iteration += 1

    return None, explorer


# def beam_search(start_state, k=2):
#     beam = [(manhattan_distance(start_state), start_state)]
#     path = {hst(start_state): None}
#     visited = set()
#     visited.add(hst(start_state))
#     while beam:
#         new_beam = []
#         for _ in range(len(beam)):
#             _, current = heappop(beam)
#             if is_goal(current):
#                 return re_path(path, current)
#             for child in generate_children(current):
#                 child_hst = hst(child)
#                 if child_hst not in visited:
#                     visited.add(child_hst)
#                     path[child_hst] = current
#                     heappush(new_beam, (manhattan_distance(child), child))
#         beam = nsmallest(k, new_beam)
#         if not beam:
#             break
#     return None


# def beam_search(start_state, k=2):
#     beam = [(manhattan_distance(start_state), start_state)]
#     path = {hst(start_state): None}
#     limit = 50
#     count = 0
#     while beam and limit > 0:
#         limit -= 1
#         count += 1
#         new_beam = []
#         for _ in range(len(beam)):
#             _, current = heappop(beam)
#             if is_goal(current):
#                 return re_path(path, current)
#             for child in generate_children(current):
#                 child_hst = hst(child)
#                 if child_hst not in path:
#                     path[child_hst] = current
#                     heappush(new_beam, (manhattan_distance(child), child))
#         beam = nsmallest(k, new_beam)
#         print(f"Xét lần {count}: {beam}")
#         if not beam:
#             break
#     return None


def beam_search(start_state, k=2):
    beam = [(manhattan_distance(start_state), start_state, [start_state])]  # (heuristic, state, path_to_state)
    visited = set()  # To track states in the current beam to avoid duplicates within one iteration
    limit = 50
    count = 0
    explored = 0
    while beam and limit > 0:
        explored += 1
        limit -= 1
        count += 1
        new_beam = []
        visited.clear()  # Clear visited set for this iteration
        for _ in range(len(beam)):
            _, current, current_path = heappop(beam)
            if is_goal(current):
                return current_path, explored
            for child in generate_children(current):
                child_hst = hst(child)
                # Allow revisiting states, but avoid duplicates in the same iteration
                if child_hst not in visited:
                    visited.add(child_hst)
                    new_path = current_path + [child]
                    heappush(new_beam, (manhattan_distance(child), child, new_path))
        beam = nsmallest(k, new_beam, key=lambda x: x[0])  # Select top k based on heuristic
        print(f"Xét lần {count}: {[(h, s) for h, s, _ in beam]}")
        if not beam:
            break
    return None, explored


def bfs(start_state):
    queue = deque([start_state])
    visited = set()
    visited.add(hst(start_state))
    path = {hst(start_state): None}
    explored = 0
    while queue:
        current = queue.popleft()
        explored += 1
        if is_goal(current):
            return re_path(path, current), explored
        for child in generate_children(current):
            child_hst = hst(child)
            if child_hst not in visited:
                visited.add(child_hst)
                queue.append(child)
                path[child_hst] = current
    return None, explored


def ucs(start_state):
    pq = []
    heappush(pq, (0, start_state))
    visited = {}
    visited[hst(start_state)] = 0
    path = {hst(start_state): None}
    explorer = 0
    while pq:
        explorer += 1
        cost, current = heappop(pq)
        if is_goal(current):
            return re_path(path, current), explorer
        for child in generate_children(current):
            child_hst = hst(child)
            new_cost = cost + 1
            if child_hst not in visited or new_cost < visited[child_hst]:
                visited[child_hst] = new_cost
                heappush(pq, (new_cost, child))
                path[child_hst] = current
    return None, explorer


def deepening(state, depth, visited, path, explorer):
    if is_goal(state):
        return re_path(path, state)
    if depth == 0:
        return None
    explorer[0] += 1  # Cập nhật explorer qua tham chiếu danh sách
    for child in generate_children(state):
        child_hst = hst(child)
        if child_hst not in visited:
            visited.add(child_hst)
            path[child_hst] = state
            result = deepening(child, depth - 1, visited, path, explorer)
            if result:
                return result
            path.pop(child_hst)
    return None


def iddfs(start_state, max_depth=50):
    depth = 0
    explorer = [0]  # Sử dụng danh sách để theo dõi explorer
    while depth <= max_depth:
        visited = set()
        visited.add(hst(start_state))
        path = {hst(start_state): None}
        result = deepening(start_state, depth, visited, path, explorer)
        if result:
            return result, explorer[0]  # Trả về giá trị explorer cuối cùng
        depth += 1
    return None, explorer[0]


def dfs(start_state, max_depth=100):
    stack = [(start_state, 0)]
    visited = set()
    visited.add(hst(start_state))
    path = {hst(start_state): None}
    explorer = 0
    while stack:
        current, depth = stack.pop()
        explorer += 1
        if is_goal(current):
            return re_path(path, current), explorer
        if depth < max_depth:
            for child in generate_children(current):
                child_hst = hst(child)
                if child_hst not in visited:
                    visited.add(child_hst)
                    stack.append((child, depth + 1))
                    path[child_hst] = current
    return None, explorer


def gbfs(start_state):
    pq = []
    heappush(pq, (manhattan_distance(start_state), start_state))
    visited = set()
    visited.add(hst(start_state))
    path = {hst(start_state): None}
    explorer = 0
    while pq:
        _, current = heappop(pq)
        explorer += 1
        if is_goal(current):
            return re_path(path, current), explorer
        for child in generate_children(current):
            child_hst = hst(child)
            if child_hst not in visited:
                visited.add(child_hst)
                heappush(pq, (manhattan_distance(child), child))
                path[child_hst] = current
    return None, explorer


def A_star(start_state):
    pq = []
    heappush(pq, (manhattan_distance(start_state), start_state))
    visited = set()
    visited.add(hst(start_state))
    path = {hst(start_state): None}
    explorer = 0
    while pq:
        _, current = heappop(pq)
        explorer += 1
        if is_goal(current):
            return re_path(path, current), explorer
        for child in generate_children(current):
            child_hst = hst(child)
            if child_hst not in visited:
                visited.add(child_hst)
                heappush(pq, (manhattan_distance(child) + 1, child))
                path[child_hst] = current
    return None, explorer


def ida_search(path, g, threshold, explorer):
    current = path[-1]
    explorer[0] += 1
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
        temp = ida_search(path, g + 1, threshold, explorer)
        if isinstance(temp, list):
            return temp
        if temp < minimum:
            minimum = temp
        path.pop()
    return minimum


def ida_star(start_state):
    threshold = manhattan_distance(start_state)
    path = [start_state]
    explorer = [0]
    while True:
        temp = ida_search(path, 0, threshold, explorer)
        if isinstance(temp, list):
            return temp, explorer[0]
        if temp == float("inf"):
            return None, explorer[0]
        threshold = temp


def genetic(start_state, population_size=100, generations=10000, mutation_rate=0.1, max_steps=50):
    # Định nghĩa các hướng di chuyển
    moves = ["U", "D", "L", "R"]
    explorer = [0]

    def create_individual():
        # Tạo chuỗi ngẫu nhiên các nước đi
        return [random.choice(moves) for _ in range(max_steps)]

    def apply_moves(state, move_sequence):
        # Áp dụng chuỗi nước đi vào trạng thái ban đầu
        current = state
        path = [current]
        for move in move_sequence:
            explorer[0] += 1
            children = generate_children(current)
            for child in children:
                if get_move(current, child) == move:
                    current = child
                    path.append(current)
                    break
            else:
                break  # Dừng nếu nước đi không hợp lệ
        return path

    def get_move(state, next_state):
        # Xác định nước đi từ state sang next_state
        blank_pos = find_blank(state)
        next_blank_pos = find_blank(next_state)
        dx = next_blank_pos[0] - blank_pos[0]
        dy = next_blank_pos[1] - blank_pos[1]
        if dx == 1:
            return "D"
        elif dx == -1:
            return "U"
        elif dy == 1:
            return "R"
        elif dy == -1:
            return "L"
        return None

    def find_blank(state):
        # Tìm vị trí ô trống (0)
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    return (i, j)

    def fitness(individual):
        # Tính fitness dựa trên đường đi
        path = apply_moves(start_state, individual)
        last_state = path[-1]
        explorer[0] += 1
        if is_goal(last_state):
            return -len(path)  # Ưu tiên đường đi ngắn
        return manhattan_distance(last_state) + misplaced_tiles(last_state)

    def crossover(parent1, parent2):
        # Cắt và nối hai chuỗi nước đi
        cut = random.randint(1, min(len(parent1), len(parent2)) - 1)
        child = parent1[:cut] + parent2[cut:]
        return child

    def mutate(individual):
        # Thay đổi ngẫu nhiên một số nước đi
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual[i] = random.choice(moves)
        return individual

    # Khởi tạo quần thể
    population = [create_individual() for _ in range(population_size)]

    for generation in range(generations):
        # Sắp xếp theo fitness nhỏ nhất
        population = sorted(population, key=fitness)
        for individual in population:
            path = apply_moves(start_state, individual)
            if is_goal(path[-1]):
                return path, explorer[0]  # Trả về đường đi nếu tìm thấy
        # Chọn một nửa tốt nhất
        next_generation = population[: population_size // 2]
        # Tạo cá thể mới
        while len(next_generation) < population_size:
            parent1, parent2 = random.sample(next_generation, 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            next_generation.append(child)
        population = next_generation
    return None, explorer[0]  # Không tìm thấy đường đi


def and_or_search(start_state):
    path = {hst(start_state): None}
    explorer = 0
    if is_goal(start_state):
        return re_path(path, start_state), explorer
    or_nodes = deque([start_state])
    visited = set()
    visited.add(hst(start_state))
    while or_nodes:
        current = or_nodes.popleft()
        explorer += 1
        if is_goal(current):
            return re_path(path, current), explorer
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
                    return re_path(path, child), explorer
    return None, explorer


def state_to_tuple(state):
    return tuple(tuple(row) for row in state)


def tuple_to_state(t):
    return [list(row) for row in t]


# Generate possible moves for 8-puzzle
def possible_moves(state):
    x, y = next((ix, iy) for ix, row in enumerate(state) for iy, v in enumerate(row) if v == 0)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(state) and 0 <= ny < len(state[0]):
            new = [r[:] for r in state]
            new[x][y], new[nx][ny] = new[nx][ny], new[x][y]
            yield new


# Search with No Observation: stop when ANY frontier contains a goal state
def search_with_no_observation(start_states, goal_states, max_steps=50):
    goal_set = {state_to_tuple(g) for g in goal_states}
    frontiers = [set(state_to_tuple(s) for s in start_states)]
    t0 = time.perf_counter()
    explorer = 0

    for _ in range(max_steps):
        curr = frontiers[-1]
        nxt = set()
        for s_tup in curr:
            explorer += 1
            for m in possible_moves(tuple_to_state(s_tup)):
                nxt.add(state_to_tuple(m))
        frontiers.append(nxt)
        # stop when ANY state in nxt is goal
        if nxt & goal_set:
            break
        if not nxt:
            break
    steps = [[tuple_to_state(s) for s in f] for f in frontiers]
    elapsed_ms = (time.perf_counter() - t0) * 1000
    solved_flag = 1 if steps else 0
    # Mở file ở chế độ append và ghi dòng mới
    with open("results.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Search_with_no_observation", f"{elapsed_ms:.3f}", len(steps) if steps else 0, explorer, solved_flag])
    return steps, elapsed_ms


# Search with Partial Observation: filter each frontier by observation at (0,0)==1, stop when ANY frontier contains goal
def search_with_partial_observation(start_states, goal_states, max_steps=50):
    goal_set = {state_to_tuple(g) for g in goal_states}
    frontiers = [set(state_to_tuple(s) for s in start_states)]
    t0 = time.perf_counter()
    explorer = 0

    for _ in range(max_steps):
        curr = frontiers[-1]
        nxt = set()
        for s_tup in curr:
            explorer += 1
            for m in possible_moves(tuple_to_state(s_tup)):
                tup = state_to_tuple(m)
                # partial observation: only keep if top-left cell == 1
                if m[0][0] == 1:
                    nxt.add(tup)
        frontiers.append(nxt)
        # stop when ANY state in nxt is goal
        if nxt & goal_set:
            break
        if not nxt:
            break

    steps = [[tuple_to_state(s) for s in f] for f in frontiers]
    elapsed_ms = (time.perf_counter() - t0) * 1000
    solved_flag = 1 if steps else 0
    # Mở file ở chế độ append và ghi dòng mới
    with open("results.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Search_with_partial_observation", f"{elapsed_ms:.3f}", len(steps) if steps else 0, explorer, solved_flag])
    return steps, elapsed_ms


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
    explorer = [0]
    result = backtrack({}, csp, explorer)
    return result, explorer[0]


def backtrack(assignment, csp, explorer):
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
        explorer[0] += 1
        if csp["constraints"] is None or is_consistent(assignment, var, value, csp):
            assignment[var] = value
            result = backtrack(assignment, csp, explorer)
            if result:
                return result
            del assignment[var]
    return None


def is_consistent(assignment, var, value, csp):
    for other_var in assignment:
        if not csp["constraints"](var, value, other_var, assignment[other_var]):
            return False
    return True


def make_neighbors():
    neighbors = {}
    for i in range(3):
        for j in range(3):
            nb = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < 3 and 0 <= nj < 3:
                    nb.append((ni, nj))
            neighbors[(i, j)] = nb
    return neighbors


csp_cons["neighbors"] = make_neighbors()


def select_unassigned_variable_mrv(assignment, csp):
    unassigned = [v for v in csp["variables"] if v not in assignment]
    random.shuffle(unassigned)
    # đếm số giá trị khả dụng (consistent) cho mỗi var
    best, best_count = None, float("inf")
    for var in unassigned:
        cnt = sum(1 for val in csp["domains"][var] if is_consistent(assignment, var, val, csp))
        if cnt < best_count:
            best_count, best = cnt, var
    return best


lcv_cache = {}  # để cache impact (tùy chọn)


def satisfies_constraint(var1, val1, var2, val2, csp):
    """
    Kiểm tra ràng buộc nhị phân giữa hai biến, hỗ trợ:
     1) csp['constraints'] là function: f(var1, val1, var2, val2)->bool
     2) csp['constraints'] là dict: {(varA,varB): funcAB, …}
    """
    constraint_def = csp.get("constraints")

    # 1) Nếu là hàm chung, gọi trực tiếp
    if callable(constraint_def):
        return constraint_def(var1, val1, var2, val2)

    # 2) Nếu là dict, tìm key (var1,var2) hoặc (var2,var1)
    if isinstance(constraint_def, dict):
        func = constraint_def.get((var1, var2)) or constraint_def.get((var2, var1))
        if func is None:
            return True
        return func(val1, val2)

    # 3) Nếu không xác định được, coi như không có ràng buộc
    return True


def compute_prune_count(var, value, assignment, csp):
    prune = 0
    for nb in csp["neighbors"][var]:
        if nb in assignment:
            continue
        for v2 in csp["domains"][nb]:
            if not satisfies_constraint(var, value, nb, v2, csp):
                prune += 1
    return prune


def order_values_lcv(var, assignment, csp):
    impacts = []
    for val in csp["domains"][var]:
        if not is_consistent(assignment, var, val, csp):
            continue
        # tính prune chỉ cho var này
        key = (var, val)
        imp = lcv_cache.get(key) or compute_prune_count(var, val, assignment, csp)
        lcv_cache[key] = imp
        impacts.append((imp, val))
    # sắp tăng dần theo impact
    impacts.sort(key=lambda x: x[0])
    return [val for imp, val in impacts]


def backtracking_mrv_lcv_wrapper(csp):
    explorer = [0]
    result = backtracking_mrv_lcv({}, csp, explorer)
    return result, explorer[0]


def backtracking_mrv_lcv(assignment, csp, explorer):
    if len(assignment) == len(csp["variables"]):
        explorer[0] += 1
        return assignment if compare_state(assignment, GOAL_STATE) else None

    var = select_unassigned_variable_mrv(assignment, csp)

    for value in order_values_lcv(var, assignment, csp):
        explorer[0] += 1
        if is_consistent(assignment, var, value, csp):
            assignment[var] = value
            result = backtracking_mrv_lcv(assignment, csp, explorer)
            if result:
                return result
            del assignment[var]

    return None


# def backtracking_mrv_lcv(assignment, csp):
#     explorer = 0
#     if len(assignment) == len(csp["variables"]):
#         explorer += 1
#         return assignment, explorer if compare_state(assignment, GOAL_STATE) else None

#     # 1) Chọn biến theo MRV
#     var = select_unassigned_variable_mrv(assignment, csp)

#     # 2) Lấy giá trị đã order qua LCV
#     for value in order_values_lcv(var, assignment, csp):
#         if is_consistent(assignment, var, value, csp):
#             assignment[var] = value
#             result = backtracking_mrv_lcv(assignment, csp)
#             if result:
#                 return result
#             del assignment[var]
#     explorer += 1
#     return None, explorer

# def select_unassigned_variable_lcv(assignment, csp):
#     """
#     Chọn ô chưa gán sao cho việc gán giá trị vào ô này gây ảnh hưởng nhỏ nhất
#     (loại bỏ ít giá trị khỏi miền của các ô lân cận nhất).
#     """
#     unassigned_vars = [v for v in csp["variables"] if v not in assignment]
#     best_var = None
#     best_impact = float("inf")

#     for var in unassigned_vars:
#         # Tính mức độ tác động lớn nhất của việc gán bất kỳ giá trị nào cho var
#         max_neighbor_prune = 0
#         for value in csp["domains"][var]:
#             if not is_consistent(assignment, var, value, csp):
#                 continue
#             prune_count = 0
#             # Duyệt qua các biến lân cận để đếm số giá trị miền bị loại bỏ
#             for neighbor in csp.get("neighbors", {}).get(var, []):
#                 if neighbor in assignment:
#                     continue
#                 for v2 in csp["domains"][neighbor]:
#                     # Nếu không thỏa ràng buộc nhị phân giữa (var=value) và (neighbor=v2)
#                     if not satisfies_constraint(var, value, neighbor, v2, csp):
#                         prune_count += 1
#             max_neighbor_prune = max(max_neighbor_prune, prune_count)

#         # Chọn biến có mức độ tác động (prune) nhỏ nhất
#         if max_neighbor_prune < best_impact:
#             best_impact = max_neighbor_prune
#             best_var = var

#     return best_var

# def backtracking_lcv(assignment, csp):
#     # Nếu tất cả các biến đã được gán, kiểm tra kết quả
#     if len(assignment) == len(csp["variables"]):
#         if compare_state(assignment, GOAL_STATE):  # Bạn có thể thay GOAL_STATE bằng start_state nếu cần
#             return assignment
#         else:
#             return None

#     # Chọn biến chưa gán theo MRV (có ít khả năng lựa chọn nhất)
#     var = select_unassigned_variable_lcv(assignment, csp)
#     # Lấy dãy các giá trị từ domain của biến và trộn ngẫu nhiên để tăng tính ngẫu nhiên
#     values = csp["domains"][var][:]
#     random.shuffle(values)

# for value in values:
#     if csp["constraints"] is None or is_consistent(assignment, var, value, csp):
#         assignment[var] = value
#         result = backtracking_lcv(assignment, csp)
#         if result is not None:
#             return result
#         del assignment[var]
# return None


def solution_time(start_state, algo_type, stop_event=None):
    start_time = time.time()
    end_time = 0
    solution = None
    t0 = time.perf_counter()
    if algo_type == "dfs":
        solution, explorer = dfs(start_state)
        end_time = time.time()
    elif algo_type == "bfs":
        solution, explorer = bfs(start_state)
        end_time = time.time()
    elif algo_type == "ucs":
        solution, explorer = ucs(start_state)
        end_time = time.time()
    elif algo_type == "iddfs":
        solution, explorer = iddfs(start_state)
        end_time = time.time()
    elif algo_type == "gbfs":
        solution, explorer = gbfs(start_state)
        end_time = time.time()
    elif algo_type == "A_star":
        solution, explorer = A_star(start_state)
        end_time = time.time()
    elif algo_type == "ida_star":
        solution, explorer = ida_star(start_state)
        end_time = time.time()
    elif algo_type == "hill_simp":
        solution, explorer = hill_simp(start_state)
        end_time = time.time()
    elif algo_type == "hill_steepest":
        solution, explorer = hill_climbing_steepest(start_state)
        end_time = time.time()
    elif algo_type == "hill_stochastic":
        solution, explorer = hill_climbing_stochastic(start_state)
        end_time = time.time()
    elif algo_type == "beam":
        solution, explorer = beam_search(start_state)
        end_time = time.time()
    elif algo_type == "simulated_annealing":
        solution, explorer = simulated_annealing(start_state)
        end_time = time.time()
    elif algo_type == "genetic":
        solution, explorer = genetic(start_state)
        end_time = time.time()
    elif algo_type == "and_or":
        solution, explorer = and_or_search(start_state)
        end_time = time.time()
    elif algo_type == "backtracking":
        solution, explorer = backtracking(csp_simple)
        end_time = time.time()
    elif algo_type == "backtracking_constraint_propagation":
        solution, explorer = backtracking(csp_cons)
        end_time = time.time()
    elif algo_type == "backtracking_lcv":
        solution, explorer = backtracking_mrv_lcv_wrapper(csp_cons)
        end_time = time.time()

    elapsed_ms = (time.perf_counter() - t0) * 1000
    solved_flag = 1 if solution else 0
    # Mở file ở chế độ append và ghi dòng mới
    with open("results.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([algo_type, f"{elapsed_ms:.3f}", len(solution) if solution else 0, explorer, solved_flag])
    # execution_time = end_time - start_time
    return solution, elapsed_ms


def re_path(path, state):
    steps = []
    while state is not None:
        steps.append(state)
        state = path[hst(state)]
    return steps[::-1]


if __name__ == "__main__":
    # start_state = [[2, 6, 5], [8, 7, 0], [4, 3, 1]]
    # start_state = [[1, 2, 3], [4, 5, 6], [7, 0, 8]]
    start_state = [[1, 2, 3], [5, 0, 6], [4, 7, 8]]
    solution = genetic(start_state)
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
