def bubble_sort(arr):
    """
    冒泡排序（Bubble Sort）实现
    
    基本思想：重复遍历数组，比较相邻元素，若顺序错误则交换；
    每轮遍历后，当前未排序部分的最大元素“冒泡”至末尾；
    当某轮遍历未发生任何交换时，说明数组已完全有序，可提前终止。
    
    时间复杂度：最坏/平均 O(n²)，最好（已有序）O(n)（得益于优化）
    空间复杂度：O(1) —— 原地排序
    稳定性：稳定（相等元素不交换位置）
    
    参数：
        arr (list): 待排序的列表（将被原地修改）
    
    返回：
        list: 排序后的同一列表对象（便于链式调用）
    """
    if not isinstance(arr, list):
        raise TypeError("输入必须是列表")
    
    n = len(arr)
    # 外层循环控制遍历轮数（最多 n-1 轮）
    for i in range(n):
        swapped = False  # 标记本轮是否发生交换（优化：提前终止）
        # 内层循环进行相邻比较；每轮后末尾 i 个元素已就位，故范围为 0 到 n-i-1
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        # 若本轮无交换，说明已有序，提前退出
        if not swapped:
            break
    return arr