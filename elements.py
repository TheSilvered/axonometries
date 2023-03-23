import pygame
from pygame.locals import *
import pygame.gfxdraw
from element import Element
from renderer import render_orthogonal_proj, render_axonometry
import ui
from mesh import *
import json
import globals

pygame.font.init()

with open('assets/meshes.json', 'r') as f:
    options = json.load(f)

dark_mode = options['settings']['dark-mode']
only_orthogonal_proj = options['settings']['only-orthogonal-proj']
use_color = options['settings']['use-color']
zy = 120.0
yx = 240.0
xm = 1
ym = 1
zm = 1

globals.DM_C_DETAIL = tuple(options['dark-theme']['detail'])
globals.DM_C_DETAIL_DIMMED = tuple(options['dark-theme']['detail-dimmed'])
globals.DM_C_GENERAL = tuple(options['dark-theme']['general'])

globals.LM_C_DETAIL = tuple(options['light-theme']['detail'])
globals.LM_C_DETAIL_DIMMED = tuple(options['light-theme']['detail-dimmed'])
globals.LM_C_GENERAL = tuple(options['light-theme']['general'])

if dark_mode:
    globals.C_DETAIL = globals.DM_C_DETAIL
    globals.C_DETAIL_DIMMED = globals.DM_C_DETAIL_DIMMED
    globals.C_GENERAL = globals.DM_C_GENERAL
else:
    globals.C_DETAIL = globals.LM_C_DETAIL
    globals.C_DETAIL_DIMMED = globals.LM_C_DETAIL_DIMMED
    globals.C_GENERAL = globals.LM_C_GENERAL

scale = 20
true_scale = 20
transparency = options['settings']['transparency']
font = pygame.font.Font('assets/fonts/Inter-Regular.ttf', 18)

zoom_in_dark = pygame.image.load('assets/icons/zoom-in-dark.png')
zoom_out_dark = pygame.image.load('assets/icons/zoom-out-dark.png')
zoom_in_light = pygame.image.load('assets/icons/zoom-in.png')
zoom_out_light = pygame.image.load('assets/icons/zoom-out.png')

with open('assets/meshes.json', 'r') as f:
    meshes = [itom(mesh) for mesh in options['meshes']]

colors = [tuple(color) for color in options['mesh-colors']]


def set_zy_value(e: Element):
    global zy
    zy = round(90 * e.data['value'] + 90)
    if not e.data['grabbed']:
        e.data['value'] = zy / 90 - 1


def set_yx_value(e: Element):
    global yx
    yx = round(90 * (1 - e.data['value']) + 180)
    if not e.data['grabbed']:
        e.data['value'] = -yx / 90 + 3


def set_xm_value(e: Element):
    global xm
    xm = round(e.data['value'], 1)
    if not e.data['grabbed']:
        e.data['value'] = xm


def set_ym_value(e: Element):
    global ym
    ym = round(e.data['value'], 1)
    if not e.data['grabbed']:
        e.data['value'] = ym


def set_zm_value(e: Element):
    global zm
    zm = round(e.data['value'], 1)
    if not e.data['grabbed']:
        e.data['value'] = zm


def set_scale_value(e: Element):
    global scale, true_scale
    if e.data['grabbed']:
        true_scale = e.data['value'] * 95 + 5
        scale = int(true_scale)
    else:
        e.data['value'] = (true_scale - 5) / 95


def bg_update(e: Element):
    screen = e.window.screen
    win_half_w = e.window.w // 2
    win_half_h = e.window.h // 2
    e.window.screen.fill(globals.C_GENERAL)
    pr = orthogonal_proj_renderer

    if only_orthogonal_proj:
        pygame.draw.line(screen, globals.C_DETAIL_DIMMED, [0, win_half_h + pr.y], [e.window.w, win_half_h + pr.y], 2)
        pygame.draw.line(screen, globals.C_DETAIL_DIMMED, [win_half_w + pr.x, 0], [win_half_w + pr.x, e.window.h], 2)
    else:
        pygame.draw.line(screen, globals.C_DETAIL_DIMMED, [win_half_w, 0], [win_half_w, e.window.h], 2)
        pygame.draw.line(screen, globals.C_DETAIL_DIMMED, [0, win_half_h + pr.y], [win_half_w, win_half_h + pr.y], 2)
    for x in range(win_half_w + pr.x, -1, -scale):
        for y in range(win_half_h + pr.y, -1, -scale):
            screen.set_at((x, y), globals.C_DETAIL_DIMMED)
    for x in range(win_half_w + pr.x, -1, -scale):
        for y in range(win_half_h + pr.y, e.window.h, scale):
            screen.set_at((x, y), globals.C_DETAIL_DIMMED)
    if only_orthogonal_proj:
        for x in range(win_half_w + pr.x, e.window.w, scale):
            for y in range(win_half_h + pr.y, -1, -scale):
                screen.set_at((x, y), globals.C_DETAIL_DIMMED)
    e.window.elements['fg'].data['labels']['lt_label'][1] = [3, win_half_h - 23 + pr.y]
    e.window.elements['fg'].data['labels']['po_label'][1] = [3, e.window.h - 23]
    if only_orthogonal_proj:
        e.window.elements['fg'].data['labels']['pl_label'][1] = [e.window.w - font.size('P.L.')[0] - 3, 3]
    else:
        e.window.elements['fg'].data['labels']['pl_label'][1] = [e.window.w + 1, e.window.h + 1]


