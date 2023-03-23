from __future__ import annotations

from typing import Self, Callable, Any
from window import Window
import pygame


class Element:
    __slots__ = ('__children', '__window', 'parent', 'x', 'y', 'w', 'h', 'update_func', 'handle_event_func', 'data')

    def __init__(self,
                 window: Window = None,
                 update: Callable[[Self], None] = None,
                 handle_event: Callable[[Self], bool] = None,
                 data: dict[str, Any] = None,
                 x: int = 0, y: int = 0, w: int = 0, h: int = 0):
        self.__children: dict[str, Self] = {}
        self.__window = window
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.update_func = update or _default_update
        self.handle_event_func = handle_event or _default_handle_event
        self.data = data
        self.parent: Element | None = None

    @property
    def window(self):
        return self.__window

    @window.setter
    def window(self, value):
        self.__window = value
        for child in self.__children.values():
            child.window = value

    def update(self) -> None:
        self.update_func(self)
        for child in self.__children.values():
            child.update()

    def handle_event(self, event: pygame.event.Event) -> bool:
        for child in reversed(self.__children.values()):
            if child.handle_event(event):
                return True
        return self.handle_event_func(self, event)

    def add_child(self, name: str, child: Element) -> Self:
        self.__children[name] = child
        child.window = self.window
        child.parent = self
        return self

    def remove_child(self, name: str) -> Self:
        del self.__children[name]
        return Self

    def get_child(self, name: str):
        return self.__children.get(name)


def _default_update(element: Element) -> None:
    return


def _default_handle_event(element: Element, event: pygame.event.Event) -> bool:
    return False
