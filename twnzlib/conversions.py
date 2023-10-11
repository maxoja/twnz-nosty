import math


def ndeg_to_rdeg(ndeg: float):
    # convert from Nostale's degree to radiant degree that works with standard cosine theory
    return math.pi - ndeg


