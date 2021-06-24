import pygame
import sys
import math
import random

# ******************** 変数／定数 ********************
# =============== COLOR ===============
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FLORALWHITE = (255,250,240)
LIGHTGRAY = (211, 211, 211)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
rc = [204, 238, 238, 243, 243, 248, 249, 239, 239, 239, 239, 239, 95]
gc = [192, 228, 224, 177, 177, 149, 94, 207, 207, 203, 199, 195, 218]
bc = [179, 218, 198, 116, 116, 90, 50, 108, 99, 82, 57, 41, 147]
# =============== SIZE ===============
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 1000
MASU_BLANK_WIDTH = 30
MASU_BLANK_HEIGHT = 330
# =============== DIRECTION ===============
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3
COMMAND_NG = 4
# =============== GAME MANAGE===============
idx = 0
tmr = 0
msg = ""
level = 1
score = 0
high_score = 0
key_di = 0
# =============== MASU ===============
masu_num = 4 * level
masu_size = 160 / level
masu_half_size = int(masu_size/2)
# =============== BOARD ===============
board = []
back = []
for y in range(masu_num):
    board.append([0]*masu_num)
    back.append([0]*masu_num)

    
# ============================================================
#                           DRAW
# ============================================================

# ******************** 文字の描画 ********************
def draw_text(sc, txt, x, y, siz, col):
    fnt = pygame.font.Font(None, siz)
    sur = fnt.render(txt, True, col)
    # 中央揃え
    x = x - sur.get_width()/2
    y = y - sur.get_height()/2
    # 文字表示
    sc.blit(sur, [x, y])


# ******************** ボードの描画 ********************
def draw_board(sc):
    # ボード表示
    for y in range(masu_num):
        for x in range(masu_num):
            X = x * masu_size + MASU_BLANK_WIDTH
            Y = y * masu_size + MASU_BLANK_HEIGHT
            # マス目の値：0
            if board[y][x] == 0:
                pygame.draw.rect(sc, LIGHTGRAY, [X, Y, masu_size, masu_size])
            # マス目の値：0以外
            else:
                index = (int(math.log(board[y][x], 2)) - 1) % 13
                color = (rc[index], gc[index], bc[index])
                # 描画
                pygame.draw.rect(sc, color, [X, Y, masu_size, masu_size])
                draw_text(sc, str(board[y][x]), X+masu_half_size, Y+masu_half_size, 100, WHITE)
            # 描画：枠線
            pygame.draw.rect(sc, GRAY, [X, Y, masu_size, masu_size], 5)

    if tmr%50 < 40:
        draw_text(sc, msg, SCREEN_WIDTH/2, 230, 50, BLACK)

    # 2048
    draw_text(sc, "2", 50, 80, 100, RED)
    draw_text(sc, "0", 90, 80, 100, GREEN)
    draw_text(sc, "4", 130, 80, 100, ORANGE)
    draw_text(sc, "8", 170, 80, 100, BLUE)
    # SCORE
    pygame.draw.rect(sc, GRAY, [240, 30, 200, 100])
    draw_text(sc, "SCORE", 340, 55, 40, LIGHTGRAY)
    draw_text(sc, str(score), 340, 100, 40, WHITE)
    # HIGH SCORE
    pygame.draw.rect(sc, GRAY, [470, 30, 200, 100])
    draw_text(sc, "HIGH SCORE", 570, 55, 40, LIGHTGRAY)
    draw_text(sc, str(high_score), 570, 100, 40, WHITE)
    # RESTART / UNDO
    draw_text(sc, "RESTART", 120, 300, 50, ORANGE)
    draw_text(sc, "UNDO", 610, 300, 50, ORANGE)


# ============================================================
#                           BOARD
# ============================================================

# 確認：空いたマス目(0)があるか
def board_check():
    for y in range(masu_num):
        for x in range(masu_num):
            if board[y][x] == 0:
                return True
    return False


# ******************** 空いたマス -> 2のランダム配置 ********************
def random_place():
    while True:
        x = random.randint(0, masu_num-1)
        y = random.randint(0, masu_num-1)
        if board[y][x] == 0:
            board[y][x] = 2
            break


# ******************** 上下左右(↑:w ↓:s ←:a →:d)のコマンド入力 ********************
def command_key(key):
    global key_di

    if key[pygame.K_w] == 1:    # 上方向
        key_di = DIR_UP
    elif key[pygame.K_s] == 1:  # 下方向
        key_di = DIR_DOWN
    elif key[pygame.K_a] == 1:  # 左方向
        key_di = DIR_LEFT
    elif key[pygame.K_d] == 1:  # 右方向
        key_di = DIR_RIGHT
    else:                       # NG方向
        key_di = COMMAND_NG


