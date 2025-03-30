import random
import time

import pygame

from Logic import solution_time

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 600
PUZZLE_AREA_HEIGHT = 300

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
GRAY = (200, 200, 200)
DARKGRAY = (100, 100, 100)
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

LEFT_PUZZLE_OFFSET = (50, 20)
LEFT_TEXT = (100, 200)
RIGHT_PUZZLE_OFFSET = (270, 20)
RIGHT_TEXT = (320, 200)
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
        screen.blit(slider_text, (320, PUZZLE_AREA_HEIGHT + 250))
        btn_left.draw(screen)
        btn_right.draw(screen)
        gap = 3
        for idx in range(visible_count):
            step_idx = scroll_index + idx
            if step_idx >= len(solution):
                break
            thumb_x = 20 + idx * (THUMB_PUZZLE_WIDTH + gap)
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


def main():
    global start_state
    start_state = [[2, 6, 5], [8, 7, 0], [4, 3, 1]]
    goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    algo_selected = None
    time_solved = 0
    btn_bfs = Button((50, PUZZLE_AREA_HEIGHT + 20, 100, 40), "BFS")
    btn_dfs = Button((200, PUZZLE_AREA_HEIGHT + 20, 100, 40), "DFS")
    btn_ucs = Button((350, PUZZLE_AREA_HEIGHT + 20, 100, 40), "UCS")
    btn_iddfs = Button((50, PUZZLE_AREA_HEIGHT + 70, 100, 40), "IDDFS")
    btn_gbfs = Button((200, PUZZLE_AREA_HEIGHT + 70, 100, 40), "GBFS")
    btn_Astar = Button((350, PUZZLE_AREA_HEIGHT + 70, 100, 40), "A*")
    btn_ida_star = Button((50, PUZZLE_AREA_HEIGHT + 120, 100, 40), "IDA*")
    btn_hill_simp = Button((200, PUZZLE_AREA_HEIGHT + 120, 100, 40), "H_SIMP")
    btn_hill_step = Button((350, PUZZLE_AREA_HEIGHT + 120, 100, 40), "H_STEEP")
    btn_hill_stocha = Button((50, PUZZLE_AREA_HEIGHT + 170, 100, 40), "H_STOR")
    btn_random = Button((200, 250, 100, 40), "Random")
    slider = Slider((50, PUZZLE_AREA_HEIGHT + 250, 250, 20), 0.01, 2.0, 1.0)
    running = True
    animating = False
    solution_solved = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
        btn_random.draw(screen)
        slider.draw(screen)
        slider_text = font_small.render(f"Delay: {slider.value:.1f}s", True, BLACK)
        screen.blit(slider_text, (320, PUZZLE_AREA_HEIGHT + 250))
        if algo_selected:
            algo_text = font_small.render(f"Algo: {algo_selected}", True, BLACK)
            screen.blit(algo_text, (50, PUZZLE_AREA_HEIGHT))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
