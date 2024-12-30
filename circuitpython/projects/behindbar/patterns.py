import math


def slide(counter, pixel):
    return counter + pixel


def pulse(counter, pixel):
    return counter


def chaos(counter, pixel):
    # Set the parameters for the chaotic map
    a = 1.5
    b = 0.05
    c = 0.15

    # Calculate the chaotic value using the logistic map
    x = math.sin(counter * b + pixel * c)
    chaos_n = a * x * (1 - x)

    # Scale and round the chaotic value to get a color index between 0 and 59
    color_index = int((chaos_n * 60) % 60)

    return color_index
