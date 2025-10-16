import pygame
import os
import wave
import struct
import math
from .paddle import Paddle
from .ball import Ball

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Asset directory setup
ASSETS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))

def ensure_assets_dir():
    os.makedirs(ASSETS_DIR, exist_ok=True)

def generate_test_sound(path, freq=440.0, duration=0.12):
    """Generate a small beep .wav for quick testing (mono 16-bit)."""
    framerate = 44100
    n_samples = int(duration * framerate)
    amplitude = 16000
    with wave.open(path, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        for i in range(n_samples):
            value = int(amplitude * math.sin(2 * math.pi * freq * i / framerate))
            w.writeframes(struct.pack('<h', value))

class GameEngine:
    def __init__(self, width, height):
        # Initialize pygame mixer & main modules
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        # Game Entities
        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 10, 10, width, height)

        # Scores and settings
        self.player_score = 0
        self.ai_score = 0
        self.max_score = 5  # default winning score
        self.font = pygame.font.SysFont("Arial", 30)

        # Ensure asset directory exists
        ensure_assets_dir()

        # Sound files
        self.sound_files = {
            "paddle": os.path.join(ASSETS_DIR, "paddle_hit.wav"),
            "wall": os.path.join(ASSETS_DIR, "wall_bounce.wav"),
            "score": os.path.join(ASSETS_DIR, "score.wav")
        }

        # Generate test sounds if missing
        freqs = {"paddle": 700.0, "wall": 400.0, "score": 900.0}
        for name, path in self.sound_files.items():
            if not os.path.exists(path) or os.path.getsize(path) < 44:
                try:
                    generate_test_sound(path, freq=freqs.get(name, 600.0), duration=0.12)
                except Exception as e:
                    print("⚠️ Could not auto-generate test sound:", e)

        # Load sounds
        pygame.mixer.init()
        self.sounds = {}
        for key, path in self.sound_files.items():
            try:
                self.sounds[key] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"⚠️ Failed to load {path}: {e}")
                self.sounds[key] = None

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-8, self.height)
        if keys[pygame.K_s]:
            self.player.move(8, self.height)

    def update(self):
        old_vy = self.ball.velocity_y
        self.ball.move()
        event = self.ball.check_collision(self.player, self.ai)

        # Paddle hit
        if event == "paddle" and self.sounds.get("paddle"):
            try:
                self.sounds["paddle"].play()
            except Exception:
                pass

        # Wall bounce
        if self.ball.velocity_y != old_vy and self.sounds.get("wall"):
            try:
                self.sounds["wall"].play()
            except Exception:
                pass

        # Scoring
        if self.ball.x <= 0:
            self.ai_score += 1
            if self.sounds.get("score"):
                try:
                    self.sounds["score"].play()
                except Exception:
                    pass
            self.ball.reset()
        elif self.ball.x + self.ball.width >= self.width:
            self.player_score += 1
            if self.sounds.get("score"):
                try:
                    self.sounds["score"].play()
                except Exception:
                    pass
            self.ball.reset()

        # Simple AI
        self.ai.auto_track(self.ball, self.height)

    def render(self, screen):
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width // 2, 0), (self.width // 2, self.height))

        # Scores
        screen.blit(self.font.render(str(self.player_score), True, WHITE), (self.width // 4, 20))
        screen.blit(self.font.render(str(self.ai_score), True, WHITE), (self.width * 3 // 4, 20))

    def show_replay_menu(self, screen):
        options = [
            ("Press 3 — Best of 3", 3),
            ("Press 5 — Best of 5", 5),
            ("Press 7 — Best of 7", 7),
            ("Press ESC — Exit", "exit"),
        ]
        while True:
            screen.fill(BLACK)
            title = self.font.render("Play Again?", True, WHITE)
            screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 3))
            for i, (text, _) in enumerate(options):
                opt = self.font.render(text, True, WHITE)
                screen.blit(opt, (self.width // 2 - opt.get_width() // 2, self.height // 2 + i * 40))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_3:
                        return 3
                    elif event.key == pygame.K_5:
                        return 5
                    elif event.key == pygame.K_7:
                        return 7
                    elif event.key == pygame.K_ESCAPE:
                        return "exit"