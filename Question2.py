class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def build_tree(arr, i=0):
    if i >= len(arr) or arr[i] is None:
        return None
    node = TreeNode(arr[i])
    node.left = build_tree(arr, 2 * i + 1)
    node.right = build_tree(arr, 2 * i + 2)
    return node


def maxPathSum(root):
    max_sum = float('-inf')

    def dfs(node):
        nonlocal max_sum
        if not node:
            return 0

        left = max(0, dfs(node.left))
        right = max(0, dfs(node.right))

        current_sum = node.val + left + right
        max_sum = max(max_sum, current_sum)

        return node.val + max(left, right)

    dfs(root)
    return max_sum


def main():
    # Example 1
    arr1 = [1, 2, 3]
    root1 = build_tree(arr1)
    print("Example 1 Output:", maxPathSum(root1))  # Expected: 6

    # Example 2
    arr2 = [-10, 9, 20, None, None, 15, 7]
    root2 = build_tree(arr2)
    print("Example 2 Output:", maxPathSum(root2))  # Expected: 42


if __name__ == "__main__":
    main()
