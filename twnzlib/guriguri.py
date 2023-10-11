import math
from conversions import ndeg_to_rdeg


def find_intersection(npoint1, npoint2, map_w, map_h):
    x1, ny1, ndeg1 = npoint1
    x2, ny2, ndeg2 = npoint2

    # map from nostale values to math world
    angle1 = ndeg_to_rdeg(ndeg1)
    angle2 = ndeg_to_rdeg(ndeg2)
    y1 = map_h - ny1
    y2 = map_h - ny2

    # Calculate slopes (m1 and m2) from angles
    m1 = math.tan(angle1)
    m2 = math.tan(angle2)

    # Calculate the intersection point
    if m1 != m2:
        x_intersection = (y2 - y1 + m1 * x1 - m2 * x2) / (m1 - m2)
        y_intersection = m1 * (x_intersection - x1) + y1
        the_x, the_y = x_intersection, map_h - y_intersection
        return int(math.ceil(the_x)), int(math.ceil(the_y))
    else:
        # Lines are parallel, so there's no intersection
        return None


if __name__ == '__main__':
    point1 = (10, 10, -math.pi*4/5)  # (x1, y1, angle1)
    point2 = (10, 70, math.pi*3/5)  # (x2, y2, angle2)

    intersection = find_intersection(point1, point2, 90, 90)

    if intersection:
        print(f"The lines intersect at point (x,y) = ({intersection})")
    else:
        print("The lines are parallel and do not intersect.")