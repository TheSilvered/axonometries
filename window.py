import pygame
from pygame.locals import *
from typing import Self


class Window:
    def __init__(self) -> None:
        self.__screen = pygame.display.set_mode((1280, 720), RESIZABLE)
        pygame.display.set_caption("Assonometrie")
        pygame.display.set_icon(pygame.image.load("assets/icons/icon.png"))
        self.__running = True
        self.elements = {}
        self.__clock = pygame.time.Clock()

    @property
    def screen(self) -> pygame.Surface:
        return self.__screen

    @property
    def w(self):
        return self.__screen.get_width()

    @property
    def h(self):
        return self.__screen.get_height()

    def add_element(self, name: str, element) -> Self:
        self.elements[name] = element
        element.window = self
        return self

    def remove_element(self, name: str) -> Self:
        del self.elements[name]
        return self

    def update(self) -> None:
        for element in self.elements.values():
            element.update()
        pygame.display.update()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            for element in reversed(self.elements.values()):
                if element.handle_event(event):
                    break
            else:
                if event.type == QUIT:
                    self.__running = False

    def schedule_quit(self) -> None:
        self.__running = False

    def run(self) -> None:
        while self.__running:
            self.update()
            self.handle_events()

    @staticmethod
    def quit() -> None:
        pygame.quit()
