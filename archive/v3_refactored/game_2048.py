import random


# 棋盘的边长固定为 4，对应标准 2048 游戏
BOARD_SIZE = 4


def create_board():
    # 创建一个 4x4 的棋盘，初始时全部填 0，0 表示这个位置为空
    board = []
    for i in range(BOARD_SIZE):
        row = []
        for j in range(BOARD_SIZE):
            row.append(0)
        board.append(row)
    return board


def print_welcome():
    # 打印游戏说明，方便演示时直接看到操作方式
    print("=" * 50)
    print("欢迎运行 2048")
    print("操作说明：")
    print("  W - 向上移动")
    print("  S - 向下移动")
    print("  A - 向左移动")
    print("  D - 向右移动")
    print("  Q - 退出游戏")
    print("合并相同数字可以得到更大的数字，目标是得到 2048。")
    print("=" * 50)


def print_board(board, score, step):
    # 每一步都把当前分数、步数和棋盘打印出来，方便观察游戏过程
    print("\n" + "-" * 50)
    print("当前步数：", step)
    print("当前分数：", score)
    print("-" * 50)

    # 用循环逐行打印棋盘，空位显示为 .
    for i in range(BOARD_SIZE):
        row_text = ""
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                cell = "."
            else:
                cell = str(board[i][j])

            # 调整显示宽度，让棋盘更整齐
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
    # 按照常见规则，大多数情况生成 2，少数情况生成 4
    empty_positions = get_empty_positions(board)

    # 如果没有空位置，就不能再放新数字了
    if len(empty_positions) == 0:
        return False

    position = random.choice(empty_positions)
    row = position[0]
    col = position[1]

    random_number = random.random()
    if random_number < 0.9:
        board[row][col] = 2
    else:
        board[row][col] = 4

    return True


def compress_line(line):
    # 这一部分负责把一行中的非 0 数字向左靠拢
    # 例如 [2, 0, 2, 4] 会先变成 [2, 2, 4, 0]
    new_line = []

    for number in line:
        if number != 0:
            new_line.append(number)

    while len(new_line) < BOARD_SIZE:
        new_line.append(0)

    return new_line


def merge_line(line):
    # 这一部分负责把已经靠拢后的相邻相同数字进行合并
    # 合并后要把分数增加，并且被合并过的位置跳过一次
    score_gained = 0
    merged_line = line[:]

    for i in range(BOARD_SIZE - 1):
        if merged_line[i] != 0 and merged_line[i] == merged_line[i + 1]:
            merged_line[i] = merged_line[i] * 2
            merged_line[i + 1] = 0
            score_gained += merged_line[i]

    # 合并后中间会出现 0，还要再压缩一次
    merged_line = compress_line(merged_line)
    return merged_line, score_gained


def move_left(board):
    # 向左移动时，逐行处理即可
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
    # 反转一行，向右移动时会用到
    new_line = []
    for i in range(len(line) - 1, -1, -1):
        new_line.append(line[i])
    return new_line


def transpose_board(board):
    # 转置棋盘，把行列交换
    # 这样就可以把上下移动转换成左右移动，减少重复代码
    new_board = []
    for i in range(BOARD_SIZE):
        new_row = []
        for j in range(BOARD_SIZE):
            new_row.append(board[j][i])
        new_board.append(new_row)
    return new_board


def move_right(board):
    # 向右移动可以看成：先反转，再按左移动处理，最后再反转回来
    reversed_board = []
    for i in range(BOARD_SIZE):
        reversed_board.append(reverse_line(board[i]))

    moved_board, moved, score_gained = move_left(reversed_board)

    final_board = []
    for i in range(BOARD_SIZE):
        final_board.append(reverse_line(moved_board[i]))

    return final_board, moved, score_gained


def move_up(board):
    # 向上移动可以转置后按左移动处理，再转置回来
    transposed = transpose_board(board)
    moved_board, moved, score_gained = move_left(transposed)
    final_board = transpose_board(moved_board)
    return final_board, moved, score_gained


def move_down(board):
    # 向下移动可以转置后按右移动处理，再转置回来
    transposed = transpose_board(board)
    moved_board, moved, score_gained = move_right(transposed)
    final_board = transpose_board(moved_board)
    return final_board, moved, score_gained


def has_won(board):
    # 只要棋盘中出现 2048，就算胜利
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 2048:
                return True
    return False


def can_move(board):
    # 先判断是否还有空位，只要有空位就还能继续
    if len(get_empty_positions(board)) > 0:
        return True

    # 如果没有空位，再检查横向是否还能合并
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE - 1):
            if board[i][j] == board[i][j + 1]:
                return True

    # 再检查纵向是否还能合并
    for i in range(BOARD_SIZE - 1):
        for j in range(BOARD_SIZE):
            if board[i][j] == board[i + 1][j]:
                return True

    # 既没有空位，也不能合并，说明游戏结束
    return False


def handle_move(board, command):
    # 根据用户输入决定调用哪一种移动函数
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
    # 负责读取并检查输入，避免用户输入错误后程序直接报错
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


def main():
    # 主函数负责组织整个游戏流程
    print_welcome()

    board = create_board()
    score = 0
    step = 0

    # 游戏开始时先随机生成两个数字
    add_new_number(board)
    add_new_number(board)

    while True:
        print_board(board, score, step)

        if has_won(board):
            print("恭喜你，已经得到 2048，可以继续挑战更高分。")

        if not can_move(board):
            print("棋盘已经无法继续移动，游戏结束。")
            print("你的最终分数是：", score)
            break

        command = get_user_command()

        if command == "q":
            print("游戏已退出。")
            print("你的最终分数是：", score)
            break

        new_board, moved, gained_score = handle_move(board, command)

        # 如果本次移动没有让棋盘发生变化，就提示用户重新输入
        if not moved:
            print("这一步无法移动，棋盘没有变化，请换一个方向。")
            continue

        board = new_board
        score += gained_score
        step += 1

        # 每次成功移动后，才会在空位置随机生成一个新数字
        add_new_number(board)


if __name__ == "__main__":
    main()
