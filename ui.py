from element import Element
import globals
import draw
import pygame
from pygame.locals import *


def pos_update(e: Element):
    if 'anchor' not in e.data:
        return
    if e.parent is None or e.data['anchor'].get('link-window', False):
        parent_x = 0
        parent_y = 0
        parent_w = e.window.w
        parent_h = e.window.h
    else:
        parent_x = e.parent.x
        parent_y = e.parent.y
        parent_w = e.parent.w
        parent_h = e.parent.h

    new_x = 0
    new_y = 0

    from_x = e.data['anchor']['from'][0]
    from_y = e.data['anchor']['from'][1]
    to_x = e.data['anchor']['to'][0]
    to_y = e.data['anchor']['to'][1]
    if from_x == 'l':
        new_x = parent_x
    elif from_x == 'c':
        new_x = parent_x + parent_w // 2
    elif from_x == 'r':
        new_x = parent_x + parent_w

    if from_y == 't':
        new_y = parent_y
    elif from_y == 'c':
        new_y = parent_y + parent_h // 2
    elif from_y == 'b':
        new_y = parent_y + parent_h

    if to_x == 'c':
        new_x -= e.w // 2
    elif to_x == 'r':
        new_x -= e.w

    if to_y == 'c':
        new_y -= e.h // 2
    elif to_y == 'b':
        new_y -= e.h
    offset = e.data['anchor'].get('offset', (0, 0))
    new_x += offset[0]
    new_y += offset[1]
    e.x = int(new_x)
    e.y = int(new_y)


def size_update(e: Element):
    if 'rel-size' not in e.data:
        return
    if e.parent is None or e.data['rel-size'].get('link-window', False):
        parent_w = e.window.w
        parent_h = e.window.h
    else:
        parent_w = e.parent.w
        parent_h = e.parent.h

    new_w = parent_w * e.data['rel-size']['w']
    new_h = parent_h * e.data['rel-size']['h']

    if new_w == 0: new_w = e.w
    if new_h == 0: new_h = e.h

    offset = e.data['anchor'].get('offset', (0, 0))
    new_w += offset[0]
    new_h += offset[1]

    if new_w > e.data['rel-size'].get('max-w', new_w):
        new_w = e.data['rel-size']['max-w']
    if new_h > e.data['rel-size'].get('max-h', new_h):
        new_h = e.data['rel-size']['max-h']

    if new_w < e.data['rel-size'].get('min-w', new_w):
        new_w = e.data['rel-size']['min-w']
    if new_h < e.data['rel-size'].get('min-h', new_h):
        new_h = e.data['rel-size']['min-h']

    e.w = int(new_w)
    e.h = int(new_h)


def slider_update(e: Element):
    size_update(e)
    pos_update(e)
    # draw.aa_rect(e.window.screen, (e.x, e.y, e.w, 5), globals.C_DETAIL_DIMMED, 2)
    draw.aa_rect(e.window.screen, (e.x, e.y - 5, e.w, 15), globals.C_DETAIL_DIMMED, 10)
    cur_w = round((e.w - 15) * e.data['value'])
    # draw.odd_circle(e.window.screen, [cur_x + 7, e.y + 2], 7, globals.C_DETAIL)
    draw.aa_rect(e.window.screen, (e.x + 1, e.y - 4, cur_w + 13, 13), globals.C_GENERAL, 10)
    draw.aa_rect(e.window.screen, (e.x + cur_w, e.y - 5, 15, 15), globals.C_GENERAL, 10, 1, globals.C_DETAIL_DIMMED)
    e.data['set-value'](e)


def slider_handle_event(e: Element, event: pygame.event.Event):
    cur_x = e.x + (e.w - 15) * e.data['value']
    if event.type == MOUSEBUTTONDOWN and cur_x - 3 <= event.pos[0] < cur_x + 18 and e.y - 8 <= event.pos[1] < e.y + 13:
        e.data['grabbed'] = True
        e.data['x-rel'] = event.pos[0] - cur_x
        return True
    elif event.type == MOUSEBUTTONUP:
        e.data['grabbed'] = False
        return False
    elif event.type == MOUSEMOTION and e.data['grabbed']:
        e.data['value'] = (event.pos[0] - e.x - e.data['x-rel']) / (e.w - 15)
        if e.data['value'] < 0: e.data['value'] = 0
        if e.data['value'] > 1: e.data['value'] = 1
        return True


def image_update(e: Element):
    e.w = e.data['image'].get_width()
    e.h = e.data['image'].get_height()
    pos_update(e)
    e.window.screen.blit(e.data['image'], (e.x, e.y))


def container_update(e: Element):
    size_update(e)
    pos_update(e)
