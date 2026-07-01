# -*- coding: utf-8 -*-
# 2048 游戏 Python 实现
# 操作说明: w-上, a-左, s-右, z-下, r-重新开始, q-退出
# 注意：题目中规定 's' 表示向右移动，'z' 表示向下移动

import os
import random
import time

# 全局变量：4x4 的地图与玩家得分
map = [[0] * 4 for _ in range(4)]   # 存储每个方格的数字，0 表示空
score = 0                           # 玩家当前得分

# 排行榜文件路径：与本程序同目录下的 scores.txt
# 用 __file__ 计算路径，避免在不同目录下运行时找不到文件
SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores.txt")

# 标记本局是否已经达到过 2048，避免每一步都重复询问玩家是否继续
reached_2048 = False


def init_game():
    """游戏初始化：清屏、清空地图、重置得分、初始化随机种子"""
    global map, score, reached_2048
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
    # 重置"是否已达到 2048"标记，避免上局状态影响新局
    reached_2048 = False


def save_score(player_name, final_score):
    """将玩家本次的得分追加写入排行榜文件
       文件格式：每行一条记录，"姓名,得分,时间" """
    try:
        # 用追加模式打开文件，不存在会自动创建
        with open(SCORE_FILE, "a", encoding="utf-8") as f:
            # 记录当前时间，方便查看
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            f.write("{},{},{}\n".format(player_name, final_score, now))
    except Exception as e:
        # 写文件失败时只提示，不让程序崩溃
        print("保存得分失败: {}".format(e))


def show_leaderboard():
    """读取排行榜文件并按得分从高到低显示前 10 名"""
    if not os.path.exists(SCORE_FILE):
        print("暂无排行榜记录。")
        return
    records = []
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                # 按逗号拆分：姓名,得分,时间
                parts = line.split(",")
                if len(parts) < 3:
                    # 格式不符合的行直接跳过，避免坏数据导致崩溃
                    continue
                name = parts[0]
                # 得分需要转为整数，转换失败的行跳过
                try:
                    sc = int(parts[1])
                except ValueError:
                    continue
                t = parts[2]
                records.append((name, sc, t))
    except Exception as e:
        print("读取排行榜失败: {}".format(e))
        return

    if len(records) == 0:
        print("暂无排行榜记录。")
        return

    # 按得分从高到低排序
    records.sort(key=lambda x: x[1], reverse=True)

    print("============ 排行榜 (前 10) ============")
    print("{:<4}{:<12}{:<8}{}".format("排名", "玩家", "得分", "时间"))
    # 只显示前 10 条记录
    for idx, rec in enumerate(records[:10]):
        print("{:<4}{:<12}{:<8}{}".format(idx + 1, rec[0], rec[1], rec[2]))
    print("=========================================")


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
    global reached_2048

    # 程序启动时先展示一次历史排行榜
    show_leaderboard()
    # 让玩家输入姓名，便于记录排行榜
    try:
        player_name = input("请输入玩家姓名 (回车默认 player): ").strip()
    except (EOFError, KeyboardInterrupt):
        player_name = ""
    if player_name == "":
        player_name = "player"
    # 姓名中不能含有逗号，否则会破坏 csv 格式，统一替换掉
    player_name = player_name.replace(",", "_")

    # 1. 初始化
    init_game()
    # 2. 开局先生成两个随机方格
    generate_block()
    generate_block()

    # 用于标识游戏结束的原因，最后保存到排行榜里
    end_reason = "结束"

    # 3. 主循环
    while True:
        # 3.1 更新画面
        update()

        # 3.2 检测胜利：仅在第一次达到 2048 时询问玩家是否继续
        if check_win() and not reached_2048:
            reached_2048 = True
            print("恭喜！你合并出了 2048！")
            # 询问玩家是否继续，直到输入合法
            while True:
                try:
                    choice = input("是否继续游戏？(y 继续 / n 退出): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    choice = "n"
                if choice == "y":
                    print("继续游戏，挑战更高分！")
                    break
                elif choice == "n":
                    end_reason = "胜利退出"
                    print("玩家选择退出，最终得分: {}".format(score))
                    save_score(player_name, score)
                    show_leaderboard()
                    return
                else:
                    print("非法输入，请输入 y 或 n。")

        # 3.3 检测失败
        if check_lose():
            end_reason = "失败"
            print("游戏失败：棋盘已满且无法移动。最终得分: {}".format(score))
            save_score(player_name, score)
            show_leaderboard()
            return

        # 3.4 读取玩家输入，做非法输入处理
        try:
            cmd = input("请输入操作 (w/a/s/z/r/q): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            # 防止 Ctrl+C / Ctrl+D 让程序直接崩溃
            print("\n检测到中断，游戏退出。")
            # 中断时也把当前得分保存进排行榜
            save_score(player_name, score)
            show_leaderboard()
            return

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
            # 退出时保存得分并显示排行榜
            save_score(player_name, score)
            show_leaderboard()
            return
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
