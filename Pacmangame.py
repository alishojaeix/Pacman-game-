import pygame
import sys
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 660
GRID_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 60) // GRID_SIZE  # 60 pixels for score area
GAME_AREA_TOP = 60  # Start game area below score

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Online image URLs (replace with actual URLs or use local files)
PACMAN_IMG_URL = "https://www.clipartmax.com/png/middle/41-415261_pacman-pac-man.png"
GHOST_IMG_URLS = [
    "https://www.clipartmax.com/png/middle/41-415266_blinky-ghost-pacman.png",  # Red
    "https://www.clipartmax.com/png/middle/41-415268_pink-ghost-pacman.png",    # Pink
    "https://www.clipartmax.com/png/middle/41-415267_cyan-ghost-pacman.png",    # Cyan
    "https://www.clipartmax.com/png/middle/41-415265_orange-ghost-pacman.png"   # Orange
]

# Try to load online images, fall back to colored circles
try:
    import requests
    from io import BytesIO
    from PIL import Image
    
    # Load Pac-Man image
    response = requests.get(PACMAN_IMG_URL)
    pacman_img = Image.open(BytesIO(response.content))
    pacman_img = pacman_img.resize((GRID_SIZE, GRID_SIZE))
    pacman_img = pygame.image.fromstring(pacman_img.tobytes(), pacman_img.size, pacman_img.mode)
    
    # Load ghost images
    ghost_imgs = []
    for url in GHOST_IMG_URLS:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((GRID_SIZE, GRID_SIZE))
        img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        ghost_imgs.append(img)
    
    use_images = True
except:
    use_images = False
    print("Failed to load online images. Using simple shapes instead.")

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pac-Man')
clock = pygame.time.Clock()

# Game variables
score = 0
lives = 3
game_over = False
paused = False

