import math
from twnz import *

if __name__ == '__main__':
    # Example usage:
    point1 = (10, 10, -math.pi*4/5)  # (x1, y1, angle1)
    point2 = (10, 70, math.pi*3/5)  # (x2, y2, angle2)

    intersection = find_intersection(point1, point2)

    if intersection:
        print(f"The lines intersect at point (x,y) = ({intersection})")
    else:
        print("The lines are parallel and do not intersect.")