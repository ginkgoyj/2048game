import random
import time
import os


# 棋盘大小固定为 4x4
BOARD_SIZE = 4

# 排行榜文件放在当前程序所在目录里，方便保存和读取
SCORE_FILE = "leaderboard.txt"


def create_board():
    # 创建一个空棋盘，0 表示这个位置没有数字
    board = []
    for i in range(BOARD_SIZE):
        row = []
        for j in range(BOARD_SIZE):
            row.append(0)
        board.append(row)
    return board


def print_welcome():
    # 打印游戏说明，方便直接演示
    print("=" * 50)
    print("欢迎运行 2048")
    print("操作说明：")
    print("  W - 向上移动")
    print("  S - 向下移动")
    print("  A - 向左移动")
    print("  D - 向右移动")
    print("  Q - 退出游戏")
    print("规则说明：")
    print("  相同数字碰到一起会合并成更大的数字")
    print("  生成出 2048 后，可以选择继续玩或者退出")
    print("=" * 50)


def print_leaderboard():
    # 读取排行榜文件并显示历史最高分
    print("\n" + "=" * 50)
    print("排行榜")
    print("=" * 50)

    if not os.path.exists(SCORE_FILE):
        print("暂无历史记录。")
        return

    records = []
    try:
        file = open(SCORE_FILE, "r", encoding="utf-8")
    except OSError:
        print("排行榜文件无法读取。")
        return

    for line in file:
        line = line.strip()
        if line == "":
            continue

        parts = line.split(",", 2)
        if len(parts) < 3:
            continue

        try:
            score = int(parts[1])
        except ValueError:
            continue

        records.append(parts)

    file.close()

    if len(records) == 0:
        print("暂无有效记录。")
        return

    # 按分数从高到低排序，做成简单排行榜
    records.sort(key=lambda x: int(x[1]), reverse=True)

    top_count = 5
    if len(records) < top_count:
        top_count = len(records)

    for i in range(top_count):
        one_record = records[i]
        play_time = one_record[0]
        score = one_record[1]
        print(str(i + 1) + "、" + "分数：" + score + "  时间：" + play_time)


def save_score(score):
    # 把本局得分写入文件，作为排行榜数据
    # 每一局结束后都记录一次，方便之后查看历史成绩
    play_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    line = play_time + "," + str(score) + "," + "本局结束"

    try:
        file = open(SCORE_FILE, "a", encoding="utf-8")
        file.write(line + "\n")
        file.close()
    except OSError:
        print("警告：本局分数无法保存到文件。")


def print_board(board, score, step):
    # 每一步都打印当前分数、步数和棋盘，方便观察游戏过程
    print("\n" + "-" * 50)
    print("当前步数：", step)
    print("当前分数：", score)
    print("-" * 50)

    for i in range(BOARD_SIZE):
        row_text = ""
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                cell = "."
            else:
                cell = str(board[i][j])
            row_text += cell.center(8)
        print(row_text)

    print("-" * 50)


def get_empty_positions(board):
    # 找出所有空位置，后面随机生成新数字时要用
    empty_positions = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                empty_positions.append((i, j))
    return empty_positions


def add_new_number(board):
    # 在空位置中随机加入一个新数字
    # 90% 生成 2，10% 生成 4
    empty_positions = get_empty_positions(board)

    if len(empty_positions) == 0:
        return False

    position = random.choice(empty_positions)
    row = position[0]
    col = position[1]

    if random.random() < 0.9:
        board[row][col] = 2
    else:
        board[row][col] = 4

    return True


def compress_line(line):
    # 把一行中的非 0 数字全部向左靠拢
    new_line = []
    for number in line:
        if number != 0:
            new_line.append(number)

    while len(new_line) < BOARD_SIZE:
        new_line.append(0)

    return new_line


def merge_line(line):
    # 合并相邻且相同的数字
    # 合并后要把分数累加起来
    score_gained = 0
    merged_line = line[:]

    for i in range(BOARD_SIZE - 1):
        if merged_line[i] != 0 and merged_line[i] == merged_line[i + 1]:
            merged_line[i] = merged_line[i] * 2
            merged_line[i + 1] = 0
            score_gained += merged_line[i]

    # 合并以后中间会有 0，所以再压缩一次
    merged_line = compress_line(merged_line)
    return merged_line, score_gained


def move_left(board):
    # 向左移动时，按行处理就可以
    new_board = []
    total_score = 0
    moved = False

    for i in range(BOARD_SIZE):
        original_line = []
        for j in range(BOARD_SIZE):
            original_line.append(board[i][j])

        compressed = compress_line(original_line)
        merged, score_gained = merge_line(compressed)

        if merged != original_line:
            moved = True

        new_board.append(merged)
        total_score += score_gained

    return new_board, moved, total_score


