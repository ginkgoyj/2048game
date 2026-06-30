# -*- coding: utf-8 -*-
# 2048 游戏 Python 实现
# 操作说明: w-上, a-左, s-右, z-下, r-重新开始, q-退出
# 注意：题目中规定 's' 表示向右移动，'z' 表示向下移动

import os
import random

# 全局变量：4x4 的地图与玩家得分
map = [[0] * 4 for _ in range(4)]   # 存储每个方格的数字，0 表示空
score = 0                           # 玩家当前得分


def init_game():
    """游戏初始化：清屏、清空地图、重置得分、初始化随机种子"""
    global map, score
    # 清除屏幕（Windows 用 cls，其他系统用 clear）
    os.system("cls" if os.name == "nt" else "clear")
    # 将 4x4 地图全部清零
    for i in range(4):
        for j in range(4):
            map[i][j] = 0
    # 初始化随机种子（Python 默认使用系统时间，这里显式调用一次）
    random.seed()
    # 初始得分为 0
    score = 0


def update():
    """更新屏幕显示，输出当前 4x4 方格内容以及得分和操作说明"""
    # 先清屏，避免上一帧画面残留
    os.system("cls" if os.name == "nt" else "clear")
    print("============ 2048 游戏 ============")
    print("操作: w-上  a-左  s-右  z-下  r-重开  q-退出")
    print("当前得分: {}".format(score))
    print("-----------------------------------")
    # 按行打印方格，0 用 "." 表示，方便观察
    for i in range(4):
        row_str = ""
        for j in range(4):
            if map[i][j] == 0:
                row_str += "{:>6}".format(".")
            else:
                row_str += "{:>6}".format(map[i][j])
        print(row_str)
        print("")   # 每行下方空一行，便于阅读
    print("-----------------------------------")


def check_win():
    """检查是否合并出 2048，胜利返回 True，否则返回 False"""
    for i in range(4):
        for j in range(4):
            if map[i][j] == 2048:
                return True
    return False


def check_lose():
    """检查游戏是否已经无法继续：
       - 如果存在 0 值方格，仍可继续，返回 False
       - 否则检查上下左右相邻是否有相同数字，若有则可合并，返回 False
       - 都不满足则失败，返回 True"""
    # 第一步：查找是否有空方格
    for i in range(4):
        for j in range(4):
            if map[i][j] == 0:
                return False
    # 第二步：检查相邻方格是否相同（横向）
    for i in range(4):
        for j in range(3):
            if map[i][j] == map[i][j + 1]:
                return False
    # 第三步：检查相邻方格是否相同（纵向）
    for i in range(3):
        for j in range(4):
            if map[i][j] == map[i + 1][j]:
                return False
    # 所有方格都满且没有可合并的，玩家失败
    return True


def generate_block():
    """随机在一个空格中生成 2 或 4（按 9:1 的比例）
       成功生成返回 True，棋盘已满返回 False"""
    # 先收集所有空位置
    empty = []
    for i in range(4):
        for j in range(4):
            if map[i][j] == 0:
                empty.append((i, j))
    if len(empty) == 0:
        return False
    # 从空位中随机挑选一个
    i, j = random.choice(empty)
    # 以 9:1 的概率决定生成 2 还是 4
    if random.randint(1, 10) == 1:
        map[i][j] = 4
    else:
        map[i][j] = 2
    return True


def move_left():
    """向左移动并合并：返回 True 表示棋盘发生了变化"""
    global score
    changed = False
    for i in range(4):
        # 取出该行所有非零数字，按原顺序排列
        nums = []
        for j in range(4):
            if map[i][j] != 0:
                nums.append(map[i][j])
        # 合并相邻相同数字（每个数字一回合只能合并一次）
        merged = []
        k = 0
        while k < len(nums):
            if k + 1 < len(nums) and nums[k] == nums[k + 1]:
                # 合并：两个数字相加，得分增加
                merged.append(nums[k] * 2)
                score += nums[k] * 2
                k += 2
            else:
                merged.append(nums[k])
                k += 1
        # 补 0 到长度 4
        while len(merged) < 4:
            merged.append(0)
        # 检查该行是否发生了变化
        for j in range(4):
            if map[i][j] != merged[j]:
                changed = True
            map[i][j] = merged[j]
    return changed


