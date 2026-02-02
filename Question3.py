def max_profit(max_trades, daily_prices):
    # Edge cases
    if not daily_prices or max_trades == 0:
        return 0

    n = len(daily_prices)

    # DP table: dp[t][d] = max profit up to day d with at most t transactions
    dp = [[0] * n for _ in range(max_trades + 1)]

    # Build the DP table
    for t in range(1, max_trades + 1):
        max_diff = -daily_prices[0]  # Best value of (dp[t-1][d] - price[d])
        for d in range(1, n):
            # Either do nothing or sell on day d
            dp[t][d] = max(dp[t][d - 1], daily_prices[d] + max_diff)

            # Update max_diff for future days
            max_diff = max(max_diff, dp[t - 1][d] - daily_prices[d])

    return dp[max_trades][n - 1]


def main():
    # Example 1
    max_trades = 2
    daily_prices = [2000, 4000, 1000]

    result = max_profit(max_trades, daily_prices)
    print("Maximum Profit:", result)  # Expected Output: 2000


if __name__ == "__main__":
    main()
