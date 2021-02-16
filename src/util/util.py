def clamp(val, minimum, maximum):
    return min(maximum, max(minimum, val))

def calculate_angle_diff(a1, a2):
    diff_angle = a1 - a2
    if diff_angle > 180:
        diff_angle = 360 - diff_angle
    return diff_angle