# ******************** 数字をコマンド方向にスライドさせる(スライドが可能かの確認を含む) ********************
def slide():
    # 確認：1回以上、数字を動かせたか or 数字を合算することができるか(同じ数字が動かす方向に並んでいる)
    command_ok = False
    
    while True:
        # 移動させた回数
        move_count = 0

        # 上方向 ／ 下方向
        if key_di == DIR_UP or key_di == DIR_DOWN:
            for y in range(masu_num - 1):
                for x in range(masu_num):
                    
                    # 上方向
                    if key_di == DIR_UP:
                        # 数字が動かせる場合(数字を動かす先が0)
                        if board[y][x] == 0 and board[y+1][x] != 0:
                            board[y][x] = board[y+1][x]
                            board[y+1][x] = 0
                            move_count += 1
                            command_ok = True
                        # 0以外で数字が並ぶ場合 -> 動かせないが[same_num_check()]で合算できるため、コマンドOK
                        elif board[y][x] == board[y+1][x] and board[y][x] != 0:
                            command_ok = True
                    # 下方向
                    elif key_di == DIR_DOWN:
                        # 数字が動かせる場合(数字を動かす先が0)
                        if board[(masu_num-1)-y][x] == 0 and board[(masu_num-2)-y][x] != 0:
                            board[(masu_num-1)-y][x] = board[(masu_num-2)-y][x]
                            board[(masu_num-2)-y][x] = 0
                            move_count += 1
                            command_ok = True
                        # 0以外で数字が並ぶ場合 -> 動かせないが[same_num_check()]で合算できるため、コマンドOK
                        elif board[(masu_num-1)-y][x] == board[(masu_num-2)-y][x] and board[(masu_num-1)-y][x] != 0:
                            command_ok = True
        
        # 左方向 ／ 右方向
        if key_di == DIR_LEFT or key_di == DIR_RIGHT:
            for x in range(masu_num - 1):
                for y in range(masu_num):

                    # 左方向
                    if key_di == DIR_LEFT:
                        # 数字が動かせる場合(数字を動かす先が0)
                        if board[y][x] == 0 and board[y][x+1] != 0:
                            board[y][x] = board[y][x+1]
                            board[y][x+1] = 0
                            move_count += 1
                            command_ok = True
                        # 0以外で数字が並ぶ場合 -> 動かせないが[same_num_check()]で合算できるため、コマンドOK
                        elif board[y][x] == board[y][x+1] and board[y][x] != 0:
                            command_ok = True
                    # 右方向
                    if key_di == DIR_RIGHT:
                        # 数字が動かせる場合(数字を動かす先が0)
                        if board[y][(masu_num-1)-x] == 0 and board[y][(masu_num-2)-x] != 0:
                            board[y][(masu_num-1)-x] = board[y][(masu_num-2)-x]
                            board[y][(masu_num-2)-x] = 0
                            move_count += 1
                            command_ok = True
                        # 0以外で数字が並ぶ場合 -> 動かせないが[same_num_check()]で合算できるため、コマンドOK
                        elif board[y][(masu_num-1)-x] == board[y][(masu_num-2)-x] and board[y][(masu_num-1)-x] != 0:
                            command_ok = True
        # 一度も動かさなくなったら、ループを抜ける        
        if move_count == 0:
            break

    return command_ok


# ******************** スライド方向に同じ数字が並ぶ場合は数字を合算する ********************
def same_num_check():
    global score, high_score
    
    # 上方向 ／ 下方向
    if key_di == DIR_UP or key_di == DIR_DOWN:
        for y in range(masu_num - 1):
            for x in range(masu_num):

                # 上方向
                if key_di == DIR_UP:
                    if board[y][x] == board[y+1][x] and board[y][x] != 0:
                        board[y][x] *= 2
                        board[y+1][x] = 0
                        score += board[y][x]
                # 下方向
                if key_di == DIR_DOWN:
                    if board[(masu_num-1)-y][x] == board[(masu_num-2)-y][x] and board[(masu_num-1)-y][x] != 0:
                        board[(masu_num-1)-y][x] *= 2
                        board[(masu_num-2)-y][x] = 0
                        score += board[(masu_num-1)-y][x]

    # 左方向 ／ 右方向
    if key_di == DIR_LEFT or key_di == DIR_RIGHT:
        for x in range(masu_num-1):
            for y in range(masu_num):

                # 左方向
                if key_di == DIR_LEFT:
                    if board[y][x] == board[y][x+1] and board[y][x] != 0:
                        board[y][x] *= 2
                        board[y][x+1] = 0
                        score += board[y][x]
                # 右方向
                if key_di == DIR_RIGHT:
                    if board[y][(masu_num-1)-x] == board[y][(masu_num-2)-x] and board[y][(masu_num-1)-x] != 0:
                        board[y][(masu_num-1)-x] *= 2
                        board[y][(masu_num-2)-x] = 0
                        score += board[y][(masu_num-1)-x]


