import random
import threading
import time
from queue import Queue

import matplotlib.pyplot as plt
import pandas as pd
import pygame
from matplotlib.backends.backend_agg import FigureCanvasAgg

from logic import solution_time

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 600
PUZZLE_AREA_HEIGHT = 250

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
GRAY = (200, 200, 200)
DARKGRAY = (100, 100, 100)
LIGHTGRAY = (130, 130, 130)
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("8-Puzzle Solver")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

TILE_SIZE = 60
PUZZLE_WIDTH = TILE_SIZE * 3
PUZZLE_HEIGHT = TILE_SIZE * 3
LEFT_PUZZLE_OFFSET = (127, 20)
LEFT_TEXT = (177, 200)
RIGHT_PUZZLE_OFFSET = (347, 20)
RIGHT_TEXT = (397, 200)
CENTER_PUZZLE_OFFSET = (140, 20)


def draw_puzzle(surface, state, offset=(0, 0)):
    x_offset, y_offset = offset
    pygame.draw.rect(surface, WHITE, (x_offset, y_offset, PUZZLE_WIDTH, PUZZLE_HEIGHT))
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            rect = pygame.Rect(x_offset + j * TILE_SIZE, y_offset + i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if value != 0:
                pygame.draw.rect(surface, BLUE, rect)
                text = font_large.render(str(value), True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)
            pygame.draw.rect(surface, BLACK, rect, 2)


class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = DARKGRAY
        self.hover_color = GRAY

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        txt_surface = font_small.render(self.text, True, BLACK)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        surface.blit(txt_surface, txt_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Slider:
    def __init__(self, rect, min_val, max_val, init_val):
        self.rect = pygame.Rect(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.value = init_val
        self.knob_radius = 10
        self.knob_x = self.value_to_pos(self.value)
        self.dragging = False

    def value_to_pos(self, value):
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + int(ratio * self.rect.width)

    def pos_to_value(self, pos_x):
        ratio = (pos_x - self.rect.x) / self.rect.width
        return self.min_val + ratio * (self.max_val - self.min_val)

    def draw(self, surface):
        pygame.draw.rect(surface, DARKGRAY, self.rect)
        self.knob_x = self.value_to_pos(self.value)
        knob_center = (self.knob_x, self.rect.centery)
        pygame.draw.circle(surface, RED, knob_center, self.knob_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(self.knob_x - self.knob_radius, self.rect.centery - self.knob_radius, self.knob_radius * 2, self.knob_radius * 2).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = min(max(event.pos[0], self.rect.x), self.rect.x + self.rect.width)
                self.value = self.pos_to_value(new_x)


def draw_thumbnail(surface, state, offset, thumb_size):
    thumb_width = thumb_size * 3
    thumb_height = thumb_size * 3
    x_offset, y_offset = offset
    pygame.draw.rect(surface, WHITE, (x_offset, y_offset, thumb_width, thumb_height))
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            rect = pygame.Rect(x_offset + j * thumb_size, y_offset + i * thumb_size, thumb_size, thumb_size)
            if value != 0:
                pygame.draw.rect(surface, BLUE, rect)
                text = font_small.render(str(value), True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)
            pygame.draw.rect(surface, BLACK, rect, 1)


def animate_solution(solution, slider, time_solved):
    running = True
    i = 0
    btn_menu = Button((WINDOW_WIDTH - 110, PUZZLE_HEIGHT + 50, 100, 40), "Menu")
    THUMB_SIZE = 30
    THUMB_PUZZLE_WIDTH = THUMB_SIZE * 3
    THUMB_PUZZLE_HEIGHT = THUMB_SIZE * 3
    visible_count = 5
    scroll_index = 0
    btn_left = Button((WINDOW_WIDTH / 2 - 35, PUZZLE_HEIGHT + 270, 30, 30), "<")
    btn_right = Button((WINDOW_WIDTH / 2 + 5, PUZZLE_HEIGHT + 270, 30, 30), ">")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if btn_menu.is_clicked(event):
                return
            slider.handle_event(event)
            if btn_left.is_clicked(event):
                scroll_index = max(scroll_index - 1, 0)
            if btn_right.is_clicked(event):
                if scroll_index + visible_count < len(solution):
                    scroll_index += 1
        delay = slider.value
        screen.fill(WHITE)
        draw_puzzle(screen, start_state, offset=LEFT_PUZZLE_OFFSET)
        if i < len(solution):
            draw_puzzle(screen, solution[i], offset=RIGHT_PUZZLE_OFFSET)
        else:
            draw_puzzle(screen, solution[-1], offset=RIGHT_PUZZLE_OFFSET)
        info_text = f"Steps: {i}  Time: {time_solved:.1f}s"
        info_surface = font_small.render(info_text, True, BLACK)
        screen.blit(info_surface, (10, PUZZLE_HEIGHT + 70))
        btn_menu.draw(screen)
        slider.draw(screen)
        slider_text = font_small.render(f"Delay: {slider.value:.3f}s", True, BLACK)
        screen.blit(slider_text, (320, PUZZLE_AREA_HEIGHT + 300))
        btn_left.draw(screen)
        btn_right.draw(screen)
        gap = 3
        for idx in range(visible_count):
            step_idx = scroll_index + idx
            if step_idx >= len(solution):
                break
            thumb_x = 85 + idx * (THUMB_PUZZLE_WIDTH + gap)
            thumb_y = PUZZLE_HEIGHT + 160
            draw_thumbnail(screen, solution[step_idx], (thumb_x, thumb_y), THUMB_SIZE)
            step_text = font_small.render(str(step_idx), True, BLACK)
            text_rect = step_text.get_rect(center=(thumb_x + THUMB_PUZZLE_WIDTH // 2, thumb_y + THUMB_PUZZLE_HEIGHT + 10))
            screen.blit(step_text, text_rect)

        pygame.display.flip()
        if i < len(solution):
            wait_start = time.time()
            while time.time() - wait_start < delay:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        return
                    if btn_menu.is_clicked(event):
                        return
                    slider.handle_event(event)
                    if btn_left.is_clicked(event):
                        scroll_index = max(scroll_index - 1, 0)
                    if btn_right.is_clicked(event):
                        if scroll_index + visible_count < len(solution):
                            scroll_index += 1
                    delay = slider.value
                clock.tick(60)
            i += 1
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if btn_menu.is_clicked(event):
                    return
                slider.handle_event(event)
                if btn_left.is_clicked(event):
                    scroll_index = max(scroll_index - 1, 0)
                if btn_right.is_clicked(event):
                    if scroll_index + visible_count < len(solution):
                        scroll_index += 1
            clock.tick(60)


def partial_belief_interface(steps, goal_states, time_solved):
    """
    Display all frontiers on the left in a scrollable grid (4 per row),
    and goal states on the right similarly, each with its own scrollbar.
    Back button + Steps/Time info below the goals.
    """
    running = True

    # Scrollbar width
    BAR_W = 12

    # Layout constants
    SCREEN_W, SCREEN_H = WINDOW_WIDTH, WINDOW_HEIGHT
    MARGIN = 20

    # Left area: holds the frontiers
    LEFT_W = SCREEN_W * 2 // 3
    LEFT_X = MARGIN
    LEFT_Y = MARGIN
    LEFT_W_INSIDE = LEFT_W - BAR_W - 2 * MARGIN
    LEFT_H_INSIDE = SCREEN_H - 2 * MARGIN - 10  # leave space at bottom

    # Right area: holds the goals + back/info
    RIGHT_X = LEFT_W + MARGIN
    RIGHT_Y = MARGIN
    RIGHT_W_INSIDE = SCREEN_W - RIGHT_X - BAR_W - MARGIN
    RIGHT_H_INSIDE = LEFT_H_INSIDE

    SMALL_TILE = 32
    SMALL_PUZZLE = SMALL_TILE * 3
    SPACING = 10
    GROUP_GAP = 30

    # Scrollbars
    left_bar = pygame.Rect(LEFT_X + LEFT_W_INSIDE + MARGIN, LEFT_Y, BAR_W, LEFT_H_INSIDE)
    right_bar = pygame.Rect(RIGHT_X + RIGHT_W_INSIDE + MARGIN, RIGHT_Y, BAR_W, RIGHT_H_INSIDE)

    # Precompute total content heights
    total_left_h = 0
    for frontier in steps:
        rows = max(1, (len(frontier) + 3) // 4)
        total_left_h += SPACING + 40 + rows * (SMALL_PUZZLE + SPACING) + GROUP_GAP

    total_right_h = len(goal_states) * (SMALL_PUZZLE + SPACING)

    left_scroll = 0
    right_scroll = 0
    dragging_left = False
    dragging_right = False
    drag_off_y = 0

    btn_back = Button((RIGHT_X, SCREEN_H - 60, 100, 40), "Back")

    # height of the "Frontier N:" label
    frontier_label_height = font_small.get_height()

    while running:
        # recompute thumb sizes
        max_ls = max(total_left_h - LEFT_H_INSIDE + 50, 0)
        thumb_h_l = max(int(left_bar.height * LEFT_H_INSIDE / total_left_h), BAR_W)

        max_rs = max(total_right_h - RIGHT_H_INSIDE, 0)
        thumb_h_r = max(int(right_bar.height * RIGHT_H_INSIDE / total_right_h), BAR_W)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if btn_back.is_clicked(ev):
                return

            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos

                # compute thumbs
                thumb_y_l = LEFT_Y + int((left_bar.height - thumb_h_l) * left_scroll / max(1, max_ls))
                thumb_rect_l = pygame.Rect(left_bar.x, thumb_y_l, BAR_W, thumb_h_l)

                thumb_y_r = RIGHT_Y + int((right_bar.height - thumb_h_r) * right_scroll / max(1, max_rs))
                thumb_rect_r = pygame.Rect(right_bar.x, thumb_y_r, BAR_W, thumb_h_r)

                if thumb_rect_l.collidepoint(mx, my):
                    dragging_left = True
                    drag_off_y = my - thumb_y_l
                elif thumb_rect_r.collidepoint(mx, my):
                    dragging_right = True
                    drag_off_y = my - thumb_y_r

            elif ev.type == pygame.MOUSEBUTTONUP:
                dragging_left = dragging_right = False

            elif ev.type == pygame.MOUSEMOTION:
                mx, my = ev.pos
                if dragging_left:
                    rel = my - LEFT_Y - drag_off_y
                    rel = max(0, min(rel, left_bar.height - thumb_h_l))
                    left_scroll = int(rel * max_ls / (left_bar.height - thumb_h_l))
                if dragging_right:
                    rel = my - RIGHT_Y - drag_off_y
                    rel = max(0, min(rel, right_bar.height - thumb_h_r))
                    right_scroll = int(rel * max_rs / (right_bar.height - thumb_h_r))

        screen.fill(WHITE)

        # Draw left content with clipping
        left_clip = pygame.Rect(LEFT_X, LEFT_Y, LEFT_W_INSIDE, LEFT_H_INSIDE)
        screen.set_clip(left_clip)
        y = LEFT_Y - left_scroll
        for i, frontier in enumerate(steps):
            # label
            lbl = font_small.render(f"Frontier {i+1}:", True, BLACK)
            screen.blit(lbl, (LEFT_X, y))
            y += frontier_label_height + SPACING

            # grid: 4 per row
            for idx, st in enumerate(frontier):
                row = idx // 3
                col = idx % 3
                x = LEFT_X + col * (SMALL_PUZZLE + SPACING)
                sy = y + row * (SMALL_PUZZLE + SPACING)
                draw_puzzle(screen, st, offset=(x, sy), tile_size=SMALL_TILE)
            rows = max(1, (len(frontier) + 3) // 4)
            y += rows * (SMALL_PUZZLE + SPACING) + GROUP_GAP
        screen.set_clip(None)

        # Left scrollbar
        pygame.draw.rect(screen, LIGHTGRAY, left_bar)
        thumb_y_l = LEFT_Y + int((left_bar.height - thumb_h_l) * left_scroll / max(1, max_ls))
        pygame.draw.rect(screen, DARKGRAY, (left_bar.x, thumb_y_l, BAR_W, thumb_h_l))

        # Draw right content with clipping
        right_clip = pygame.Rect(RIGHT_X, RIGHT_Y, RIGHT_W_INSIDE, RIGHT_H_INSIDE)
        screen.set_clip(right_clip)
        y2 = RIGHT_Y - right_scroll
        for st in goal_states:
            draw_puzzle(screen, st, offset=(RIGHT_X, y2), tile_size=SMALL_TILE)
            y2 += SMALL_PUZZLE + SPACING
        screen.set_clip(None)

        # Right scrollbar
        pygame.draw.rect(screen, LIGHTGRAY, right_bar)
        thumb_y_r = RIGHT_Y + int((right_bar.height - thumb_h_r) * right_scroll / max(1, max_rs))
        pygame.draw.rect(screen, DARKGRAY, (right_bar.x, thumb_y_r, BAR_W, thumb_h_r))

        # Back button and info
        btn_back.draw(screen)
        info = font_small.render(f"Steps: {len(steps)-1}   Time: {time_solved:.2f}s", True, BLACK)
        screen.blit(info, (RIGHT_X, SCREEN_H - 20))

        pygame.display.flip()
        clock.tick(60)


# def partial_belief_interface(steps, goal_states, time_solved):
#     running = True
#     step_idx = 0
#     max_step = len(steps) - 1
#     belief_scroll = 0
#     goal_scroll = 0

#     # Số puzzle hiển thị trên một cột
#     BELIEF_SHOW = 5
#     GOAL_SHOW = 5

#     # Kích thước
#     SMALL_TILE = 32
#     SMALL_PUZZLE = SMALL_TILE * 3
#     SPACE_Y = 10

#     # Vị trí khung hiển thị belief và goal
#     BELIEF_X, BELIEF_Y = 40, 40
#     GOAL_X, GOAL_Y = 400, 40

#     # Các nút điều khiển
#     btn_back = Button((WINDOW_WIDTH // 2 - 70, PUZZLE_AREA_HEIGHT + 40, 100, 40), "Back")
#     btn_step_left = Button((WINDOW_WIDTH // 2 - 100, PUZZLE_AREA_HEIGHT + 100, 40, 40), "<")
#     btn_step_right = Button((WINDOW_WIDTH // 2 + 20, PUZZLE_AREA_HEIGHT + 100, 40, 40), ">")
#     btn_belief_up = Button((BELIEF_X + SMALL_PUZZLE + 10, BELIEF_Y, 50, 30), "Up")
#     btn_belief_down = Button((BELIEF_X + SMALL_PUZZLE + 10, BELIEF_Y + 40, 50, 30), "Down")
#     btn_goal_up = Button((GOAL_X - 60, GOAL_Y, 50, 30), "Up")
#     btn_goal_down = Button((GOAL_X - 60, GOAL_Y + 40, 50, 30), "Down")

#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 return
#             if btn_back.is_clicked(event):
#                 return
#             if btn_step_left.is_clicked(event):
#                 step_idx = max(0, step_idx - 1)
#                 belief_scroll = goal_scroll = 0
#             if btn_step_right.is_clicked(event):
#                 step_idx = min(max_step, step_idx + 1)
#                 belief_scroll = goal_scroll = 0
#             if btn_belief_up.is_clicked(event):
#                 belief_scroll = max(0, belief_scroll - 1)
#             if btn_belief_down.is_clicked(event):
#                 if belief_scroll + BELIEF_SHOW < len(steps[step_idx]):
#                     belief_scroll += 1
#             if btn_goal_up.is_clicked(event):
#                 goal_scroll = max(0, goal_scroll - 1)
#             if btn_goal_down.is_clicked(event):
#                 if goal_scroll + GOAL_SHOW < len(goal_states):
#                     goal_scroll += 1

#         screen.fill(WHITE)

#         # Vẽ các belief states của frontier hiện tại
#         current_frontier = steps[step_idx]
#         for i in range(BELIEF_SHOW):
#             idx = belief_scroll + i
#             if idx >= len(current_frontier):
#                 break
#             state = current_frontier[idx]
#             draw_puzzle(screen, state, offset=(BELIEF_X, BELIEF_Y + i * (SMALL_PUZZLE + SPACE_Y)), tile_size=SMALL_TILE)

#         # Vẽ các goal states cố định
#         for i in range(GOAL_SHOW):
#             idx = goal_scroll + i
#             if idx >= len(goal_states):
#                 break
#             goal = goal_states[idx]
#             draw_puzzle(screen, goal, offset=(GOAL_X, GOAL_Y + i * (SMALL_PUZZLE + SPACE_Y)), tile_size=SMALL_TILE)

#         # Hiển thị các nút
#         btn_belief_up.draw(screen)
#         btn_belief_down.draw(screen)
#         btn_goal_up.draw(screen)
#         btn_goal_down.draw(screen)
#         btn_step_left.draw(screen)
#         btn_step_right.draw(screen)
#         btn_back.draw(screen)

#         # Thông tin bước và thời gian
#         info = font_small.render(f"Step: {step_idx}/{max_step}   Time: {time_solved:.2f}s", True, BLACK)
#         screen.blit(info, (WINDOW_WIDTH // 2 - info.get_width() // 2, PUZZLE_AREA_HEIGHT + 150))

#         pygame.display.flip()
#         clock.tick(60)


# def belief_state_interface(steps, goal_states, time_solved):
#     """
#     Draw sequence of frontiers. 'steps' is list of frontiers per time step.
#     Each frontier is list of states to display.
#     Similar to partial_belief_interface but generic naming.
#     """
#     running = True
#     step_idx = 0
#     max_step = len(steps) - 1
#     scroll = 0
#     SHOW = 5
#     TILE = 32
#     PUZZLE_SZ = TILE * 3
#     X0, Y0 = 40, 40
#     SPACE = 10

#     btn_back = Button((...), "Back")
#     btn_left = Button((...), "<")
#     btn_right = Button((...), ">")
#     btn_up = Button((...), "Up")
#     btn_down = Button((...), "Down")

#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 return
#             if btn_back.is_clicked(event):
#                 return
#             if btn_left.is_clicked(event):
#                 step_idx = max(0, step_idx - 1)
#                 scroll = 0
#             if btn_right.is_clicked(event):
#                 step_idx = min(max_step, step_idx + 1)
#                 scroll = 0
#             if btn_up.is_clicked(event):
#                 scroll = max(0, scroll - 1)
#             if btn_down.is_clicked(event):
#                 if scroll + SHOW < len(steps[step_idx]):
#                     scroll += 1

#         screen.fill(WHITE)
#         # draw frontiers
#         for i in range(SHOW):
#             idx = scroll + i
#             if idx >= len(steps[step_idx]):
#                 break
#             draw_puzzle(screen, steps[step_idx][idx], offset=(X0, Y0 + i * (PUZZLE_SZ + SPACE)), tile_size=TILE)

#         # draw goals on side
#         for gi, g in enumerate(goal_states[:SHOW]):
#             draw_puzzle(screen, g, offset=(X0 + 300, Y0 + gi * (PUZZLE_SZ + SPACE)), tile_size=TILE)

#         btn_back.draw(screen)
#         btn_left.draw(screen)
#         btn_right.draw(screen)
#         btn_up.draw(screen)
#         btn_down.draw(screen)

#         info = font.render(f"Step {step_idx}/{max_step}  Time {time_solved:.2f}s", True, BLACK)
#         screen.blit(info, (X0, Y0 + SHOW * (PUZZLE_SZ + SPACE) + 20))
#         pygame.display.flip()
#         clock.tick(60)


def backtracking_interface(final_assignment, time_solved):
    """
    final_assignment: dictionary chứa lời giải cuối của backtracking
                      (key: (row, col), value: số từ 0 đến 8, với 0 là ô trống)
    Phiên bản này vẽ ra một puzzle nền xanh dương có viền đen,
    ban đầu là puzzle rỗng, sau đó dần điền các số (ngoại trừ 0)
    theo thứ tự các ô (theo sorted keys). Bên dưới hiển thị thông tin steps, time và nút Menu.
    Nhấn ESC hoặc nút Menu để thoát về menu chính.
    """
    # Tạo danh sách các bước animation: ban đầu là puzzle rỗng, sau đó dần điền các ô theo thứ tự sorted key.
    sorted_keys = final_assignment.keys()
    steps = []  # mỗi phần tử là một assignment (dict) chứa dần các ô đã điền.
    current_assignment = {}
    steps.append(current_assignment.copy())  # bước 0: puzzle rỗng
    for key in sorted_keys:
        # Nếu final_assignment[key] khác 0 thì gán, còn nếu là 0 thì vẫn giữ ô trống.
        if final_assignment[key] != 0:
            current_assignment[key] = final_assignment[key]
        else:
            current_assignment[key] = 0
        steps.append(current_assignment.copy())
    total_steps = len(steps) - 1

    # Nút Menu để quay lại menu chính
    btn_menu = Button((WINDOW_WIDTH - 120, PUZZLE_HEIGHT + 20, 100, 40), "Menu")

    # Vị trí hiển thị puzzle: ở phía trên (centering theo chiều ngang)
    board_x = WINDOW_WIDTH // 2 - PUZZLE_WIDTH // 2
    board_y = 40  # cách trên màn hình 40 pixel

    # Hàm vẽ puzzle nền xanh dương với viền đen
    def draw_puzzle_blue(surface, state, offset=(0, 0), tile_size=TILE_SIZE):
        x_offset, y_offset = offset
        # Vẽ nền xanh cho toàn puzzle
        pygame.draw.rect(surface, BLUE, (x_offset, y_offset, PUZZLE_WIDTH, PUZZLE_HEIGHT))
        # Vẽ từng ô; nếu số khác 0 thì in số (với màu chữ trắng), còn nếu = 0 thì chỉ vẽ viền.
        for i in range(3):
            for j in range(3):
                rect = pygame.Rect(x_offset + j * tile_size, y_offset + i * tile_size, tile_size, tile_size)
                value = state[i][j]
                if value != 0:
                    # Vẽ ô có nền xanh (giữ nguyên màu nền) và in số trắng
                    text = font_large.render(str(value), True, WHITE)
                    text_rect = text.get_rect(center=rect.center)
                    surface.blit(text, text_rect)
                pygame.draw.rect(surface, BLACK, rect, 2)

    running = True
    step_idx = 0
    delay = 0.8  # thời gian delay giữa các bước animation (giây)
    last_update = time.time()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return
            if btn_menu.is_clicked(event):
                return

        # Tự động tiến animation sau khoảng delay
        if time.time() - last_update >= delay and step_idx < total_steps:
            step_idx += 1
            last_update = time.time()

        # Tái tạo state dựa trên assignment của bước hiện tại
        state = [[0 for _ in range(3)] for _ in range(3)]
        current_state_assignment = steps[step_idx]
        for i in range(3):
            for j in range(3):
                if (i, j) in current_state_assignment:
                    state[i][j] = current_state_assignment[(i, j)]

        screen.fill(WHITE)
        # Vẽ puzzle với nền xanh dương ở vị trí board_x, board_y
        draw_puzzle_blue(screen, state, offset=(board_x, board_y))

        # Vẽ thông tin bên dưới: step hiện tại và thời gian
        info = font_small.render(f"Steps: {step_idx}/{total_steps}   Time: {time_solved:.2f}s", True, BLACK)
        screen.blit(info, (50, PUZZLE_AREA_HEIGHT + 10))
        # Vẽ nút Menu
        btn_menu.draw(screen)
        # Hướng dẫn (ESC hoặc Menu để thoát)
        help_text = font_small.render("ESC or Menu", True, BLACK)
        screen.blit(help_text, (50, PUZZLE_AREA_HEIGHT + 40))

        pygame.display.flip()
        clock.tick(60)


def draw_puzzle(surface, state, offset=(0, 0), tile_size=TILE_SIZE):
    x_offset, y_offset = offset
    puzzle_width = tile_size * 3
    puzzle_height = tile_size * 3
    pygame.draw.rect(surface, WHITE, (x_offset, y_offset, puzzle_width, puzzle_height))
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            rect = pygame.Rect(x_offset + j * tile_size, y_offset + i * tile_size, tile_size, tile_size)
            if value != 0:
                pygame.draw.rect(surface, BLUE, rect)
                text = font_large.render(str(value), True, WHITE) if tile_size >= 40 else font_small.render(str(value), True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)
            pygame.draw.rect(surface, BLACK, rect, 2)


def run_backtracking(algo, start_state, thread_manager, result_queue, stop_event):
    solution, time_solved = solution_time(start_state, algo, stop_event)
    if not stop_event.is_set():
        result_queue.append((solution, time_solved))
    thread_manager.threads = [t for t in thread_manager.threads if t[0] != threading.current_thread()]


class ThreadManager:
    def __init__(self):
        self.threads = []

    def add_thread(self, thread, stop_event):
        self.threads.append((thread, stop_event))

    def cancel_all(self):
        for _, stop_event in self.threads:
            stop_event.set()
        self.threads = []


def show_analysis_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
    # 1) Resize Pygame window lên lớn hơn
    ANALYSIS_W, ANALYSIS_H = 800, 700
    pygame.display.set_mode((ANALYSIS_W, ANALYSIS_H))

    # 2) Đọc CSV và tính số liệu
    df = pd.read_csv("results.csv", names=["algo", "time", "steps", "explored", "solved"])
    grouped = df.groupby("algo")
    algos = sorted(grouped.groups.keys())

    avg_time = grouped["time"].mean()
    avg_steps = grouped["steps"].mean()
    avg_explored = grouped["explored"].mean()
    success_rate = grouped["solved"].mean() * 100

    stats = {"Time (ms)": avg_time, "Steps": avg_steps, "Explored": avg_explored, "Success (%)": success_rate}

    # 3) Vẽ 4 biểu đồ thành surfaces
    surfaces = []
    for title, series in stats.items():
        fig = plt.figure(figsize=(3.5, 3))  # ~350×300 px
        ax = fig.add_subplot(111)
        ax.bar(algos, series[algos])
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        raw = canvas.tostring_rgb()
        w, h = canvas.get_width_height()
        surf = pygame.image.fromstring(raw, (w, h), "RGB")
        surfaces.append(surf)
        plt.close(fig)

    # 4) Hiển thị trong loop, 2×2 grid
    positions = [(20, 20), (420, 20), (20, 360), (420, 360)]  # top-left  # top-right  # bottom-left  # bottom-right

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

        screen.fill((255, 255, 255))
        for surf, pos in zip(surfaces, positions):
            screen.blit(surf, pos)

        pygame.display.flip()
        clock.tick(30)

    # 5) Khôi phục lại kích thước cũ
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


def main():
    global start_state
    start_state = [[1, 2, 3], [5, 0, 6], [4, 7, 8]]
    # start_state = [[1, 2, 3], [4, 5, 6], [7, 0, 8]]
    goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    algo_selected = None

    time_solved = 0
    is_processing = False
    thread_manager = ThreadManager()
    result_queue = []

    btn_bfs = Button((50, PUZZLE_AREA_HEIGHT + 50, 100, 40), "BFS")
    btn_dfs = Button((200, PUZZLE_AREA_HEIGHT + 50, 100, 40), "DFS")
    btn_ucs = Button((350, PUZZLE_AREA_HEIGHT + 50, 100, 40), "UCS")
    btn_part_belief = Button((500, PUZZLE_AREA_HEIGHT + 50, 100, 40), "Part_Belief")
    btn_iddfs = Button((50, PUZZLE_AREA_HEIGHT + 100, 100, 40), "IDDFS")
    btn_gbfs = Button((200, PUZZLE_AREA_HEIGHT + 100, 100, 40), "GBFS")
    btn_Astar = Button((350, PUZZLE_AREA_HEIGHT + 100, 100, 40), "A*")
    btn_backtrack = Button((500, PUZZLE_AREA_HEIGHT + 100, 100, 40), "BT")
    btn_ida_star = Button((50, PUZZLE_AREA_HEIGHT + 150, 100, 40), "IDA*")
    btn_hill_simp = Button((200, PUZZLE_AREA_HEIGHT + 150, 100, 40), "H_SIMP")
    btn_hill_step = Button((350, PUZZLE_AREA_HEIGHT + 150, 100, 40), "H_STEEP")
    btn_backtrack_cons = Button((500, PUZZLE_AREA_HEIGHT + 150, 100, 40), "BT_CONS")
    btn_hill_stocha = Button((50, PUZZLE_AREA_HEIGHT + 200, 100, 40), "H_STOR")
    btn_beam = Button((200, PUZZLE_AREA_HEIGHT + 200, 100, 40), "BEAM")
    btn_sa = Button((350, PUZZLE_AREA_HEIGHT + 200, 100, 40), "SA")
    btn_backtrack_heus = Button((500, PUZZLE_AREA_HEIGHT + 200, 100, 40), "BT_HEU")
    btn_genetic = Button((50, PUZZLE_AREA_HEIGHT + 250, 100, 40), "Genetic")
    btn_and_or = Button((200, PUZZLE_AREA_HEIGHT + 250, 100, 40), "And_Or")
    btn_belief = Button((350, PUZZLE_AREA_HEIGHT + 250, 100, 40), "Belief")
    btn_ql = Button((500, PUZZLE_AREA_HEIGHT + 250, 100, 40), "QLearning")
    btn_random = Button((277, PUZZLE_AREA_HEIGHT, 100, 40), "Random")
    btn_analysis = Button((400, PUZZLE_AREA_HEIGHT + 300, 100, 40), "Analysis")
    slider = Slider((50, PUZZLE_AREA_HEIGHT + 300, 250, 20), 0.01, 2.0, 1.0)
    btn_back = Button((WINDOW_WIDTH - 120, PUZZLE_AREA_HEIGHT + 300, 100, 40), "Back")
    running = True
    animating = False
    solution_solved = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                thread_manager.cancel_all()
                running = False
            elif btn_random.is_clicked(event):
                lst = random.sample(range(9), 9)
                start_state = [lst[i * 3 : (i + 1) * 3] for i in range(3)]
            elif btn_bfs.is_clicked(event):
                algo_selected = "bfs"
                solution_solved, time_solved = solution_time(start_state, "bfs")
                animating = True
            elif btn_dfs.is_clicked(event):
                algo_selected = "dfs"
                solution_solved, time_solved = solution_time(start_state, "dfs")
                animating = True
            elif btn_ucs.is_clicked(event):
                algo_selected = "ucs"
                solution_solved, time_solved = solution_time(start_state, "ucs")
                animating = True
            elif btn_iddfs.is_clicked(event):
                algo_selected = "iddfs"
                solution_solved, time_solved = solution_time(start_state, "iddfs")
                animating = True
            elif btn_gbfs.is_clicked(event):
                algo_selected = "gbfs"
                solution_solved, time_solved = solution_time(start_state, "gbfs")
                animating = True
            elif btn_Astar.is_clicked(event):
                algo_selected = "A*"
                solution_solved, time_solved = solution_time(start_state, "A_star")
                animating = True
            elif btn_ida_star.is_clicked(event):
                algo_selected = "IDA*"
                solution_solved, time_solved = solution_time(start_state, "ida_star")
                animating = True
            elif btn_hill_simp.is_clicked(event):
                algo_selected = "HillClimbing_Simple"
                solution_solved, time_solved = solution_time(start_state, "hill_simp")
                animating = True
            elif btn_hill_step.is_clicked(event):
                algo_selected = "HillClimbing_Steepest"
                solution_solved, time_solved = solution_time(start_state, "hill_steepest")
                animating = True
            elif btn_hill_stocha.is_clicked(event):
                algo_selected = "HillClimbing_Stochastic"
                solution_solved, time_solved = solution_time(start_state, "hill_stochastic")
                animating = True
            elif btn_beam.is_clicked(event):
                algo_selected = "Beam"
                solution_solved, time_solved = solution_time(start_state, "beam")
                animating = True
            elif btn_sa.is_clicked(event):
                algo_selected = "simulated_annealing"
                solution_solved, time_solved = solution_time(start_state, "simulated_annealing")
                animating = True
            elif btn_genetic.is_clicked(event):
                algo_selected = "genetic"
                solution_solved, time_solved = solution_time(start_state, "genetic")
                animating = True
            elif btn_and_or.is_clicked(event):
                algo_selected = "and or"
                solution_solved, time_solved = solution_time(start_state, "and_or")
                animating = True
            elif btn_part_belief.is_clicked(event):
                algo_selected = "partial belief"
                # Giả định 3 trạng thái bắt đầu và 2 goal
                start_states = [
                    [[1, 2, 3], [4, 5, 6], [7, 0, 8]],
                    [[1, 2, 3], [4, 0, 6], [7, 5, 8]],
                    [[1, 2, 3], [4, 5, 0], [7, 6, 8]],
                ]
                goal_states = [
                    [[1, 2, 3], [4, 5, 6], [7, 8, 0]],
                    [[1, 2, 3], [4, 5, 6], [0, 7, 8]],
                ]
                from logic import search_with_partial_observation

                steps, time_solved = search_with_partial_observation(start_states, goal_states)
                partial_belief_interface(steps, goal_states, time_solved)
            elif btn_belief.is_clicked(event):
                algo_selected = "belief"
                # Giả định 3 trạng thái bắt đầu và 2 goal
                start_states = [
                    [[1, 2, 3], [4, 5, 6], [7, 0, 8]],
                    [[1, 2, 3], [4, 0, 6], [7, 5, 8]],
                    [[1, 2, 3], [4, 5, 0], [7, 6, 8]],
                ]
                goal_states = [
                    [[1, 2, 3], [4, 5, 6], [7, 8, 0]],
                    [[1, 2, 3], [4, 5, 6], [0, 7, 8]],
                ]
                from logic import search_with_no_observation

                steps, time_solved = search_with_no_observation(start_states, goal_states)
                partial_belief_interface(steps, goal_states, time_solved)
            elif btn_backtrack.is_clicked(event):
                algo_selected = "backtracking"
                is_processing = True
                stop_event = threading.Event()
                thread = threading.Thread(target=run_backtracking, args=("backtracking", start_state, thread_manager, result_queue, stop_event))
                thread_manager.add_thread(thread, stop_event)
                thread.start()
            elif btn_backtrack_cons.is_clicked(event):
                algo_selected = "backtracking_constraint_propagation"
                is_processing = True
                stop_event = threading.Event()
                thread = threading.Thread(target=run_backtracking, args=("backtracking_constraint_propagation", start_state, thread_manager, result_queue, stop_event))
                thread_manager.add_thread(thread, stop_event)
                thread.start()
            elif btn_backtrack_heus.is_clicked(event):
                algo_selected = "backtracking_lcv"
                is_processing = True
                stop_event = threading.Event()
                thread = threading.Thread(target=run_backtracking, args=("backtracking_lcv", start_state, thread_manager, result_queue, stop_event))
                thread_manager.add_thread(thread, stop_event)
                thread.start()
            elif btn_back.is_clicked(event):
                thread_manager.cancel_all()
                is_processing = False
                algo_selected = None
            elif btn_analysis.is_clicked(event):
                show_analysis_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)
            slider.handle_event(event)
        if animating:
            if solution_solved:
                animate_solution(solution_solved, slider, time_solved)
            else:
                screen.fill(WHITE)
                draw_puzzle(screen, start_state, offset=CENTER_PUZZLE_OFFSET)
                error_text = font_small.render(f"{algo_selected} can't solve this puzzle!", True, RED)
                screen.blit(error_text, (50, PUZZLE_AREA_HEIGHT + 10))
                pygame.display.flip()
                time.sleep(2)
            animating = False

        screen.fill(WHITE)
        draw_puzzle(screen, start_state, offset=LEFT_PUZZLE_OFFSET)
        left_text = font_small.render("start state", True, BLACK)
        screen.blit(left_text, LEFT_TEXT)
        draw_puzzle(screen, goal_state, offset=RIGHT_PUZZLE_OFFSET)
        right_text = font_small.render("goal state", True, BLACK)
        screen.blit(right_text, RIGHT_TEXT)
        btn_bfs.draw(screen)
        btn_dfs.draw(screen)
        btn_ucs.draw(screen)
        btn_iddfs.draw(screen)
        btn_gbfs.draw(screen)
        btn_Astar.draw(screen)
        btn_ida_star.draw(screen)
        btn_hill_simp.draw(screen)
        btn_hill_step.draw(screen)
        btn_hill_stocha.draw(screen)
        btn_beam.draw(screen)
        btn_sa.draw(screen)
        btn_genetic.draw(screen)
        btn_and_or.draw(screen)
        btn_random.draw(screen)
        btn_belief.draw(screen)
        btn_part_belief.draw(screen)
        btn_backtrack.draw(screen)
        btn_backtrack_cons.draw(screen)
        btn_backtrack_heus.draw(screen)
        btn_ql.draw(screen)
        btn_analysis.draw(screen)
        slider.draw(screen)
        slider_text = font_small.render(f"Delay: {slider.value:.1f}s", True, BLACK)
        screen.blit(slider_text, (320, PUZZLE_AREA_HEIGHT + 300))
        if algo_selected:
            algo_text = font_small.render(f"Algo: {algo_selected}", True, BLACK)
            screen.blit(algo_text, (50, PUZZLE_AREA_HEIGHT - 20))
        if is_processing:
            processing_text = font_small.render("Processing...", True, BLACK)
            screen.blit(processing_text, (WINDOW_WIDTH // 2 - 50, PUZZLE_AREA_HEIGHT // 2))
            btn_back.draw(screen)
            pygame.display.flip()
            if result_queue:
                solution_solved, time_solved = result_queue.pop(0)
                is_processing = False
                backtracking_interface(solution_solved, time_solved)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
