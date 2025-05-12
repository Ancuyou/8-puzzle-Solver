import matplotlib.pyplot as plt
import pandas as pd
import pygame
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Initialize Pygame
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 700
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Analysis Plots")
clock = pygame.time.Clock()
font_small = pygame.font.Font(None, 24)


def draw_analysis_plots():
    # Read CSV
    try:
        df = pd.read_csv("results.csv", names=["algo", "time", "steps", "explored", "solved"])
        print("CSV loaded successfully. Shape:", df.shape)
        print("Algorithms found:", df["algo"].unique())
    except FileNotFoundError:
        print("Error: results.csv not found")
        screen.fill((255, 255, 255))
        error_text = font_small.render("Error: results.csv not found", True, (255, 0, 0))
        screen.blit(error_text, (20, 20))
        pygame.display.flip()
        pygame.time.wait(2000)
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        screen.fill((255, 255, 255))
        error_text = font_small.render(f"Error reading CSV: {e}", True, (255, 0, 0))
        screen.blit(error_text, (20, 20))
        pygame.display.flip()
        pygame.time.wait(2000)
        return

    # Group data and calculate statistics
    grouped = df.groupby("algo")
    algos = sorted(grouped.groups.keys())
    print("Grouped algorithms:", algos)

    avg_time = grouped["time"].mean()
    avg_steps = grouped["steps"].mean()
    avg_explored = grouped["explored"].mean()
    success_rate = grouped["solved"].mean() * 100

    stats = {"Time (ms)": avg_time, "Steps": avg_steps, "Explored": avg_explored, "Success (%)": success_rate}

    # Print statistics for debugging
    for title, series in stats.items():
        print(f"{title} values:", series.to_dict())

    # Create plots
    surfaces = []
    for title, series in stats.items():
        try:
            fig = plt.figure(figsize=(3.5, 3))
            ax = fig.add_subplot(111)
            ax.bar(algos, series[algos])
            ax.set_title(title)
            ax.set_ylabel(title)
            ax.tick_params(axis="x", rotation=45)
            fig.tight_layout()

            canvas = FigureCanvasAgg(fig)
            canvas.draw()
            raw = canvas.tostring_rgb()
            w, h = canvas.get_width_height()
            surf = pygame.image.fromstring(raw, (w, h), "RGB")
            surfaces.append(surf)
            print(f"Plot created for {title}: {w}x{h} pixels")
            plt.close(fig)
        except Exception as e:
            print(f"Error creating plot for {title}: {e}")
            surfaces.append(None)

    # Display loop
    positions = [(20, 20), (420, 20), (20, 360), (420, 360)]  # 2x2 grid
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill((255, 255, 255))
        for i, (surf, pos) in enumerate(zip(surfaces, positions)):
            if surf:
                screen.blit(surf, pos)
            else:
                error_text = font_small.render(f"Plot {i+1} failed", True, (255, 0, 0))
                screen.blit(error_text, pos)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    draw_analysis_plots()
    pygame.quit()