def fg_update(e: Element):
    for label in e.data['labels'].values():
        if len(label) == 2:
            label.append(font.render(label[0], True, globals.C_DETAIL))
        e.window.screen.blit(label[2], label[1])


def orthogonal_proj_renderer_update(e: Element):
    render_orthogonal_proj(
        meshes,
        colors if use_color else [globals.C_DETAIL],
        e.window.screen,
        e.window.w // 2 + e.x, e.window.h // 2 + e.y,
        scale,
        only_orthogonal_proj,
        transparency,
        globals.C_DETAIL_DIMMED)


def orthogonal_proj_renderer_handle_event(e: Element, event: pygame.event.Event):
    if event.type == WINDOWFOCUSLOST:
        e.data['panning'] = False
        return False
    elif event.type == MOUSEBUTTONDOWN and event.button == BUTTON_LEFT \
            and (event.pos[0] < e.window.w / 2 or only_orthogonal_proj):
        e.data['panning'] = True
        return True
    elif event.type == MOUSEBUTTONUP:
        e.data['panning'] = False
        return False
    elif event.type == MOUSEMOTION and e.data['panning']:
        e.x += event.rel[0]
        e.y += event.rel[1]
        return True
    return False


def isometric_axonometry_renderer_update(e: Element):
    if only_orthogonal_proj:
        if 'a_label' in fg.data['labels']:
            del fg.data['labels']['a_label']
            del fg.data['labels']['b_label']
            del fg.data['labels']['x_label']
            del fg.data['labels']['y_label']
            del fg.data['labels']['z_label']
        if e.get_child('sliders'):
            e.remove_child('sliders')
        return
    surf = pygame.Surface((e.window.w // 2 + 1, e.window.h))
    surf.fill(globals.C_GENERAL)
    render_axonometry(
        meshes,
        colors if use_color else [globals.C_DETAIL],
        surf,
        e.x, e.y,
        ym * scale, xm * scale, zm * scale,
        transparency,
        -90, zy, yx, 0
    )

    e.window.screen.blit(surf, (e.window.w // 2 + 2, 0))
    e.add_child('sliders', sliders)
    fg.data['labels']['a_label'] = [f'α: {zy:.0f}°', (e.window.w - 460, 12)]
    fg.data['labels']['b_label'] = [f'β: {360 - yx:.0f}°', (e.window.w - 459, 32)]
    fg.data['labels']['x_label'] = [f'x: {xm:.1f}', (e.window.w - 185, 52)]
    fg.data['labels']['y_label'] = [f'y: {ym:.1f}', (e.window.w - 185, 72)]
    fg.data['labels']['z_label'] = [f'z: {zm:.1f}', (e.window.w - 185, 92)]


def isometric_axonometry_renderer_handle_event(e: Element, event: pygame.event.Event):
    if only_orthogonal_proj:
        e.data['panning'] = False
        return False

    if event.type == WINDOWFOCUSLOST:
        e.data['panning'] = False
        return False
    elif event.type == MOUSEBUTTONDOWN and event.button == BUTTON_LEFT and event.pos[0] > e.window.w / 2:
        e.data['panning'] = True
        return True
    elif event.type == MOUSEBUTTONUP:
        e.data['panning'] = False
        return False
    elif event.type == MOUSEMOTION and e.data['panning']:
        e.x += event.rel[0]
        e.y += event.rel[1]
        return True
    return False


def key_event_handler(e: Element, event: pygame.event.Event):
    global scale, only_orthogonal_proj, dark_mode
    global transparency, use_color, true_scale

    if event.type == KEYDOWN:
        if event.key == K_m:
            dark_mode = not dark_mode
            if dark_mode:
                globals.C_DETAIL = globals.DM_C_DETAIL
                globals.C_DETAIL_DIMMED = globals.DM_C_DETAIL_DIMMED
                globals.C_GENERAL = globals.DM_C_GENERAL
            else:
                globals.C_DETAIL = globals.LM_C_DETAIL
                globals.C_DETAIL_DIMMED = globals.LM_C_DETAIL_DIMMED
                globals.C_GENERAL = globals.LM_C_GENERAL
            for label in e.window.elements['fg'].data['labels'].values():
                if len(label) == 3:
                    label.pop()
            return True
        elif event.key == K_o:
            only_orthogonal_proj = not only_orthogonal_proj
            return True
        elif event.key == K_c:
            use_color = not use_color
            return True
        elif event.key == K_PLUS or event.key == K_KP_PLUS:
            transparency += 15
            if transparency > 255:
                transparency = 255
            return True
        elif event.key == K_MINUS or event.key == K_KP_MINUS:
            transparency -= 15
            if transparency < 0:
                transparency = 0
            return True
    elif event.type == MOUSEWHEEL:
        true_scale += event.y * (scale / 10)
        if true_scale < 5:
            true_scale = 5
        if true_scale > 100:
            true_scale = 100
        scale = int(true_scale)
        return True


def zoom_in_update(e: Element):
    e.x = e.window.w // 2 + 115
    e.y = e.window.h - 32
    if dark_mode:
        e.window.screen.blit(zoom_in_dark, (e.x, e.y))
    else:
        e.window.screen.blit(zoom_in_light, (e.x, e.y))


def zoom_out_update(e: Element):
    e.x = e.window.w // 2 - 135
    e.y = e.window.h - 32
    if dark_mode:
        e.window.screen.blit(zoom_out_dark, (e.x, e.y))
    else:
        e.window.screen.blit(zoom_out_light, (e.x, e.y))


bg = Element(update=bg_update)
fg = Element(
    update=fg_update,
    data={'labels': {
        'lt_label': ['L.T.', [0, 0]],
        'po_label': ['P.O.', [0, 0]],
        'pv_label': ['P.V.', [3, 3]],
        'pl_label': ['P.L.', [0, 0]],
    }}
)

orthogonal_proj_renderer = Element(
    update=orthogonal_proj_renderer_update,
    handle_event=orthogonal_proj_renderer_handle_event,
    data={'panning': False}
)
isometric_axonometry_renderer = Element(
    update=isometric_axonometry_renderer_update,
    handle_event=isometric_axonometry_renderer_handle_event,
    data={'panning': False}
)
isometric_axonometry_renderer.x = 320
isometric_axonometry_renderer.y = 360
key_event_handler = Element(handle_event=key_event_handler)

zy_slider = Element(
    update=ui.slider_update,
    handle_event=ui.slider_handle_event,
    w=375,
    data={
        'value': 1 / 3,
        'grabbed': False,
        'set-value': set_zy_value,
        'anchor': {
            'from': 'rt',
            'to': 'rt',
            'offset': (-20, 20)
        }
    }
)

yx_slider = Element(
    update=ui.slider_update,
    handle_event=ui.slider_handle_event,
    w=375,
    data={
        'value': 1 / 3,
        'grabbed': False,
        'set-value': set_yx_value,
        'anchor': {
            'from': 'rt',
            'to': 'rt',
            'offset': (-20, 40)
        }
    }
)

xm_slider = Element(
    update=ui.slider_update,
    handle_event=ui.slider_handle_event,
    w=115,
    data={
        'value': 1,
        'grabbed': False,
        'set-value': set_xm_value,
        'anchor': {
            'from': 'rt',
            'to': 'rt',
            'offset': (-20, 60)
        }
    }
)

ym_slider = Element(
    update=ui.slider_update,
    handle_event=ui.slider_handle_event,
    w=115,
    data={
        'value': 1,
        'grabbed': False,
        'set-value': set_ym_value,
        'anchor': {
            'from': 'rt',
            'to': 'rt',
            'offset': (-20, 80)
        }
    }
)

zm_slider = Element(
    update=ui.slider_update,
    handle_event=ui.slider_handle_event,
    w=115,
    data={
        'value': 1,
        'grabbed': False,
        'set-value': set_zm_value,
        'anchor': {
            'from': 'rt',
            'to': 'rt',
            'offset': (-20, 100)
        }
    }
)

scale_slider = Element(
    update=ui.slider_update,
    handle_event=ui.slider_handle_event,
    w=216, h=15,
    data={
        'value': 3 / 19,
        'grabbed': False,
        'set-value': set_scale_value,
        'anchor': {
            'from': 'cb',
            'to': 'cb',
            'offset': (0, -10)
        }
    }
)

sliders = Element(
    update=ui.container_update,
    data={
        'anchor': {
            'from': 'rt',
            'to': 'rt',
            'link-window': True
        }
    }
) \
    .add_child('zy_slider', zy_slider) \
    .add_child('yx_slider', yx_slider) \
    .add_child('xm_slider', xm_slider) \
    .add_child('ym_slider', ym_slider) \
    .add_child('zm_slider', zm_slider)

zoom_in = Element(update=zoom_in_update)
zoom_out = Element(update=zoom_out_update)
