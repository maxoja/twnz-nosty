import math

import numpy as np

from twnz.conversions import ndeg_to_rdeg


def find_intersection_xy(npoint1, npoint2, map_h):
    y1, x1, ndeg1 = npoint1
    y2, x2, ndeg2 = npoint2

    # translate to y that works with this algo
    y1 = map_h - y1
    y2 = map_h - y2

    # map from nostale values to math world
    angle1 = ndeg_to_rdeg(ndeg1)
    angle2 = ndeg_to_rdeg(ndeg2)
    # Calculate slopes (m1 and m2) from angles
    m1 = math.tan(angle1)
    m2 = math.tan(angle2)

    # Calculate the intersection point
    if m1 != m2:
        x_intersection = (y2 - y1 + m1 * x1 - m2 * x2) / (m1 - m2)
        y_intersection = m1 * (x_intersection - x1) + y1
        # convert y back to normal y
        the_y, the_x = map_h - y_intersection, x_intersection
        return int(math.ceil(the_y)), int(math.ceil(the_x))
    else:
        # Lines are parallel, so there's no intersection
        return None


if __name__ == '__main__':
    point1 = (10, 10, -math.pi*4/5)  # (y1, x1, angle1)
    point2 = (70, 10, math.pi*3/5)  # (y2, x2, angle2)

    intersection = find_intersection_xy(point1, point2, 100)

    if intersection:
        print(f"The lines intersect at point (x,y) = {intersection}")
    else:
        print("The lines are parallel and do not intersect.")