# Maze layout (1 = wall, 0 = path, 2 = dot, 3 = power pellet)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
    [1, 3, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1],
    [0, 0, 0, 1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 2, 1, 1, 0, 0, 1, 1, 2, 1, 2, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1],
    [0, 0, 0, 1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
    [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1],
    [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1],
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

class PacMan:
    def __init__(self):
        self.x = 9
        self.y = 15
        self.direction = STOP
        self.next_direction = STOP
        self.speed = 2
        self.radius = GRID_SIZE // 2 - 2
        self.mouth_angle = 0
        self.mouth_direction = 1
        self.mouth_speed = 0.2
        
    def update(self):
        # Mouth animation
        self.mouth_angle += self.mouth_direction * self.mouth_speed
        if self.mouth_angle > 0.4 or self.mouth_angle < 0:
            self.mouth_direction *= -1
            self.mouth_angle = max(0, min(0.4, self.mouth_angle))
        
        # Try to change direction if there's a next direction queued
        if self.next_direction != STOP and self.next_direction != self.direction:
            new_x = self.x + self.next_direction[0]
            new_y = self.y + self.next_direction[1]
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and maze[new_y][new_x] != 1:
                self.direction = self.next_direction
                self.next_direction = STOP
        
        # Move
        if self.direction != STOP:
            new_x = self.x + self.direction[0] * self.speed / 10
            new_y = self.y + self.direction[1] * self.speed / 10
            
            # Check if we've entered a new grid cell
            if abs(new_x - round(new_x)) < 0.1 and abs(new_y - round(new_y)) < 0.1:
                new_x = round(new_x)
                new_y = round(new_y)
                
                # Check for walls
                if (new_x < 0 or new_x >= GRID_WIDTH or 
                    new_y < 0 or new_y >= GRID_HEIGHT or 
                    maze[new_y][new_x] == 1):
                    self.direction = STOP
                    new_x = self.x
                    new_y = self.y
                else:
                    # Eat dots
                    if maze[new_y][new_x] == 2:
                        maze[new_y][new_x] = 0
                        global score
                        score += 10
                    elif maze[new_y][new_x] == 3:
                        maze[new_y][new_x] = 0
                        score += 50
                        for ghost in ghosts:
                            ghost.frightened = True
                            ghost.frightened_timer = 500  # 10 seconds at 50 FPS
            
            self.x = new_x
            self.y = new_y
            
            # Wrap around tunnel
            if self.x < 0:
                self.x = GRID_WIDTH - 1
            elif self.x >= GRID_WIDTH:
                self.x = 0
    
    def draw(self):
        x = int(self.x * GRID_SIZE + GRID_SIZE // 2)
        y = int(self.y * GRID_SIZE + GRID_SIZE // 2 + GAME_AREA_TOP)
        
        if use_images:
            # Rotate image based on direction
            angle = 0
            if self.direction == UP:
                angle = 90
            elif self.direction == LEFT:
                angle = 180
            elif self.direction == DOWN:
                angle = 270
                
            rotated_img = pygame.transform.rotate(pacman_img, angle)
            img_rect = rotated_img.get_rect(center=(x, y))
            screen.blit(rotated_img, img_rect)
        else:
            # Draw Pac-Man as a yellow circle with mouth
            pygame.draw.circle(screen, YELLOW, (x, y), self.radius)
            
            # Calculate mouth points
            if self.direction == RIGHT:
                start_angle = self.mouth_angle
                end_angle = -self.mouth_angle
            elif self.direction == LEFT:
                start_angle = math.pi + self.mouth_angle
                end_angle = math.pi - self.mouth_angle
            elif self.direction == UP:
                start_angle = math.pi/2 + self.mouth_angle
                end_angle = math.pi/2 - self.mouth_angle
            elif self.direction == DOWN:
                start_angle = 3*math.pi/2 + self.mouth_angle
                end_angle = 3*math.pi/2 - self.mouth_angle
            else:  # STOP
                start_angle = 0.1
                end_angle = -0.1
            
            # Draw mouth
            pygame.draw.arc(screen, BLACK, (x - self.radius, y - self.radius, 
                                          self.radius * 2, self.radius * 2), 
                          start_angle, end_angle, 2)
            pygame.draw.line(screen, BLACK, (x, y), 
                           (x + self.radius * math.cos(start_angle), 
                            y + self.radius * math.sin(start_angle)), 2)
            pygame.draw.line(screen, BLACK, (x, y), 
                           (x + self.radius * math.cos(end_angle), 
                            y + self.radius * math.sin(end_angle)), 2)

class Ghost:
    def __init__(self, x, y, color_index):
        self.x = x
        self.y = y
        self.color_index = color_index
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.speed = 1
        self.radius = GRID_SIZE // 2 - 2
        self.frightened = False
        self.frightened_timer = 0
        self.target = (0, 0)
        
    def update(self, pacman):
        if self.frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.frightened = False
        
        # Simple AI: move randomly but prefer directions toward Pac-Man
        if random.random() < 0.1 or (self.x == round(self.x) and self.y == round(self.y)):
            possible_directions = []
            for direction in [UP, DOWN, LEFT, RIGHT]:
                new_x = round(self.x) + direction[0]
                new_y = round(self.y) + direction[1]
                if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and 
                    maze[new_y][new_x] != 1 and direction != (-self.direction[0], -self.direction[1])):
                    possible_directions.append(direction)
            
            if possible_directions:
                if self.frightened:
                    # Run away from Pac-Man
                    distances = []
                    for direction in possible_directions:
                        new_x = round(self.x) + direction[0]
                        new_y = round(self.y) + direction[1]
                        dist = (new_x - pacman.x)**2 + (new_y - pacman.y)**2
                        distances.append(dist)
                    self.direction = possible_directions[distances.index(max(distances))]
                else:
                    # Chase Pac-Man
                    distances = []
                    for direction in possible_directions:
                        new_x = round(self.x) + direction[0]
                        new_y = round(self.y) + direction[1]
                        dist = (new_x - pacman.x)**2 + (new_y - pacman.y)**2
                        distances.append(dist)
                    self.direction = possible_directions[distances.index(min(distances))]
        
        # Move
        new_x = self.x + self.direction[0] * self.speed / 10
        new_y = self.y + self.direction[1] * self.speed / 10
        
        # Check if we've entered a new grid cell
        if abs(new_x - round(new_x)) < 0.1 and abs(new_y - round(new_y)) < 0.1:
            new_x = round(new_x)
            new_y = round(new_y)
            
            # Check for walls
            if (new_x < 0 or new_x >= GRID_WIDTH or 
                new_y < 0 or new_y >= GRID_HEIGHT or 
                maze[new_y][new_x] == 1):
                # Find a new direction
                possible_directions = []
                for direction in [UP, DOWN, LEFT, RIGHT]:
                    test_x = new_x + direction[0]
                    test_y = new_y + direction[1]
                    if (0 <= test_x < GRID_WIDTH and 0 <= test_y < GRID_HEIGHT and 
                        maze[test_y][test_x] != 1 and direction != (-self.direction[0], -self.direction[1])):
                        possible_directions.append(direction)
                
                if possible_directions:
                    self.direction = random.choice(possible_directions)
                else:
                    self.direction = (-self.direction[0], -self.direction[1])
                
                new_x = self.x
                new_y = self.y
        
        self.x = new_x
        self.y = new_y
        
        # Wrap around tunnel
        if self.x < 0:
            self.x = GRID_WIDTH - 1
        elif self.x >= GRID_WIDTH:
            self.x = 0
    
    def draw(self):
        x = int(self.x * GRID_SIZE + GRID_SIZE // 2)
        y = int(self.y * GRID_SIZE + GRID_SIZE // 2 + GAME_AREA_TOP)
        
        if use_images:
            if self.frightened:
                # Draw blue ghost
                pygame.draw.circle(screen, BLUE, (x, y - 5), self.radius)
                pygame.draw.rect(screen, BLUE, (x - self.radius, y - 5, self.radius * 2, self.radius))
                pygame.draw.rect(screen, BLUE, (x - self.radius, y + self.radius - 5, self.radius * 2, 5))
                
                # Draw eyes
                pygame.draw.circle(screen, WHITE, (x - 8, y - 8), 5)
                pygame.draw.circle(screen, WHITE, (x + 8, y - 8), 5)
                pygame.draw.circle(screen, BLACK, (x - 8, y - 8), 2)
                pygame.draw.circle(screen, BLACK, (x + 8, y - 8), 2)
            else:
                # Use ghost image
                screen.blit(ghost_imgs[self.color_index], (x - self.radius, y - self.radius))
        else:
            # Draw ghost body
            if self.frightened:
                color = BLUE
            else:
                colors = [RED, PINK, CYAN, ORANGE]
                color = colors[self.color_index]
            
            pygame.draw.circle(screen, color, (x, y - 5), self.radius)
            pygame.draw.rect(screen, color, (x - self.radius, y - 5, self.radius * 2, self.radius))
            
            # Draw bottom wavy part
            points = []
            for i in range(5):
                points.append((x - self.radius + i * self.radius // 2, y + self.radius - 5 + (5 if i % 2 else 0)))
            points.append((x + self.radius, y + self.radius - 5))
            points.append((x + self.radius, y - 5 + self.radius // 2))
            pygame.draw.polygon(screen, color, points)
            
            # Draw eyes
            pygame.draw.circle(screen, WHITE, (x - 8, y - 8), 5)
            pygame.draw.circle(screen, WHITE, (x + 8, y - 8), 5)
            pygame.draw.circle(screen, BLACK, (x - 8, y - 8), 2)
            pygame.draw.circle(screen, BLACK, (x + 8, y - 8), 2)

def draw_maze():
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] == 1:  # Wall
                pygame.draw.rect(screen, BLUE, 
                                (x * GRID_SIZE, y * GRID_SIZE + GAME_AREA_TOP, GRID_SIZE, GRID_SIZE))
                # Add some details to walls
                pygame.draw.rect(screen, BLUE, 
                                (x * GRID_SIZE + 2, y * GRID_SIZE + 2 + GAME_AREA_TOP, 
                                 GRID_SIZE - 4, GRID_SIZE - 4))
            elif maze[y][x] == 2:  # Dot
                pygame.draw.circle(screen, WHITE, 
                                 (x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2 + GAME_AREA_TOP), 
                                 3)
            elif maze[y][x] == 3:  # Power pellet
                pygame.draw.circle(screen, WHITE, 
                                 (x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2 + GAME_AREA_TOP), 
                                 8)

def draw_score():
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (SCREEN_WIDTH - 120, 20))

def check_collisions(pacman, ghosts):
    global lives, game_over
    
    for ghost in ghosts:
        # Simple distance-based collision detection
        if ((pacman.x - ghost.x)**2 + (pacman.y - ghost.y)**2) < 0.5:
            if ghost.frightened:
                # Eat ghost
                ghost.x = 9
                ghost.y = 9
                ghost.frightened = False
                global score
                score += 200
            else:
                # Lose life
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    # Reset positions
                    pacman.x = 9
                    pacman.y = 15
                    pacman.direction = STOP
                    pacman.next_direction = STOP
                    for g in ghosts:
                        g.x = 9 + ghosts.index(g)
                        g.y = 9
                        g.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                return

# Create game objects
pacman = PacMan()
ghosts = [
    Ghost(9, 9, 0),  # Red
    Ghost(10, 9, 1),  # Pink
    Ghost(11, 9, 2),  # Cyan
    Ghost(12, 9, 3)   # Orange
]

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                pacman.next_direction = UP
            elif event.key == K_DOWN:
                pacman.next_direction = DOWN
            elif event.key == K_LEFT:
                pacman.next_direction = LEFT
            elif event.key == K_RIGHT:
                pacman.next_direction = RIGHT
            elif event.key == K_p:
                paused = not paused
            elif event.key == K_r and game_over:
                # Reset game
                score = 0
                lives = 3
                game_over = False
                pacman = PacMan()
                ghosts = [
                    Ghost(9, 9, 0),
                    Ghost(10, 9, 1),
                    Ghost(11, 9, 2),
                    Ghost(12, 9, 3)
                ]
                # Reset maze
                for y in range(len(maze)):
                    for x in range(len(maze[y])):
                        if maze[y][x] == 0:
                            maze[y][x] = 2
    
    if not paused and not game_over:
        # Update game objects
        pacman.update()
        for ghost in ghosts:
            ghost.update(pacman)
        
        # Check for collisions
        check_collisions(pacman, ghosts)
    
    # Draw everything
    screen.fill(BLACK)
    draw_maze()
    for ghost in ghosts:
        ghost.draw()
    pacman.draw()
    draw_score()
    
    if game_over:
        font = pygame.font.SysFont(None, 72)
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press R to restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 50))
    
    if paused:
        font = pygame.font.SysFont(None, 72)
        pause_text = font.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
    
    pygame.display.flip()
    clock.tick(50)  # 50 FPS

pygame.quit()
sys.exit()
