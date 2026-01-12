from collections import defaultdict
from math import gcd


def find_max_collinear_points(locations):
    if len(locations) <= 2:
        return len(locations)

    maximum_count = 0

    for index in range(len(locations)):
        slope_map = defaultdict(int)
        duplicate_points = 1
        base_x, base_y = locations[index]

        for next_index in range(index + 1, len(locations)):
            current_x, current_y = locations[next_index]
            delta_x = current_x - base_x
            delta_y = current_y - base_y

            if delta_x == 0 and delta_y == 0:
                duplicate_points += 1
                continue

            divisor = gcd(delta_x, delta_y)
            delta_x //= divisor
            delta_y //= divisor

            slope_map[(delta_y, delta_x)] += 1

        local_max = duplicate_points
        for value in slope_map.values():
            local_max = max(local_max, value + duplicate_points)

        maximum_count = max(maximum_count, local_max)

    return maximum_count


def main():
    # Example 1
    customer_locations1 = [[1, 1], [2, 2], [3, 3]]
    output1 = find_max_collinear_points(customer_locations1)
    print("Max number of customers covered 2:", output1)

    # Example 2
    customer_locations2 = [[1, 4], [2, 3], [3, 2], [4, 1], [5, 3]]
    output2 = find_max_collinear_points(customer_locations2)
    print("Max number of customers covered 2:", output2)


if __name__ == "__main__":
    main()
