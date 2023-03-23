import pygame
from math import hypot

even_circle_cache = {}
odd_circle_cache = {}
rect_cache = {}


def _draw_quarters(surf, rad, col, border, b_col, w, h) -> None:
    in_rad = rad - border
    alpha_col = len(col) == 4
    alpha_b_col = b_col and len(b_col) == 4

    for x in range(rad):
        for y in range(rad):
            inv_x = w - x - 1
            inv_y = h - y - 1

            distance = hypot(x - rad, y - rad)

            if distance < in_rad:
                surf.set_at((x, y), col)
                surf.set_at((inv_x, y), col)
                surf.set_at((x, inv_y), col)
                surf.set_at((inv_x, inv_y), col)

            elif border and distance < in_rad + 1:
                alpha = 1 - (distance - in_rad)
                new_color = [alpha * c1 + (1 - alpha) * c2 for c1, c2 in zip(col, b_col)]
                surf.set_at((x, y), new_color)
                surf.set_at((inv_x, y), new_color)
                surf.set_at((x, inv_y), new_color)
                surf.set_at((inv_x, inv_y), new_color)

            elif distance < rad:
                surf.set_at((x, y), b_col)
                surf.set_at((inv_x, y), b_col)
                surf.set_at((x, inv_y), b_col)
                surf.set_at((inv_x, inv_y), b_col)

            elif distance < rad + 1:
                if border:
                    alpha = (b_col[3] if alpha_b_col else 255) * (1 - (distance - rad))
                    new_color = list(b_col[:3])
                else:
                    alpha = (col[3] if alpha_col else 255) * (1 - (distance - rad))
                    new_color = list(col[:3])
                new_color.append(alpha)

                surf.set_at((x, y), new_color)
                surf.set_at((inv_x, y), new_color)
                surf.set_at((x, inv_y), new_color)
                surf.set_at((inv_x, inv_y), new_color)


def even_circle(surface: pygame.Surface | None,
                center: tuple[int, int] | list[int],
                radius: int,
                color,
                border: int = 0,
                border_color=None) -> pygame.Surface:
    blit_pos = (center[0] - radius, center[1] - radius)
    radius = round(radius)
    if radius - border < 0: border = radius

    key = (radius, color, border, border_color)

    surf = even_circle_cache.get(key, None)
    if surface is not None and surf is not None:
        surface.blit(surf, blit_pos)
        return surf

    new_surf = pygame.Surface((radius*2, radius*2), flags=pygame.SRCALPHA)
    new_surf.set_colorkey((0, 0, 0))

    _draw_quarters(
        new_surf,
        radius,
        color,
        border,
        border_color,
        radius*2,
        radius*2
    )

    if surface is not None: surface.blit(new_surf, blit_pos)
    even_circle_cache[key] = new_surf
    return new_surf


def odd_circle(surface: pygame.Surface | None,
               center,
               radius: int,
               color,
               border: int = 0,
               border_color=None) -> pygame.Surface:
    blit_pos = (center[0] - radius, center[1] - radius)
    radius = round(radius)
    if radius - border < 0: border = radius

    key = (radius, color, border, border_color)

    surf = odd_circle_cache.get(key, None)
    if surface is not None and surf is not None:
        surface.blit(surf, blit_pos)
        return surf

    size = (radius * 2 + 1, radius * 2 + 1)

    new_surf = pygame.Surface(size, flags=pygame.SRCALPHA)
    new_surf.set_colorkey((0, 0, 0))

    _draw_quarters(
        new_surf,
        radius,
        color,
        border,
        border_color,
        radius * 2 + 1,
        radius * 2 + 1
    )

    if border:
        pygame.draw.line(new_surf, border_color, (radius, 0), (radius, radius*2))
        pygame.draw.line(new_surf, border_color, (0, radius), (radius*2, radius))
    pygame.draw.line(new_surf, color, (radius, border), (radius, radius*2 - border))
    pygame.draw.line(new_surf, color, (border, radius), (radius*2 - border, radius))

    if surface is not None: surface.blit(new_surf, blit_pos)
    odd_circle_cache[key] = new_surf
    return new_surf


def aa_rect(surface: pygame.Surface | None,
            rect,
            color,
            corner_radius: int = 0,
            border: int = 0,
            border_color=None) -> pygame.Surface:
    corner_radius = round(corner_radius)
    rect = pygame.Rect(rect)
    if corner_radius > min(rect.width, rect.height) / 2:
        corner_radius = int(min(rect.width, rect.height) / 2)

    if border > min(rect.width, rect.height) / 2:
        border = int(min(rect.width, rect.height) / 2)

    key = (rect.size, color, corner_radius, border, border_color)

    surf = rect_cache.get(key, None)
    if surface is not None and surf is not None:
        surface.blit(surf, rect.topleft)
        return surf

    new_surf = pygame.Surface(rect.size, flags=pygame.SRCALPHA)
    new_surf.set_colorkey((0, 0, 0))
    line_rect = pygame.Rect(0, 0, rect.w, rect.h)
    inner_rect = pygame.Rect(border, border, rect.w - border*2, rect.h - border*2)
    inner_radius = corner_radius - border

    if border:
        pygame.draw.rect(new_surf, border_color, line_rect, 0, corner_radius)
    pygame.draw.rect(new_surf, color, inner_rect, 0, inner_radius)

    _draw_quarters(
        new_surf,
        corner_radius,
        color,
        border,
        border_color,
        rect.w,
        rect.h
    )

    if surface is not None: surface.blit(new_surf, rect.topleft)
    rect_cache[key] = new_surf
    return new_surf


def aa_line(surface: pygame.Surface,
            color,
            start_pos,
            end_pos,
            width: int = 1) -> None:
    if width < 0: return

    if width == 0:
        pygame.draw.aaline(surface, color, start_pos, end_pos)
        return
    width *= 2

    horizontal = abs(start_pos[0] - end_pos[0]) <= abs(start_pos[1] - end_pos[1])

    pygame.draw.line(surface, color, start_pos, end_pos, round(width))
    line_offset = (width / 2, 0) if horizontal else (0, width / 2)
    pygame.draw.aaline(
        surface, color,
        (start_pos[0] + line_offset[0], start_pos[1] + line_offset[1]),
        (end_pos[0]   + line_offset[0], end_pos[1]   + line_offset[1]))
    pygame.draw.aaline(
        surface, color,
        (start_pos[0] - line_offset[0], start_pos[1] - line_offset[1]),
        (end_pos[0]   - line_offset[0], end_pos[1]   - line_offset[1]))
