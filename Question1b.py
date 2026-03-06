def keyword_segmentation(user_query, marketing_keywords_dictionary):
 
    word_set = set(marketing_keywords_dictionary)
    memo = {}

    def dfs(remaining):
        if remaining in memo:
            return memo[remaining]
        if not remaining:
            return [""]

        results = []
        for i in range(1, len(remaining) + 1):
            prefix = remaining[:i]
            if prefix in word_set:
                sub_results = dfs(remaining[i:])
                for sentence in sub_results:
                    if sentence:
                        results.append(prefix + " " + sentence)
                    else:
                        results.append(prefix)

        memo[remaining] = results
        return results

    return dfs(user_query)


def main():
    # Example 1
    user_query1 = "nepaltrekkingguide"
    dict1 = ["nepal", "trekking", "guide", "nepaltrekking"]
    print("Example 1 Output:")
    print(keyword_segmentation(user_query1, dict1))

    # Example 2
    user_query2 = "visitkathmandunepal"
    dict2 = ["visit", "kathmandu", "nepal", "visitkathmandu", "kathmandunepal"]
    print("\nExample 2 Output:")
    print(keyword_segmentation(user_query2, dict2))

    # Example 3
    user_query3 = "everesthikingtrail"
    dict3 = ["everest", "hiking", "trek"]
    print("\nExample 3 Output:")
    print(keyword_segmentation(user_query3, dict3))


if __name__ == "__main__":
    main()