def reverse_line(line):
    # 把一行反过来，向右移动时会用到
    new_line = []
    for i in range(len(line) - 1, -1, -1):
        new_line.append(line[i])
    return new_line


def transpose_board(board):
    # 转置棋盘，行和列互换
    new_board = []
    for i in range(BOARD_SIZE):
        new_row = []
        for j in range(BOARD_SIZE):
            new_row.append(board[j][i])
        new_board.append(new_row)
    return new_board


def move_right(board):
    # 向右移动可以转成：先反转，再按左移动处理，最后再反转回来
    reversed_board = []
    for i in range(BOARD_SIZE):
        reversed_board.append(reverse_line(board[i]))

    moved_board, moved, score_gained = move_left(reversed_board)

    final_board = []
    for i in range(BOARD_SIZE):
        final_board.append(reverse_line(moved_board[i]))

    return final_board, moved, score_gained


def move_up(board):
    # 向上移动可以先转置，再按左移动处理，最后再转置回来
    transposed = transpose_board(board)
    moved_board, moved, score_gained = move_left(transposed)
    final_board = transpose_board(moved_board)
    return final_board, moved, score_gained


def move_down(board):
    # 向下移动可以先转置，再按右移动处理，最后再转置回来
    transposed = transpose_board(board)
    moved_board, moved, score_gained = move_right(transposed)
    final_board = transpose_board(moved_board)
    return final_board, moved, score_gained


def has_won(board):
    # 只要棋盘中出现 2048，就认为达成目标
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 2048:
                return True
    return False


def can_move(board):
    # 只要还有空位，就一定可以继续走
    if len(get_empty_positions(board)) > 0:
        return True

    # 如果没有空位，再检查横向有没有可以合并的相同数字
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE - 1):
            if board[i][j] == board[i][j + 1]:
                return True

    # 再检查纵向有没有可以合并的相同数字
    for i in range(BOARD_SIZE - 1):
        for j in range(BOARD_SIZE):
            if board[i][j] == board[i + 1][j]:
                return True

    return False


def handle_move(board, command):
    # 根据输入字符决定调用哪一种移动函数
    if command == "w":
        return move_up(board)
    if command == "s":
        return move_down(board)
    if command == "a":
        return move_left(board)
    if command == "d":
        return move_right(board)
    return None, False, 0


def get_user_command():
    # 负责读取用户输入并检查合法性
    while True:
        try:
            command = input("请输入操作（W/A/S/D，Q 退出）：")
        except EOFError:
            print("\n检测到输入结束，程序退出。")
            return "q"
        except KeyboardInterrupt:
            print("\n检测到手动中断，程序退出。")
            return "q"

        command = command.strip().lower()

        if command == "":
            print("输入不能为空，请重新输入。")
            continue

        if command in ["w", "a", "s", "d", "q"]:
            return command

        print("输入不合法，请输入 W、A、S、D 或 Q。")


def ask_continue_after_win():
    # 当玩家得到 2048 后，询问是否继续游戏
    # 返回 True 表示继续，False 表示退出
    while True:
        try:
            answer = input("你已经生成 2048，是否继续游戏？请输入 Y 继续，N 退出：")
        except EOFError:
            print("\n检测到输入结束，程序退出。")
            return False
        except KeyboardInterrupt:
            print("\n检测到手动中断，程序退出。")
            return False

        answer = answer.strip().lower()

        if answer in ["y", "yes"]:
            return True
        if answer in ["n", "no"]:
            return False

        print("输入不合法，请输入 Y 或 N。")


def main():
    # 主函数负责组织整个游戏流程
    print_welcome()
    print_leaderboard()

    board = create_board()
    score = 0
    step = 0
    reached_2048 = False

    # 游戏开始时先随机生成两个数字
    add_new_number(board)
    add_new_number(board)

    while True:
        print_board(board, score, step)

        # 如果已经得到 2048，只在第一次达到时询问是否继续
        if has_won(board) and not reached_2048:
            reached_2048 = True
            print("恭喜你，已经得到 2048！")
            if not ask_continue_after_win():
                print("游戏已退出。")
                print("你的最终分数是：", score)
                save_score(score)
                break
            print("你选择继续游戏。")

        if not can_move(board):
            print("棋盘已经无法继续移动，游戏结束。")
            print("你的最终分数是：", score)
            save_score(score)
            break

        command = get_user_command()

        if command == "q":
            print("游戏已退出。")
            print("你的最终分数是：", score)
            save_score(score)
            break

        new_board, moved, gained_score = handle_move(board, command)

        # 如果这一步没有改变棋盘，就提示重新输入
        if not moved:
            print("这一步无法移动，棋盘没有变化，请换一个方向。")
            continue

        board = new_board
        score += gained_score
        step += 1

        # 每次成功移动后，随机生成一个新数字
        add_new_number(board)


if __name__ == "__main__":
    main()
