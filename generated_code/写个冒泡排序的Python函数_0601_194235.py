def bubble_sort(arr):
    """
    冒泡排序（Bubble Sort）——简洁、直观的入门级排序算法
    
    原理（依据搜索结果总结）：
    - 比较相邻元素，若前一个 > 后一个（升序），则交换；
    - 每轮遍历将当前未排序部分的最大值“冒泡”到末尾；
    - 经过 n-1 轮后，整个数组有序（第 n 轮仅剩 1 个元素，无需比较）；
    - 最优情况（已有序）：仅需 1 次遍历，时间复杂度 O(n)；
    - 最坏/平均情况：O(n²)；空间复杂度：O(1)（原地排序）。
    
    参考来源：2025-07-21、2025-07-28、2026-02-26 等多条权威描述
    """
    if not isinstance(arr, list):
        raise TypeError("输入必须为列表")
    
    # 创建新列表，避免修改原列表
    result = arr.copy()
    n = len(result)
    # 外层循环控制轮数：最多 n-1 轮
    for i in range(n - 1):
        # 标志位：检测本轮是否发生交换（用于优化）
        swapped = False
        # 内层循环进行相邻比较，每轮后边界收缩 1 位（因末尾已有序）
        for j in range(n - 1 - i):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        # 若本趟无交换，说明已完全有序，提前终止（呼应 2026-01-07 “没有需要交换时即完成”）
        if not swapped:
            break
    return result