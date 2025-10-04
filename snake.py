import pygame
import random
import sys
import asyncio

# Initialize pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
CELL_NUMBER_X = WINDOW_WIDTH // CELL_SIZE
CELL_NUMBER_Y = WINDOW_HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 155, 0)

class Snake:
    def __init__(self):
        self.body = [pygame.Vector2(5, 10), pygame.Vector2(4, 10), pygame.Vector2(3, 10)]
        self.direction = pygame.Vector2(1, 0)
        self.new_block = False
        
    def draw_snake(self, screen):
        for block in self.body:
            x_pos = int(block.x * CELL_SIZE)
            y_pos = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x_pos, y_pos, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, DARK_GREEN, block_rect)
            
    def move_snake(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            
    def add_block(self):
        self.new_block = True
        
    def check_collision(self):
        if not 0 <= self.body[0].x < CELL_NUMBER_X or not 0 <= self.body[0].y < CELL_NUMBER_Y:
            return True
            
        for block in self.body[1:]:
            if block == self.body[0]:
                return True
                
        return False

class Food:
    def __init__(self):
        self.randomize()
        
    def draw_food(self, screen):
        food_rect = pygame.Rect(int(self.pos.x * CELL_SIZE), int(self.pos.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, food_rect)
        
    def randomize(self):
        self.x = random.randint(0, CELL_NUMBER_X - 1)
        self.y = random.randint(0, CELL_NUMBER_Y - 1)
        self.pos = pygame.Vector2(self.x, self.y)

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.last_update = 0
        
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > 150:  # 150ms delay
            self.snake.move_snake()
            self.check_collision()
            self.check_fail()
            self.last_update = current_time
        
    def draw_elements(self, screen):
        self.draw_grass(screen)
        self.food.draw_food(screen)
        self.snake.draw_snake(screen)
        self.draw_score(screen)
        
    def check_collision(self):
        if self.food.pos == self.snake.body[0]:
            self.food.randomize()
            self.snake.add_block()
            self.score += 1
            
        for block in self.snake.body[1:]:
            if block == self.food.pos:
                self.food.randomize()
                
    def check_fail(self):
        if self.snake.check_collision():
            self.game_over()
            
    def game_over(self):
        self.snake = Snake()
        self.score = 0
        
    def draw_grass(self, screen):
        grass_color = (167, 209, 61)
        for row in range(CELL_NUMBER_Y):
            if row % 2 == 0:
                for col in range(0, CELL_NUMBER_X, 2):
                    grass_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, grass_color, grass_rect)
            else:
                for col in range(1, CELL_NUMBER_X, 2):
                    grass_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, grass_color, grass_rect)
                    
    def draw_score(self, screen):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, 10)
        screen.blit(score_text, score_rect)

# Global variables for web compatibility
screen = None
clock = None
game = None
running = True

async def main():
    global screen, clock, game, running
    
    # Initialize pygame and screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Snake Game')
    clock = pygame.time.Clock()
    
    game = Game()
    
    # Main game loop - this runs continuously for web
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if game.snake.direction.y != 1:
                        game.snake.direction = pygame.Vector2(0, -1)
                if event.key == pygame.K_DOWN:
                    if game.snake.direction.y != -1:
                        game.snake.direction = pygame.Vector2(0, 1)
                if event.key == pygame.K_RIGHT:
                    if game.snake.direction.x != -1:
                        game.snake.direction = pygame.Vector2(1, 0)
                if event.key == pygame.K_LEFT:
                    if game.snake.direction.x != 1:
                        game.snake.direction = pygame.Vector2(-1, 0)
        
        # Update game state
        game.update()
        
        # Draw everything
        screen.fill((175, 215, 70))
        game.draw_elements(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
        
        # CRITICAL: This allows the browser to process other tasks
        await asyncio.sleep(0)
        
    # quit
    pygame.quit()

# For web deployment, just call main() without asyncio.run()
if __name__ == "__main__":
    # For desktop: asyncio.run(main())
    # For web: just call main() - the web framework handles async
    import sys
    if "pygbag" in sys.modules or "pyodide" in sys.modules:
        # Running in web environment
        asyncio.create_task(main())
    else:
        # Running on desktop
        asyncio.run(main())
