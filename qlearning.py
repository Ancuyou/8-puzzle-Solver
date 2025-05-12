import copy
import os
import pickle
import random
import time
import csv

ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.3
Q_table = {}
Q_TABLE_FILE = "q_table.pkl"
GRID = 3
final_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]


class Node:
    def __init__(self, state):
        self.state = state

    def get_index_0(self):
        for i, row in enumerate(self.state):
            for j, val in enumerate(row):
                if val == 0:
                    return i, j
        raise ValueError("No zero found")


def heuristic(state):
    dist = 0
    for i in range(GRID):
        for j in range(GRID):
            v = state[i][j]
            if v != 0:
                # vị trí đích của giá trị v (1..8) là ((v-1)//3, (v-1)%3)
                goal_i, goal_j = divmod(v - 1, GRID)
                dist += abs(i - goal_i) + abs(j - goal_j)
    return dist


def get_state_key(state):
    return tuple(tuple(row) for row in state)


def get_possible_actions(state):
    x_0, y_0 = Node(state).get_index_0()
    actions = []
    if x_0 > 0:
        actions.append("up")
    if x_0 < GRID - 1:
        actions.append("down")
    if y_0 > 0:
        actions.append("left")
    if y_0 < GRID - 1:
        actions.append("right")
    return actions


def take_action(state, action):
    x_0, y_0 = Node(state).get_index_0()
    moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
    i, j = moves[action]
    new_i, new_j = x_0 + i, y_0 + j
    new_state = copy.deepcopy(state)
    new_state[x_0][y_0], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[x_0][y_0]
    return new_state


def reward_function(state):
    if state == final_state:
        return 100
    return -1 - heuristic(state) / 10


def perturb_state(state, steps=1):
    current_state = copy.deepcopy(state)
    for _ in range(steps):
        actions = get_possible_actions(current_state)
        if not actions:
            break
        action = random.choice(actions)
        current_state = take_action(current_state, action)
    return current_state


def save_q_table():
    with open(Q_TABLE_FILE, "wb") as f:
        pickle.dump(Q_table, f)
    print(f"Q-Learning: Q-table đã được lưu vào {Q_TABLE_FILE}")


def load_q_table():
    global Q_table
    if os.path.exists(Q_TABLE_FILE):
        with open(Q_TABLE_FILE, "rb") as f:
            Q_table = pickle.load(f)
        print(f"Q-Learning: Q-table đã được tải từ {Q_TABLE_FILE}, kích thước: {len(Q_table)}")
        return True
    return False


def train_q_learning(initial_state, episodes=2000, max_steps=200):
    print(">>> Bắt đầu train_q_learning", flush=True)
    global Q_table
    start_time = time.perf_counter()
    if load_q_table():
        print("Q-Learning: Sử dụng Q-table đã lưu, bỏ qua huấn luyện")
        return
    Q_table = {}
    for episode in range(episodes):
        if random.random() < 0.5:
            current_state = copy.deepcopy(initial_state)
        else:
            current_state = perturb_state(initial_state, steps=random.randint(1, 5))
        steps = 0
        while steps < max_steps:
            state_key = get_state_key(current_state)
            if state_key not in Q_table:
                Q_table[state_key] = {action: 0 for action in get_possible_actions(current_state)}
            if random.random() < EPSILON:
                action = random.choice(get_possible_actions(current_state))
            else:
                action = max(Q_table[state_key], key=Q_table[state_key].get)
            new_state = take_action(current_state, action)
            reward = reward_function(new_state)
            new_state_key = get_state_key(new_state)
            if new_state_key not in Q_table:
                Q_table[new_state_key] = {action: 0 for action in get_possible_actions(new_state)}
            best_next_action = max(Q_table[new_state_key], key=Q_table[new_state_key].get)
            Q_table[state_key][action] += ALPHA * (reward + GAMMA * Q_table[new_state_key][best_next_action] - Q_table[state_key][action])
            current_state = new_state
            steps += 1
            if current_state == final_state:
                break
        if (episode + 1) % 3 == 0:
            print(f"Q-Learning: Hoàn thành {episode + 1}/{episodes} episode, kích thước Q-table: {len(Q_table)}")
    end_time = time.perf_counter()
    print(f"Q-Learning: Huấn luyện hoàn tất, Thời gian: {end_time - start_time:.4f}s, Kích thước Q-table: {len(Q_table)}")
    save_q_table()


def q_learning(state, episodes=2000, max_steps=200):
    t0 = time.perf_counter()
    if not Q_table and not load_q_table():
        print("Q-Learning: Huấn luyện Q-table...")
        train_q_learning(state, episodes, max_steps)
    solution = []
    current_state = copy.deepcopy(state)
    visited = set()
    steps = 0
    state_key = get_state_key(current_state)
    if state_key not in Q_table:
        Q_table[state_key] = {action: 0 for action in get_possible_actions(current_state)}
    while current_state != final_state and steps < max_steps:
        state_key = get_state_key(current_state)
        visited.add(state_key)
        actions = get_possible_actions(current_state)
        if not actions:
            print("Q-Learning: Không có hành động hợp lệ")
            break
        action = max(Q_table[state_key], key=Q_table[state_key].get)
        new_state = take_action(current_state, action)
        new_state_key = get_state_key(new_state)
        if new_state_key not in Q_table:
            Q_table[new_state_key] = {action: 0 for action in get_possible_actions(new_state)}
        if new_state_key in visited:
            print("Q-Learning: Phát hiện vòng lặp, thử hành động khác")
            alternative_actions = [a for a in actions if a != action]
            if not alternative_actions:
                print("Q-Learning: Không có hành động thay thế, dừng lại")
                break
            action = random.choice(alternative_actions)
            new_state = take_action(current_state, action)
            new_state_key = get_state_key(new_state)
            if new_state_key not in Q_table:
                Q_table[new_state_key] = {action: 0 for action in get_possible_actions(new_state)}
        solution.append(Node(current_state))
        current_state = new_state
        steps += 1
    if current_state == final_state:
        solution.append(Node(current_state))
        end_time = time.perf_counter()
        print(f"Q-Learning: Tìm thấy giải pháp, Thời gian: {end_time - t0:.3f}s, Số bước: {len(solution)-1}")
    else:
        solution.append(Node(current_state))
        end_time = time.perf_counter()
        print(f"Q-Learning: Không tìm thấy giải pháp, Thời gian: {end_time - t0:.3f}s, Số bước: {len(solution)-1}")
    # sau khi tính xong solution và elapsed_ms:
    solved_flag = 1 if current_state == final_state else 0
    elapsed_ms = (time.perf_counter() - t0) * 1000
    with open("results.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["QLearning", f"{elapsed_ms:.3f}", len(solution) - 1, 0, solved_flag])  # explorer count (tabular Q-Learning ko track)
    nodes = solution
    states = [node.state for node in nodes]
    return states, elapsed_ms


if __name__ == "__main__":
    initial = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    train_q_learning(initial, episodes=2000, max_steps=200)
