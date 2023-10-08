import math


def nostale_deg_to_rad_deg(nostale_deg):
    return math.pi - nostale_deg


def find_intersection(point1, point2):
    x1, y1, angle1 = point1
    x2, y2, angle2 = point2

    # map from nostale values to math world
    map_h = 100
    angle1 = nostale_deg_to_rad_deg(angle1)
    angle2 = nostale_deg_to_rad_deg(angle2)
    y1 = map_h - y1
    y2 = map_h - y2

    # Calculate slopes (m1 and m2) from angles
    m1 = math.tan(angle1)
    m2 = math.tan(angle2)

    # Calculate the intersection point
    if m1 != m2:
        x_intersection = (y2 - y1 + m1 * x1 - m2 * x2) / (m1 - m2)
        y_intersection = m1 * (x_intersection - x1) + y1
        intersection = x_intersection, map_h - y_intersection
        the_x, the_y = intersection
        the_x = int(math.ceil(the_x))
        the_y = int(math.ceil(the_y))
        return the_x, the_y
    else:
        # Lines are parallel, so there's no intersection
        return None

