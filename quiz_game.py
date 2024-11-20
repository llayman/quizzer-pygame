""" A simple quiz game using Pygame that interacts with the Flask quizzer API. """

import sys
from uuid import UUID

import pygame
import requests


class MultipleChoiceQuestion:
    """A class to represent a multiple choice question"""

    def __init__(self, question_id: UUID, question_text: str,  answer_index: int, choices: list[str]):
        """Constructor for MultipleChoiceQuestion

        Args:
            question_id (UUID): The unique identifier for the question
            question_text (str): The question to be asked
            answer_index (int): The index of the correct answer in the choices list
            choices (list[str]): the list of choices for the question
        """
        self.question_id = question_id
        self.question_text = question_text
        self.answer_index = answer_index
        self.choices = choices

    def __repr__(self) -> str:
        return f"MultipleChoiceQuestion({self.question_id}, {self.question_text}, {self.answer_index}, {self.choices})"


# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize Pygame
pygame.init()

# Fonts
FONT = pygame.font.Font(None, 36)
LARGE_FONT = pygame.font.Font(None, 48)

# API Base URL
API_BASE_URL = "http://127.0.0.1:5000/api"


class GameException(Exception):
    """A custom exception class for the game."""


def fetch_random_question() -> MultipleChoiceQuestion:
    """Fetch a random question from the API."""
    response = requests.get(f"{API_BASE_URL}/random-question", timeout=5)
    if response.status_code == 200:
        return MultipleChoiceQuestion(**response.json())
    elif response.status_code == 400:
        raise GameException(f"Bad request: {response.json()['message']}")
    else:
        raise GameException(
            "Something is wrong reaching the Flask quizzer API.")


def check_answer(question: MultipleChoiceQuestion, selected_option: int) -> bool:
    """Check if the selected answer is correct using the API."""
    response = requests.get(
        f"{API_BASE_URL}/question/{question.question_id}/answer/{selected_option}", timeout=5)
    if response.status_code == 200:
        return response.json()["is_correct"]
    elif response.status_code == 400:
        raise GameException(f"Bad request: {response.json()['message']}")
    else:
        raise GameException(
            "Something is wrong reaching the Flask quizzer API.")


def draw_text(screen: pygame.Surface, text: str, x: int, y: int, font: pygame.font.Font, color: tuple[int, int, int] = WHITE) -> None:
    """Render and draw text on the screen."""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def draw_question(screen, question: MultipleChoiceQuestion, selected_option: int = 0, score: int = 0) -> None:
    """Draw the current question and options on the screen."""
    screen.fill(BLACK)
    if question:
        draw_text(screen, question.question_text, 20, 50, LARGE_FONT, WHITE)
        for i, option in enumerate(question.choices):
            color = GREEN if i == selected_option else WHITE
            draw_text(screen, f"{i + 1}. {option}",
                      50, 150 + i * 40, FONT, color)
    draw_text(screen, f"Score: {score}", 20, HEIGHT - 50, FONT, BLUE)
    pygame.display.flip()


def main():
    """Main function containing the game loop."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Quiz Game")

    # Game Variables
    score = 0
    selected_option = 0

    # Fetch the first question
    question = fetch_random_question()

    # Main Game Loop
    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_running = False
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option +
                                       1) % len(question.choices)
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option -
                                       1) % len(question.choices)
                elif event.key == pygame.K_RETURN:
                    if check_answer(question, selected_option):
                        question = fetch_random_question()
                        selected_option = 0

        draw_question(screen, question, selected_option, score)

    # End screen
    screen.fill(BLACK)
    draw_text(screen, "Game Over!", WIDTH // 2 - 100,
              HEIGHT // 2 - 50, LARGE_FONT, RED)
    draw_text(screen, f"Your Score: {score}", WIDTH //
              2 - 100, HEIGHT // 2, FONT, WHITE)
    pygame.display.flip()
    pygame.time.wait(3000)

    # Quit Pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
