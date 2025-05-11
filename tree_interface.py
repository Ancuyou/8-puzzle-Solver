from heapq import heappop, heappush, nsmallest
from uuid import uuid4

import pygame

# Assuming these are defined in your main file
from logic import generate_children, hst, is_goal, manhattan_distance, re_path
from visualization import BLACK, BLUE, GRAY, WHITE, Button, Slider, clock, draw_puzzle, font_small

WINDOW_HEIGHT = 1000
WINDOW_WIDTH = 1300


def beam_search_with_tree(start_state, k=2):
    # Modified beam search to collect tree structure, allowing revisits
    beam = [(manhattan_distance(start_state), start_state, [start_state], str(uuid4()))]  # (heuristic, state, path, node_id)
    nodes = [(hst(start_state), start_state, 0, True, beam[0][3])]  # (state_hst, state, depth, is_selected, node_id)
    edges = []  # (parent_id, child_id)
    limit = 50
    count = 0

    while beam and limit > 0:
        limit -= 1
        count += 1
        new_beam = []
        visited_per_iteration = set()  # To avoid duplicates within the same iteration

        print(f"Step {count}:\n")  # Print step number

        for _ in range(len(beam)):
            _, current, current_path, current_id = heappop(beam)
            if is_goal(current):
                return current_path, nodes, edges

            for child in generate_children(current):
                child_hst = hst(child)

                if child_hst not in visited_per_iteration:  # Ensure no duplicates in the same iteration
                    visited_per_iteration.add(child_hst)
                    child_id = str(uuid4())
                    new_path = current_path + [child]
                    heappush(new_beam, (manhattan_distance(child), child, new_path, child_id))
                    nodes.append((child_hst, child, count, False, child_id))
                    edges.append((current_id, child_id))

                    # Print the generated state
                    print(f"Generated state at depth {count}: {child}")

        # Prepare for the next beam
        beam = nsmallest(k, new_beam, key=lambda x: x[0])

        # Mark selected nodes
        selected_states = set(hst(state) for _, state, _, _ in beam)
        for node in nodes:
            if node[0] in selected_states and node[2] == count:
                node_list = list(node)
                node_list[3] = True
                nodes[nodes.index(node)] = tuple(node_list)

    return None, nodes, edges


# Constants for tree visualization
TILE_SIZE = 35  # Smaller tile size for compact puzzles
PUZZLE_WIDTH = TILE_SIZE * 3
PUZZLE_HEIGHT = TILE_SIZE * 3
HORIZONTAL_SPACING = 60
VERTICAL_SPACING = 60
NODE_WIDTH = PUZZLE_WIDTH + HORIZONTAL_SPACING
NODE_HEIGHT = PUZZLE_HEIGHT + VERTICAL_SPACING + 20  # Extra space for heuristic text
GRAY_COLOR = GRAY
SCROLLBAR_WIDTH = 20
SCROLLBAR_COLOR = (150, 150, 150)
SCROLLBAR_HANDLE_COLOR = (200, 0, 0)


