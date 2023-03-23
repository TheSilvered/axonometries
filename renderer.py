import pygame
import pygame.gfxdraw
from mesh import *
import draw


def proj_point(point_list, orig_x, orig_y, scale, polygons, vlinks, hlinks, rlinks, i, show_pl):
    points_po = []
    points_pv = []
    points_pl = []
    for point in point_list:
        p1 = (orig_x - point[0] * scale, orig_y + point[1] * scale)
        p2 = (orig_x - point[0] * scale, orig_y - point[2] * scale)
        p3 = (orig_x + point[1] * scale, orig_y - point[2] * scale)
        points_po.append(p1)
        points_pv.append(p2)
        points_pl.append(p3)
        vlinks.append((p1, p2))
        hlinks.append((p2, p3))
        rlinks.append((p1, p3))
    polygons.append([points_po, sum(point[2] for point in point_list) / len(point_list), i])
    polygons.append([points_pv, sum(point[1] for point in point_list) / len(point_list), i])
    if show_pl:
        polygons.append([points_pl, sum(point[0] for point in point_list) / len(point_list), i])


def render_orthogonal_proj(meshes: list[Mesh], colors, surf, orig_x, orig_y, scale, show_pl, alpha, line_color):
    polygons = []
    vlinks = []
    hlinks = []
    rlinks = []

    for i, mesh in enumerate(meshes):
        for face in mesh.faces:
            for tri in face.triangles:
                proj_point(tri.point_list(), orig_x, orig_y, scale,
                           polygons,
                           vlinks, hlinks, rlinks, i, show_pl)

            for edge in face.edges:
                proj_point(edge.point_list(), orig_x, orig_y, scale,
                           polygons,
                           vlinks, hlinks, rlinks, i, show_pl)

    for link in vlinks:
        pygame.draw.line(surf, line_color, link[0], link[1])
    if show_pl:
        for link in hlinks:
            pygame.draw.line(surf, line_color, link[0], link[1])
        for link in rlinks:
            pass
            pygame.gfxdraw.arc(surf, orig_x, orig_y, int(link[0][1]) - orig_y, 0, 90, line_color)
            pygame.draw.line(surf, line_color, link[0], (orig_x, link[0][1]))
            pygame.draw.line(surf, line_color, link[1], (link[1][0], orig_y))

    polygons.sort(key=lambda x: x[1])

    for polygon in polygons:
        if len(polygon[0]) == 3:
            pygame.gfxdraw.filled_polygon(surf, polygon[0], colors[polygon[2] % len(colors)] + (alpha,))
        else:
            pygame.draw.aaline(surf, colors[polygon[2] % len(colors)], polygon[0][0], polygon[0][1])


def render_axonometry(meshes: list[Mesh], colors, surf, offset_x, offset_y, xm, ym, zm, alpha, a, zy, yx, xz):
    elements = []
    for i, mesh in enumerate(meshes):
        for face in mesh.faces:
            elements.extend([(i, edge) for edge in face.edges])
            elements.extend([(i, tri) for tri in face.triangles])

    elements.sort(key=lambda el: min(i[2] for i in el[1].point_list())
                               + min(i[1] for i in el[1].point_list())
                               + min(i[0] for i in el[1].point_list()))

    for element in elements:
        points = element[1].project_to_2d(a, zy, yx, xz, xm, ym, zm, offset_x, offset_y, (1, 0, 2)).point_list()
        if len(points) == 2:
            pygame.draw.aaline(surf, colors[element[0] % len(colors)], points[0], points[1])
        else:
            pygame.gfxdraw.filled_polygon(surf, points, colors[element[0] % len(colors)] + (alpha,))