def move_right():
    """向右移动：思路与向左相同，先把行翻转，做左移，再翻回去"""
    global score
    changed = False
    for i in range(4):
        # 把这一行翻转（向右等价于翻转后向左）
        row = map[i][::-1]
        nums = [x for x in row if x != 0]
        merged = []
        k = 0
        while k < len(nums):
            if k + 1 < len(nums) and nums[k] == nums[k + 1]:
                merged.append(nums[k] * 2)
                score += nums[k] * 2
                k += 2
            else:
                merged.append(nums[k])
                k += 1
        while len(merged) < 4:
            merged.append(0)
        # 再翻回原方向，写回地图
        merged.reverse()
        for j in range(4):
            if map[i][j] != merged[j]:
                changed = True
            map[i][j] = merged[j]
    return changed


def move_up():
    """向上移动：按列处理，每列向上压缩并合并"""
    global score
    changed = False
    for j in range(4):
        # 取出该列所有非零数字
        nums = []
        for i in range(4):
            if map[i][j] != 0:
                nums.append(map[i][j])
        # 合并
        merged = []
        k = 0
        while k < len(nums):
            if k + 1 < len(nums) and nums[k] == nums[k + 1]:
                merged.append(nums[k] * 2)
                score += nums[k] * 2
                k += 2
            else:
                merged.append(nums[k])
                k += 1
        while len(merged) < 4:
            merged.append(0)
        # 写回该列
        for i in range(4):
            if map[i][j] != merged[i]:
                changed = True
            map[i][j] = merged[i]
    return changed


def move_down():
    """向下移动：按列翻转后做向上移动"""
    global score
    changed = False
    for j in range(4):
        # 把该列从下到上读出来（等价于翻转）
        nums = []
        for i in range(3, -1, -1):
            if map[i][j] != 0:
                nums.append(map[i][j])
        merged = []
        k = 0
        while k < len(nums):
            if k + 1 < len(nums) and nums[k] == nums[k + 1]:
                merged.append(nums[k] * 2)
                score += nums[k] * 2
                k += 2
            else:
                merged.append(nums[k])
                k += 1
        while len(merged) < 4:
            merged.append(0)
        # 写回时再次翻转，使其从下往上对应
        for idx in range(4):
            i = 3 - idx
            if map[i][j] != merged[idx]:
                changed = True
            map[i][j] = merged[idx]
    return changed


def main():
    """主函数：按照题目算法流程控制游戏循环"""
    # 1. 初始化
    init_game()
    # 2. 开局先生成两个随机方格
    generate_block()
    generate_block()

    # 3. 主循环
    while True:
        # 3.1 更新画面
        update()

        # 3.2 检测胜利
        if check_win():
            print("恭喜！你合并出了 2048，胜利！")
            break

        # 3.3 检测失败
        if check_lose():
            print("游戏失败：棋盘已满且无法移动。最终得分: {}".format(score))
            break

        # 3.4 读取玩家输入，做非法输入处理
        try:
            cmd = input("请输入操作 (w/a/s/z/r/q): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            # 防止 Ctrl+C / Ctrl+D 让程序直接崩溃
            print("\n检测到中断，游戏退出。")
            break

        if cmd == "":
            # 空输入直接忽略
            continue

        # 只取第一个字符，避免一次输入多个字符引起混乱
        cmd = cmd[0]

        moved = False     # 标记本次是否产生有效移动
        if cmd == "w":
            moved = move_up()
        elif cmd == "a":
            moved = move_left()
        elif cmd == "s":
            moved = move_right()
        elif cmd == "z":
            moved = move_down()
        elif cmd == "r":
            # 重新开始：重置后再放两个方格，并跳过本轮后续流程
            init_game()
            generate_block()
            generate_block()
            continue
        elif cmd == "q":
            print("玩家选择退出，最终得分: {}".format(score))
            break
        else:
            # 非法输入：提示并继续
            print("非法输入，请重新输入！")
            # 加一个简单的暂停，避免提示一闪而过
            input("按回车继续...")
            continue

        # 只有产生了有效移动才生成新方格
        if moved:
            generate_block()
        # 没移动则不生成新块，玩家可以再次尝试


# 程序入口
if __name__ == "__main__":
    main()
