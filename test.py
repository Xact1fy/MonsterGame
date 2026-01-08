import pygame
import random

# --- 1. Initial Setup ---
pygame.init()
WIDTH, HEIGHT = 1920, 1080 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Impact", 48)

# Darkness Surface
fog = pygame.Surface((WIDTH, HEIGHT))

# --- 2. Classes ---

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((30, 30, 40))
        self.rect = self.image.get_rect(topleft=(x, y))

class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill((255, 215, 0)) # Gold
        self.rect = self.image.get_rect(center=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((200, 200, 200))
        self.rect = self.image.get_rect()
        self.speed = 8
        self.keys_collected = 0

    def update(self, walls):
        keys = pygame.key.get_pressed()
        old_x, old_y = self.rect.x, self.rect.y
        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed
        if pygame.sprite.spritecollide(self, walls, False): self.rect.x = old_x
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed
        if pygame.sprite.spritecollide(self, walls, False): self.rect.y = old_y

class Stalker(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 0, 0), (35, 35), 30)
        pygame.draw.circle(self.image, (255, 0, 0), (25, 25), 5) 
        pygame.draw.circle(self.image, (255, 0, 0), (45, 25), 5) 
        self.rect = self.image.get_rect()
        self.player = player
        self.speed = 3

    def update(self, walls):
        old_x, old_y = self.rect.x, self.rect.y
        if self.rect.x < self.player.rect.x: self.rect.x += self.speed
        if self.rect.x > self.player.rect.x: self.rect.x -= self.speed
        if pygame.sprite.spritecollide(self, walls, False): self.rect.x = old_x
        if self.rect.y < self.player.rect.y: self.rect.y += self.speed
        if self.rect.y > self.player.rect.y: self.rect.y -= self.speed
        if pygame.sprite.spritecollide(self, walls, False): self.rect.y = old_y

# --- 3. Level Management ---

def setup_level(level_num, player, stalker):
    """Resets sprites and creates a new layout."""
    all_sprites = pygame.sprite.Group()
    wall_group = pygame.sprite.Group()
    key_group = pygame.sprite.Group()
    
    # Reset Player
    player.rect.center = (100, HEIGHT // 2)
    player.keys_collected = 0
    all_sprites.add(player)
    
    # Increase Stalker difficulty
    stalker.speed = 3 + level_num 
    stalker.rect.center = (WIDTH - 100, HEIGHT // 2)
    all_sprites.add(stalker)
    
    # Create the Exit Door (far right)
    door = Wall(WIDTH - 60, HEIGHT // 2 - 100, 60, 200)
    door.image.fill((100, 50, 0)) # Brown
    all_sprites.add(door)
    wall_group.add(door)
    
    # Spawn 3 Keys in random spots (avoiding walls)
    for _ in range(3):
        k = Key(random.randint(200, WIDTH-300), random.randint(100, HEIGHT-100))
        key_group.add(k)
        all_sprites.add(k)

    # Simple Procedural Walls (Horizontal or Vertical blocks)
    for _ in range(5 + level_num):
        w_width, w_height = random.choice([(50, 300), (300, 50)])
        w = Wall(random.randint(300, WIDTH-400), random.randint(0, HEIGHT-300), w_width, w_height)
        wall_group.add(w)
        all_sprites.add(w)

    return all_sprites, wall_group, key_group, door

# --- 4. Main Game Loop ---

current_level = 1
player = Player()
stalker = Stalker(player)
all_sprites, wall_group, key_group, door = setup_level(current_level, player, stalker)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # Logic
    all_sprites.update(wall_group)
    
    # 1. Collect Keys
    keys_hit = pygame.sprite.spritecollide(player, key_group, True)
    for k in keys_hit:
        player.keys_collected += 1
        if player.keys_collected >= 3:
            wall_group.remove(door)
            door.image.fill((0, 255, 0)) # Green means open!

    # 2. Level Transition
    if player.rect.x > WIDTH - 50 and player.keys_collected >= 3:
        current_level += 1
        all_sprites, wall_group, key_group, door = setup_level(current_level, player, stalker)

    # 3. Death Logic
    if player.rect.colliderect(stalker.rect):
        current_level = 1 # Back to start
        all_sprites, wall_group, key_group, door = setup_level(current_level, player, stalker)

    # Drawing
    screen.fill((5, 5, 10))
    all_sprites.draw(screen)
    
    # Darkness effect
    fog.fill((0, 0, 15))
    pygame.draw.circle(fog, (255, 255, 255), player.rect.center, 300)
    screen.blit(fog, (0, 0), special_flags=pygame.BLEND_MULT)

    # UI
    info = font.render(f"LEVEL {current_level}  |  KEYS: {player.keys_collected}/3", True, (255, 255, 255))
    screen.blit(info, (50, 50))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
