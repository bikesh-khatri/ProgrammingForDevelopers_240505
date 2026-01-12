from collections import defaultdict
from math import gcd

def max_customers_on_line(customer_locations):
    if len(customer_locations) <= 2:
        return len(customer_locations)

    max_points = 0

    for i in range(len(customer_locations)):
        slopes = defaultdict(int)
        same_point = 1
        x1, y1 = customer_locations[i]

        for j in range(i + 1, len(customer_locations)):
            x2, y2 = customer_locations[j]
            dx = x2 - x1
            dy = y2 - y1

            if dx == 0 and dy == 0:
                same_point += 1
                continue

            g = gcd(dx, dy)
            dx //= g
            dy //= g

            slopes[(dy, dx)] += 1

        current_max = same_point
        for count in slopes.values():
            current_max = max(current_max, count + same_point)

        max_points = max(max_points, current_max)

    return max_points



def main():
    # Example 1
    customer_locations1 = [[1, 1], [2, 2], [3, 3]]
    result1 = max_customers_on_line(customer_locations1)
    print("Max number of customers covered 2:", result1)

    # Example 2
    customer_locations2 = [[1,4], [2,3], [3,2], [4,1], [5,3]]
    result2 = max_customers_on_line(customer_locations2)
    print("Max number of customers covered 2:", result2)


if __name__ == "__main__":
    main()