# ============================================================
#                           GAME
# ============================================================

# ******************** ゲームのリスタート ********************
def game_restart():
    global score

    # スコアの初期化
    score = 0
    # ボードの初期化
    for y in range(masu_num):
        for x in range(masu_num):
            board[y][x] = 0
            back[y][x] = 0
    

# ******************** 1つ前のボードに戻るためのボードのセーブ ********************
def save():
    for y in range(masu_num):
        for x in range(masu_num):
            back[y][x] = board[y][x]


# ******************** 1つ前のボードに戻すためにボードをロード ********************
def load():
    for y in range(masu_num):
        for x in range(masu_num):
            board[y][x] = back[y][x]


# ******************** リスタート／戻る ********************
def restart_undo(mx, my):
    global idx, tmr
    
    # RESTART
    if (30 <= mx <= 210) and (280 <= my <= 320):
        game_restart()
        idx = 1
        tmr = 0
    # UNDO
    elif (550 <= mx <= 670) and (280 <= my <= 320):
        load()


# ******************** ゲームの終了判定 ********************
def game_set():
    # ランダムに数字を置けなくなった(空きのマスがない)場合は、ゲーム終了
    for y in range(masu_num):
        for x in range(masu_num):
            if board[y][x] == 0:
                return False
    return True


# ============================================================
#                           MAIN
# ============================================================
    
# ******************** メインループ ********************
def main():
    global idx, tmr, msg, high_score
    global level, masu_num, masu_size, masu_half_size
    
    pygame.init()
    pygame.display.set_caption("2048")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    tmr = 0

    while True:
        tmr = tmr + 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # スクリーン
        screen.fill(FLORALWHITE)
        # キー入力
        key = pygame.key.get_pressed()
        # マウスのクリック
        mBtn_1, mBtn_2, mBtn_3 = pygame.mouse.get_pressed()
        click = mBtn_1
        # マウスのx,y座標
        mouseX, mouseY = pygame.mouse.get_pos()

        # タイトル
        if idx == 0:
            msg = "select level ...    [1]:4x4   [2]:8x8"
            if key[pygame.K_1] == 1:
                level = 1
                idx = 1
                tmr = 0
            elif key[pygame.K_2] == 1:
                level = 2
                idx = 1
                tmr = 0

        # プレイヤープレイ中
        elif idx == 1:
            msg = "W - UP  S - DOWN  A - LEFT  D - RIGHT"
            # 最初に、ランダムに「2」を配置
            if tmr == 1:
                random_place()
                
            # コマンド入力を受け付ける
            elif tmr > 10:
                command_key(key)
                
                if key_di != COMMAND_NG:    # 適正なコマンド入力が得られた場合
                    save()                  # スライド前のボードを保存
                    
                    if slide() == True:     # 確認：コマンド方向にスライドが可能か
                        same_num_check()    # 数字の合算を行う
                        slide()             # 数字の合算を行った場合を考慮して、もう一度スライド
                        idx = 2
                        tmr = 0
        
        # ゲームの終了判定
        elif idx == 2:
            # ゲーム終了へ
            if game_set() == True:
                idx == 3
            # ゲーム続行
            else:
                idx = 1
                tmr = 0

        # ゲーム終了
        elif idx == 3:
            msg = "GAME OVER!"
            if tmr == 120:
                idx = 0
                tmr = 0

        # RESTART or UNDO
        if click == True:
            restart_undo(mouseX, mouseY)

        # ハイスコアの更新判定
        if high_score < score:
            high_score = score

        # ボードの描画
        draw_board(screen)

        pygame.display.update()
        clock.tick(30)

if __name__ == '__main__':
    main()
