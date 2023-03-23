from dataclasses import dataclass
from math import sin, cos, radians as rad


@dataclass(frozen=True)
class Point3D:
    x: float | int
    y: float | int
    z: float | int

    def __getitem__(self, idx):
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        elif idx == 2:
            return self.z
        else:
            raise IndexError(f'index {idx} out of bounds for 3D point')

    def project_to_2d(self, a, zy, yx, xz, xm, ym, zm, ox, oy, indexes=(1, 0, 2)):
        return Point2D(
              self[indexes[0]] * cos(rad(a + zy)) * xm
            + self[indexes[1]] * cos(rad(a + yx)) * ym
            + self[indexes[2]] * cos(rad(a + xz)) * zm + ox,
              self[indexes[0]] * sin(rad(a + zy)) * xm
            + self[indexes[1]] * sin(rad(a + yx)) * ym
            + self[indexes[2]] * sin(rad(a + xz)) * zm + oy,
        )

    def to_list(self):
        return [self.x, self.y, self.z]


@dataclass(frozen=True)
class Point2D:
    x: float | int
    y: float | int

    def __getitem__(self, idx):
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        else:
            raise IndexError(f'index {idx} out of bounds for 2D point')

    def to_list(self):
        return [self.x, self.y]


@dataclass(frozen=True, eq=False)
class Edge3D:
    p1: Point3D
    p2: Point3D

    def __eq__(self, other):
        return (self.p1 == other.p1 and self.p2 == other.p2) or (self.p1 == other.p2 and self.p2 == other.p1)

    def __hash__(self):
        return hash(frozenset([self.p1, self.p2]))

    def project_to_2d(self, a, zy, yx, xz, xm, ym, zm, ox, oy, indexes=(1, 0, 2)):
        return Edge2D(
            self.p1.project_to_2d(a, zy, yx, xz, xm, ym, zm, ox, oy, indexes),
            self.p2.project_to_2d(a, zy, yx, xz, xm, ym, zm, ox, oy, indexes)
        )

    @property
    def midpoint(self):
        return Point3D(
            (self.p1.x + self.p2.x) / 2,
            (self.p1.y + self.p2.y) / 2,
            (self.p1.z + self.p2.z) / 2
        )

    def point_list(self):
        return [self.p1.to_list(), self.p2.to_list()]


@dataclass(frozen=True, eq=False)
class Edge2D:
    p1: Point2D
    p2: Point2D

    def __eq__(self, other):
        return (self.p1 == other.p1 and self.p2 == other.p2) or (self.p1 == other.p2 and self.p2 == other.p1)

    def __hash__(self):
        return hash(frozenset([self.p1, self.p2]))

    def point_list(self):
        return [self.p1.to_list(), self.p2.to_list()]


@dataclass(frozen=True)
class Triangle3D:
    p1: Point3D
    p2: Point3D
    p3: Point3D

    @property
    def midpoint(self):
        return Point3D(
            (self.p1.x + self.p2.x + self.p3.x) / 3,
            (self.p1.y + self.p2.y + self.p3.y) / 3,
            (self.p1.z + self.p2.z + self.p3.z) / 3,
        )

    @property
    def edges(self):
        return Edge3D(self.p1, self.p2), Edge3D(self.p2, self.p3), Edge3D(self.p3, self.p1)

    def project_to_2d(self, a, zy, yx, xz, xm, ym, zm, ox, oy, indexes=(1, 0, 2)):
        return Triangle2D(
            self.p1.project_to_2d(a, zy, yx, xz, xm, ym, zm, ox, oy, indexes),
            self.p2.project_to_2d(a, zy, yx, xz, xm, ym, zm, ox, oy, indexes),
            self.p3.project_to_2d(a, zy, yx, xz, xm, ym, zm, ox, oy, indexes),
        )

    def point_list(self):
        return [self.p1.to_list(), self.p2.to_list(), self.p3.to_list()]


@dataclass(frozen=True)
class Triangle2D:
    p1: Point2D
    p2: Point2D
    p3: Point2D

    @property
    def midpoint(self):
        return Point2D(
            (self.p1.x + self.p2.x + self.p3.x) / 3,
            (self.p1.y + self.p2.y + self.p3.y) / 3
        )

    @property
    def edges(self):
        return Edge2D(self.p1, self.p2), Edge2D(self.p2, self.p3), Edge2D(self.p3, self.p1)

    def point_list(self):
        return [self.p1.to_list(), self.p2.to_list(), self.p3.to_list()]


@dataclass
class Face3D:
    triangles: list[Triangle3D]

    @property
    def edges(self):
        edges = set()
        for tri in self.triangles:
            edges ^= set(tri.edges)
        return list(edges)

    def project_to_2d(self, a, zy, yx, xz, xm, ym, zm, ox, oy, indexes=(0, 1, 2)):
        return Face2D([tri.project_to_2d(a, zy, yx, xz, xm, ym, zm, ox, oy, indexes) for tri in self.triangles])


@dataclass
class Face2D:
    triangles: list[Triangle2D]

    @property
    def edges(self):
        edges = set()
        for tri in self.triangles:
            edges ^= set(tri.edges)
        return list(edges)


@dataclass
class Mesh:
    faces: list[Face3D]


def itop(p):
    return Point3D(p[0], p[1], p[2])


def itot(tri):
    return Triangle3D(itop(tri[0]), itop(tri[1]), itop(tri[2]))


def itof(face):
    return Face3D([itot(tri) for tri in face])


def itom(mesh):
    return Mesh([itof(face) for face in mesh])
