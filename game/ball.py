import pygame
import random
import math

class Ball:
    def __init__(self, x, y, width, height, screen_width, screen_height):
        self.original_x = x
        self.original_y = y
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.velocity_x = random.choice([-5.0, 5.0])
        self.velocity_y = random.choice([-3.0, 3.0])

    def move(self):
        """Move the ball (positions are floats for smoothness). Handle wall bounces."""
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Top/bottom wall bounce with clamp
        if self.y <= 0:
            self.y = 0
            self.velocity_y *= -1
        elif self.y + self.height >= self.screen_height:
            self.y = self.screen_height - self.height
            self.velocity_y *= -1

    def check_collision(self, player, ai):
        """
        Robust paddle collision:
        - Sub-step movement to avoid tunneling.
        - Returns event string: "paddle" if paddle hit, None otherwise.
        """

        # Current integer rect for drawing/collision API
        ball_rect = self.rect()

        # Determine steps from largest velocity magnitude (at least 1)
        steps = int(max(1, math.ceil(max(abs(self.velocity_x), abs(self.velocity_y)))))

        # Simulate movement in small steps and check collision at each step
        for i in range(1, steps + 1):
            # fractional movement up to this sub-step
            frac_x = (self.velocity_x * i) / steps
            frac_y = (self.velocity_y * i) / steps
            test_rect = ball_rect.move(int(frac_x), int(frac_y))

            # Player paddle collision
            if test_rect.colliderect(player.rect()):
                # place ball just outside player paddle (on player side)
                if self.velocity_x > 0:  # moving right, hit player (right paddle)
                    self.x = player.x - self.width
                else:
                    self.x = player.x + player.width

                # reverse horizontal velocity
                self.velocity_x *= -1

                # Add vertical deflection based on hit offset (makes game feel realistic)
                hit_pos = (test_rect.centery) - (player.y + player.height / 2)
                # scale deflection; cap to prevent extreme angles
                self.velocity_y += (hit_pos / (player.height / 2)) * 3.0
                self.velocity_y = max(-8, min(8, self.velocity_y))
                return "paddle"

            # AI paddle collision
            if test_rect.colliderect(ai.rect()):
                if self.velocity_x > 0:
                    self.x = ai.x - self.width
                else:
                    self.x = ai.x + ai.width

                self.velocity_x *= -1

                hit_pos = (test_rect.centery) - (ai.y + ai.height / 2)
                self.velocity_y += (hit_pos / (ai.height / 2)) * 3.0
                self.velocity_y = max(-8, min(8, self.velocity_y))
                return "paddle"

        return None

    def reset(self):
        """Reset ball to center with randomized direction and mild speed variation."""
        self.x = float(self.original_x)
        self.y = float(self.original_y)
        self.velocity_x = random.choice([-5.0, 5.0])
        # small random vertical velocity, avoid 0
        self.velocity_y = random.choice([-3.0, -2.0, 2.0, 3.0])

    def rect(self):
        """Return a pygame.Rect for the current integer-rounded position."""
        return pygame.Rect(int(round(self.x)), int(round(self.y)), self.width, self.height)