def beam_search_tree_interface(algo_name, start_state):
    # Run beam search to get tree data
    solution, nodes, edges = beam_search_with_tree(start_state, k=2)

    # Pygame setup
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Beam Search Tree Visualization")

    # Organize nodes by depth
    depth_nodes = {}
    for node in nodes:
        depth = node[2]
        if depth not in depth_nodes:
            depth_nodes[depth] = []
        depth_nodes[depth].append(node)

    # Calculate total width and height for scrolling
    max_depth = max(depth_nodes.keys()) if depth_nodes else 0
    max_nodes_in_depth = max(len(nodes) for nodes in depth_nodes.values()) if depth_nodes else 1
    total_width = max_nodes_in_depth * NODE_WIDTH

    # Calculate height considering "Chosen states" section
    total_height = 0
    for depth in range(max_depth + 1):
        if depth in depth_nodes:
            nodes_at_depth = depth_nodes[depth]
            total_height += len(nodes_at_depth) * NODE_HEIGHT  # Height for generated states
            # Find selected states at this depth
            selected_at_depth = [node for node in nodes_at_depth if node[3]]
            if selected_at_depth:
                total_height += 50  # Space for "Chosen states" text
                total_height += len(selected_at_depth) * NODE_HEIGHT  # Space for selected states

    # Camera for scrolling
    camera_x, camera_y = 0, 0
    scroll_speed = 10
    dragging_scrollbar = False

    # Buttons and slider
    btn_back = Button((WINDOW_WIDTH - 120, 20, 100, 40), "Back")
    slider = Slider((50, WINDOW_HEIGHT - 50, 250, 20), 0.01, 2.0, 1.0)

    # Scrollbar setup
    visible_height = WINDOW_HEIGHT
    if total_height > visible_height:
        scrollbar_height = (visible_height / total_height) * visible_height
        scrollbar_y = (abs(camera_y) / total_height) * visible_height
    else:
        scrollbar_height = visible_height
        scrollbar_y = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if btn_back.is_clicked(event):
                running = False
            slider.handle_event(event)
            # Handle scrolling with arrow keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    camera_x = min(camera_x + scroll_speed, 0)
                if event.key == pygame.K_RIGHT:
                    camera_x = max(camera_x - scroll_speed, -total_width + WINDOW_WIDTH)
                if event.key == pygame.K_UP:
                    camera_y = min(camera_y + scroll_speed, 0)
                if event.key == pygame.K_DOWN:
                    camera_y = max(camera_y - scroll_speed, -total_height + WINDOW_HEIGHT)
            # Handle scrollbar interaction
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                scrollbar_rect = pygame.Rect(WINDOW_WIDTH - SCROLLBAR_WIDTH, scrollbar_y, SCROLLBAR_WIDTH, scrollbar_height)
                if scrollbar_rect.collidepoint(mouse_x, mouse_y):
                    dragging_scrollbar = True
            if event.type == pygame.MOUSEBUTTONUP:
                dragging_scrollbar = False
            if event.type == pygame.MOUSEMOTION and dragging_scrollbar:
                _, mouse_y = event.pos
                scrollbar_y = max(0, min(mouse_y, WINDOW_HEIGHT - scrollbar_height))
                camera_y = -(scrollbar_y / visible_height) * total_height

        screen.fill(WHITE)

        # Draw nodes and "Chosen states" vertically
        current_y = camera_y
        for depth in sorted(depth_nodes.keys()):
            nodes_at_depth = depth_nodes[depth]
            # Center nodes horizontally
            total_nodes_width = len(nodes_at_depth) * NODE_WIDTH
            start_x = (WINDOW_WIDTH - total_nodes_width) / 2 if total_nodes_width < WINDOW_WIDTH else 0
            # Draw generated states at this depth
            for idx, node in enumerate(nodes_at_depth):
                state_hst, state, node_depth, is_selected, node_id = node
                x = start_x + idx * NODE_WIDTH + camera_x
                y = current_y
                # Draw puzzle (gray if not selected)
                if not is_selected:
                    for i in range(3):
                        for j in range(3):
                            if state[i][j] != 0:
                                rect = pygame.Rect(x + j * TILE_SIZE, y + i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                                pygame.draw.rect(screen, GRAY_COLOR, rect)
                    draw_puzzle(screen, state, offset=(x, y), tile_size=TILE_SIZE)
                else:
                    draw_puzzle(screen, state, offset=(x, y), tile_size=TILE_SIZE)
                # Draw heuristic value below puzzle
                heuristic = manhattan_distance(state)
                heuristic_text = font_small.render(f"h={heuristic}", True, BLACK)
                text_rect = heuristic_text.get_rect(center=(x + PUZZLE_WIDTH / 2, y + PUZZLE_HEIGHT + 20))
                screen.blit(heuristic_text, text_rect)
            current_y += max(50, len(nodes_at_depth) * NODE_HEIGHT // 2)

            # Draw "Chosen states" section
            selected_at_depth = [node for node in nodes_at_depth if node[3]]
            if selected_at_depth:
                # Draw "Chosen states" text
                chosen_text = font_small.render("Chosen states", True, BLACK)
                chosen_text_rect = chosen_text.get_rect(center=(WINDOW_WIDTH / 2, current_y + 25))
                screen.blit(chosen_text, chosen_text_rect)
                current_y += 50  # Space for the text

                # Draw selected states
                total_selected_width = len(selected_at_depth) * NODE_WIDTH
                selected_start_x = (WINDOW_WIDTH - total_selected_width) / 2 if total_selected_width < WINDOW_WIDTH else 0
                for idx, node in enumerate(selected_at_depth):
                    state_hst, state, node_depth, is_selected, node_id = node
                    x = selected_start_x + idx * NODE_WIDTH + camera_x
                    y = current_y
                    # Draw puzzle
                    draw_puzzle(screen, state, offset=(x, y), tile_size=TILE_SIZE)
                    # Draw heuristic value below puzzle
                    heuristic = manhattan_distance(state)
                    heuristic_text = font_small.render(f"h={heuristic}", True, BLACK)
                    text_rect = heuristic_text.get_rect(center=(x + PUZZLE_WIDTH / 2, y + PUZZLE_HEIGHT + 20))
                    screen.blit(heuristic_text, text_rect)
                current_y += 200

        # Draw scrollbar
        if total_height > visible_height:
            scrollbar_rect = pygame.Rect(WINDOW_WIDTH - SCROLLBAR_WIDTH, 0, SCROLLBAR_WIDTH, WINDOW_HEIGHT)
            pygame.draw.rect(screen, SCROLLBAR_COLOR, scrollbar_rect)
            scrollbar_handle_rect = pygame.Rect(WINDOW_WIDTH - SCROLLBAR_WIDTH, scrollbar_y, SCROLLBAR_WIDTH, scrollbar_height)
            pygame.draw.rect(screen, SCROLLBAR_HANDLE_COLOR, scrollbar_handle_rect)

        # Draw UI elements
        btn_back.draw(screen)
        slider.draw(screen)
        slider_text = font_small.render(f"Delay: {slider.value:.1f}s", True, BLACK)
        screen.blit(slider_text, (320, WINDOW_HEIGHT - 50))

        pygame.display.flip()
        clock.tick(60)

    return solution


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Beam Search Tree Test")

    start_state = [[1, 2, 3], [5, 0, 6], [4, 7, 8]]  # Example start state
    btn_run = Button((WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2, 100, 40), "Run Beam")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if btn_run.is_clicked(event):
                beam_search_tree_interface("Beam Search", start_state)

        screen.fill(WHITE)
        draw_puzzle(screen, start_state, offset=(WINDOW_WIDTH // 2 - PUZZLE_WIDTH // 2, 100))
        start_text = font_small.render("Start State", True, BLACK)
        screen.blit(start_text, (WINDOW_WIDTH // 2 - 50, 280))
        btn_run.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
