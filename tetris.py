import pygame as pg
import random
import time
import sys
import pickle
import os
import math
from pygame.locals import *

# Инициализация констант
fps = 25
window_w, window_h = 600, 500
block, cup_h, cup_w = 20, 20, 10

side_freq, down_freq = 0.15, 0.1
side_margin = int((window_w - cup_w * block) / 2)
top_margin = window_h - (cup_h * block) - 5

colors = ((0, 0, 225), (0, 225, 0), (225, 0, 0), (225, 225, 0))
lightcolors = ((30, 30, 255), (50, 255, 50), (255, 30, 30), (255, 255, 30))

white, gray, black = (255, 255, 255), (185, 185, 185), (0, 0, 0)
brd_color, bg_color, txt_color, title_color, info_color = white, black, white, colors[3], colors[0]

# Эффекты
flash_duration = 0.3
last_cleared_lines = []
flash_start_time = 0

# Фигуры
fig_w, fig_h = 5, 5
empty = 'o'

figures = {
    'S': [['ooooo', 'ooooo', 'ooxxo', 'oxxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'ooxxo', 'ooxoo', 'ooooo']],
    'Z': [['ooooo', 'ooooo', 'oxxoo', 'ooxxo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxoo', 'oxooo', 'ooooo']],
    'J': [['ooooo', 'oxooo', 'oxxxo', 'ooooo', 'ooooo'],
          ['ooooo', 'ooxxo', 'ooxoo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxxo', 'oooxo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxoo', 'oxxoo', 'ooooo']],
    'L': [['ooooo', 'oooxo', 'oxxxo', 'ooooo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxoo', 'ooxxo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxxo', 'oxooo', 'ooooo'],
          ['ooooo', 'oxxoo', 'ooxoo', 'ooxoo', 'ooooo']],
    'I': [['ooxoo', 'ooxoo', 'ooxoo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'xxxxo', 'ooooo', 'ooooo']],
    'O': [['ooooo', 'ooooo', 'oxxoo', 'oxxoo', 'ooooo']],
    'T': [['ooooo', 'ooxoo', 'oxxxo', 'ooooo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxxo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxxo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooxoo', 'oxxoo', 'ooxoo', 'ooooo']]
}

fig_stats = {'S': 0, 'Z': 0, 'J': 0, 'L': 0, 'I': 0, 'O': 0, 'T': 0}


def drawFlashEffect():
    if time.time() - flash_start_time < flash_duration:
        flash_intensity = 0.5 + 0.5 * math.sin((time.time() - flash_start_time) * 20)
        for y in last_cleared_lines:
            for x in range(cup_w):
                pixelx, pixely = convertCoords(x, y)
                s = pg.Surface((block, block), pg.SRCALPHA)
                s.fill((255, 255, 255, int(150 * flash_intensity)))
                display_surf.blit(s, (pixelx, pixely))


def save_score(points):
    with open('scores.txt', 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Очки: {points}\n")


def save_highscore(name, score):
    try:
        with open('highscores.dat', 'rb') as f:
            highscores = pickle.load(f)
    except (FileNotFoundError, EOFError):
        highscores = []

    highscores.append((name, score))
    highscores.sort(key=lambda x: x[1], reverse=True)
    highscores = highscores[:10]

    with open('highscores.dat', 'wb') as f:
        pickle.dump(highscores, f)


def show_highscores():
    try:
        with open('highscores.dat', 'rb') as f:
            highscores = pickle.load(f)
    except (FileNotFoundError, EOFError):
        highscores = []

    display_surf.fill(bg_color)

    title = big_font.render('Топ-10 рекордов', True, title_color)
    display_surf.blit(title, (window_w / 2 - title.get_width() / 2, 30))

    if not highscores:
        no_scores = basic_font.render('Рекордов пока нет!', True, txt_color)
        display_surf.blit(no_scores, (window_w / 2 - no_scores.get_width() / 2, 150))
    else:
        for i, (name, score) in enumerate(highscores):
            entry = basic_font.render(f"{i + 1}. {name}: {score}", True, txt_color)
            display_surf.blit(entry, (window_w / 2 - entry.get_width() / 2, 100 + i * 40))

    back = basic_font.render('Нажмите любую клавишу для возврата', True, info_color)
    display_surf.blit(back, (window_w / 2 - back.get_width() / 2, window_h - 50))

    pg.display.update()

    while True:
        for event in pg.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key != K_ESCAPE):
                return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return


def get_player_name(points):
    name = ""
    input_active = True

    while input_active:
        display_surf.fill(bg_color)

        title = big_font.render('Новый рекорд!', True, title_color)
        display_surf.blit(title, (window_w / 2 - title.get_width() / 2, 100))

        score_text = basic_font.render(f'Ваш результат: {points}', True, txt_color)
        display_surf.blit(score_text, (window_w / 2 - score_text.get_width() / 2, 180))

        prompt = basic_font.render('Введите ваше имя:', True, txt_color)
        display_surf.blit(prompt, (window_w / 2 - prompt.get_width() / 2, 250))

        name_surface = basic_font.render(name, True, white)
        pg.draw.rect(display_surf, white, (window_w / 2 - 100, 300, 200, 30), 2)
        display_surf.blit(name_surface, (window_w / 2 - name_surface.get_width() / 2, 305))

        instruction = basic_font.render('Нажмите Enter для сохранения', True, info_color)
        display_surf.blit(instruction, (window_w / 2 - instruction.get_width() / 2, 350))

        pg.display.update()

        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    input_active = False
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 15:
                    name += event.unicode

    return name if name.strip() else "Игрок"


def save_game_state(cup, points, level, fallingFig, nextFig):
    game_state = {
        'cup': cup,
        'points': points,
        'level': level,
        'fallingFig': fallingFig,
        'nextFig': nextFig,
        'timestamp': time.time(),
        'fig_stats': fig_stats
    }
    try:
        with open('tetris_save.dat', 'wb') as f:
            pickle.dump(game_state, f)
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False


def load_game_state():
    try:
        with open('tetris_save.dat', 'rb') as f:
            state = pickle.load(f)
            if time.time() - state['timestamp'] > 86400:  # Сохранение актуально 1 день
                return None
            return state
    except FileNotFoundError:
        return None
    except (EOFError, pickle.PickleError) as e:
        print(f"Ошибка загрузки: {e}")
        return None


def show_pause_screen():
    pause_surface = pg.Surface((window_w, window_h), pg.SRCALPHA)
    pause_surface.fill((0, 0, 0, 150))
    display_surf.blit(pause_surface, (0, 0))

    pause_text = big_font.render('ПАУЗА', True, white)
    pause_rect = pause_text.get_rect(center=(window_w / 2, window_h / 2 - 50))
    display_surf.blit(pause_text, pause_rect)

    continue_text = basic_font.render('Нажмите ПРОБЕЛ чтобы продолжить', True, white)
    continue_rect = continue_text.get_rect(center=(window_w / 2, window_h / 2 + 50))
    display_surf.blit(continue_text, continue_rect)

    pg.display.update()

    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return
                if event.key == K_ESCAPE:
                    pg.quit()
                    sys.exit()


def txtObjects(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def stopGame():
    pg.quit()
    sys.exit()


def checkKeys():
    for event in pg.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showText(text):
    titleSurf, titleRect = txtObjects(text, big_font, title_color)
    titleRect.center = (int(window_w / 2) - 3, int(window_h / 2) - 3)
    display_surf.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = txtObjects('Нажмите любую клавишу для продолжения', basic_font, title_color)
    pressKeyRect.center = (int(window_w / 2), int(window_h / 2) + 100)
    display_surf.blit(pressKeySurf, pressKeyRect)

    while checkKeys() == None:
        pg.display.update()
        fps_clock.tick()


def quitGame():
    # Сохраняем состояние игры перед выходом
    if 'cup' in globals() and 'points' in globals() and 'fallingFig' in globals():
        save_game_state(cup, points, level, fallingFig, nextFig)

    for event in pg.event.get(QUIT):
        stopGame()
    for event in pg.event.get(KEYUP):
        if event.key == K_ESCAPE:
            stopGame()
        pg.event.post(event)


def calcSpeed(points):
    level = int(points / 10) + 1
    fall_speed = 0.27 - (level * 0.02)
    return level, fall_speed


def getNewFig():
    shape = random.choice(list(figures.keys()))
    newFigure = {
        'shape': shape,
        'rotation': random.randint(0, len(figures[shape]) - 1),
        'x': int(cup_w / 2) - int(fig_w / 2),
        'y': -2,
        'color': random.randint(0, len(colors) - 1)
    }
    fig_stats[shape] += 1
    return newFigure


def emptycup():
    cup = []
    for i in range(cup_w):
        cup.append([empty] * cup_h)
    return cup


def addToCup(cup, fig):
    for x in range(fig_w):
        for y in range(fig_h):
            if figures[fig['shape']][fig['rotation']][y][x] != empty:
                cup[x + fig['x']][y + fig['y']] = fig['color']


def incup(x, y):
    return 0 <= x < cup_w and y < cup_h


def checkPos(cup, fig, adjX=0, adjY=0):
    for x in range(fig_w):
        for y in range(fig_h):
            abovecup = y + fig['y'] + adjY < 0
            if abovecup or figures[fig['shape']][fig['rotation']][y][x] == empty:
                continue
            if not incup(x + fig['x'] + adjX, y + fig['y'] + adjY):
                return False
            if cup[x + fig['x'] + adjX][y + fig['y'] + adjY] != empty:
                return False
    return True


def isCompleted(cup, y):
    for x in range(cup_w):
        if cup[x][y] == empty:
            return False
    return True


def clearCompleted(cup):
    global last_cleared_lines, flash_start_time
    removed_lines = 0
    y = cup_h - 1
    last_cleared_lines = []
    while y >= 0:
        if isCompleted(cup, y):
            last_cleared_lines.append(y)
            for pushDownY in range(y, 0, -1):
                for x in range(cup_w):
                    cup[x][pushDownY] = cup[x][pushDownY - 1]
            for x in range(cup_w):
                cup[x][0] = empty
            removed_lines += 1
            flash_start_time = time.time()
        else:
            y -= 1
    return removed_lines


def convertCoords(block_x, block_y):
    return (side_margin + (block_x * block)), (top_margin + (block_y * block))


def drawBlock(block_x, block_y, color, pixelx=None, pixely=None):
    if color == empty:
        return
    if pixelx is None and pixely is None:
        pixelx, pixely = convertCoords(block_x, block_y)
    pg.draw.rect(display_surf, colors[color], (pixelx + 1, pixely + 1, block - 1, block - 1), 0, 3)
    pg.draw.rect(display_surf, lightcolors[color], (pixelx + 1, pixely + 1, block - 4, block - 4), 0, 3)
    pg.draw.circle(display_surf, colors[color], (pixelx + block / 2, pixely + block / 2), 5)


def gamecup(cup):
    pg.draw.rect(display_surf, brd_color, (side_margin - 4, top_margin - 4, (cup_w * block) + 8, (cup_h * block) + 8),
                 5)
    pg.draw.rect(display_surf, bg_color, (side_margin, top_margin, block * cup_w, block * cup_h))
    for x in range(cup_w):
        for y in range(cup_h):
            drawBlock(x, y, cup[x][y])
    drawFlashEffect()


def drawTitle():
    titleSurf = big_font.render('Тетрис Lite', True, title_color)
    titleRect = titleSurf.get_rect()
    titleRect.topleft = (window_w - 425, 30)
    display_surf.blit(titleSurf, titleRect)


def drawInfo(points, level):
    pointsSurf = basic_font.render(f'Баллы: {points}', True, txt_color)
    pointsRect = pointsSurf.get_rect()
    pointsRect.topleft = (window_w - 550, 180)
    display_surf.blit(pointsSurf, pointsRect)

    levelSurf = basic_font.render(f'Уровень: {level}', True, txt_color)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (window_w - 550, 250)
    display_surf.blit(levelSurf, levelRect)

    sorted_stats = sorted(fig_stats.items(), key=lambda x: x[1], reverse=True)
    stats_text = "Чаще: " + ", ".join(f"{shape}:{count}" for shape, count in sorted_stats[:3])
    statsSurf = basic_font.render(stats_text, True, info_color)
    statsRect = statsSurf.get_rect()
    statsRect.topleft = (window_w - 550, 320)
    display_surf.blit(statsSurf, statsRect)

    pausebSurf = basic_font.render('Пауза: пробел', True, info_color)
    pausebRect = pausebSurf.get_rect()
    pausebRect.topleft = (window_w - 550, 420)
    display_surf.blit(pausebSurf, pausebRect)

    escbSurf = basic_font.render('Выход: Esc', True, info_color)
    escbRect = escbSurf.get_rect()
    escbRect.topleft = (window_w - 550, 450)
    display_surf.blit(escbSurf, escbRect)


def drawFig(fig, pixelx=None, pixely=None):
    figToDraw = figures[fig['shape']][fig['rotation']]
    if pixelx is None and pixely is None:
        pixelx, pixely = convertCoords(fig['x'], fig['y'])

    for x in range(fig_w):
        for y in range(fig_h):
            if figToDraw[y][x] != empty:
                drawBlock(None, None, fig['color'], pixelx + (x * block), pixely + (y * block))


def drawnextFig(fig):
    nextSurf = basic_font.render('Следующая:', True, txt_color)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (window_w - 150, 180)
    display_surf.blit(nextSurf, nextRect)
    drawFig(fig, pixelx=window_w - 150, pixely=230)


def runTetris(initial_state=None):
    global fig_stats, cup, points, level, fallingFig, nextFig

    if initial_state is None:
        cup = emptycup()
        points = 0
        level, fall_speed = calcSpeed(points)
        fallingFig = getNewFig()
        nextFig = getNewFig()
        fig_stats = {'S': 0, 'Z': 0, 'J': 0, 'L': 0, 'I': 0, 'O': 0, 'T': 0}
    else:
        cup = initial_state['cup']
        points = initial_state['points']
        level = initial_state['level']
        fall_speed = calcSpeed(points)[1]
        fallingFig = initial_state['fallingFig']
        nextFig = initial_state['nextFig']
        fig_stats = initial_state.get('fig_stats', {'S': 0, 'Z': 0, 'J': 0, 'L': 0, 'I': 0, 'O': 0, 'T': 0})

    last_move_down = time.time()
    last_side_move = time.time()
    last_fall = time.time()
    going_down = False
    going_left = False
    going_right = False
    paused = False

    while True:
        if fallingFig is None:
            fallingFig = nextFig
            nextFig = getNewFig()
            last_fall = time.time()

            if not checkPos(cup, fallingFig):
                save_score(points)
                return False

        quitGame()

        for event in pg.event.get():
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    going_left = False
                elif event.key == K_RIGHT:
                    going_right = False
                elif event.key == K_DOWN:
                    going_down = False

            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    paused = not paused
                    if paused:
                        show_pause_screen()
                        last_fall = time.time()
                        last_move_down = time.time()
                        last_side_move = time.time()
                    continue

                if paused:
                    continue

                if event.key == K_LEFT and checkPos(cup, fallingFig, adjX=-1):
                    fallingFig['x'] -= 1
                    going_left = True
                    going_right = False
                    last_side_move = time.time()

                elif event.key == K_RIGHT and checkPos(cup, fallingFig, adjX=1):
                    fallingFig['x'] += 1
                    going_right = True
                    going_left = False
                    last_side_move = time.time()

                elif event.key == K_UP:
                    fallingFig['rotation'] = (fallingFig['rotation'] + 1) % len(figures[fallingFig['shape']])
                    if not checkPos(cup, fallingFig):
                        fallingFig['rotation'] = (fallingFig['rotation'] - 1) % len(figures[fallingFig['shape']])

                elif event.key == K_DOWN:
                    going_down = True
                    if checkPos(cup, fallingFig, adjY=1):
                        fallingFig['y'] += 1
                    last_move_down = time.time()

                elif event.key == K_RETURN:
                    going_down = False
                    going_left = False
                    going_right = False
                    for i in range(1, cup_h):
                        if not checkPos(cup, fallingFig, adjY=i):
                            break
                    fallingFig['y'] += i - 1

        if paused:
            continue

        if (going_left or going_right) and time.time() - last_side_move > side_freq:
            if going_left and checkPos(cup, fallingFig, adjX=-1):
                fallingFig['x'] -= 1
            elif going_right and checkPos(cup, fallingFig, adjX=1):
                fallingFig['x'] += 1
            last_side_move = time.time()

        if going_down and time.time() - last_move_down > down_freq and checkPos(cup, fallingFig, adjY=1):
            fallingFig['y'] += 1
            last_move_down = time.time()

        if time.time() - last_fall > fall_speed:
            if not checkPos(cup, fallingFig, adjY=1):
                addToCup(cup, fallingFig)
                points += clearCompleted(cup)
                level, fall_speed = calcSpeed(points)
                fallingFig = None
            else:
                fallingFig['y'] += 1
                last_fall = time.time()

        display_surf.fill(bg_color)
        drawTitle()
        gamecup(cup)
        drawInfo(points, level)
        drawnextFig(nextFig)
        if fallingFig is not None:
            drawFig(fallingFig)
        pg.display.update()
        fps_clock.tick(fps)


def show_menu():
    display_surf.fill(bg_color)

    titleSurf = big_font.render('ТЕТРИС', True, title_color)
    titleRect = titleSurf.get_rect(center=(window_w / 2, window_h / 2 - 100))
    display_surf.blit(titleSurf, titleRect)

    option1 = basic_font.render('1. Новая игра', True, txt_color)
    option1_rect = option1.get_rect(center=(window_w / 2, window_h / 2))
    display_surf.blit(option1, option1_rect)

    option2 = basic_font.render('2. Топ 10 игроков', True, txt_color)
    option2_rect = option2.get_rect(center=(window_w / 2, window_h / 2 + 50))
    display_surf.blit(option2, option2_rect)

    pg.display.update()

    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_1:
                    return None  # Новая игра
                elif event.key == K_2:
                    show_highscores()
                    return show_menu()
                elif event.key == K_ESCAPE:
                    pg.quit()
                    sys.exit()


def main():
    global fps_clock, display_surf, basic_font, big_font
    pg.init()
    fps_clock = pg.time.Clock()
    display_surf = pg.display.set_mode((window_w, window_h))
    basic_font = pg.font.SysFont('arial', 20)
    big_font = pg.font.SysFont('verdana', 45)
    pg.display.set_caption('Тетрис Lite')

    # Проверяем наличие сохраненной игры
    saved_game = load_game_state()

    if saved_game is not None:
        # Если есть сохранение, сразу запускаем игру
        game_result = runTetris(saved_game)
    else:
        # Если сохранения нет, показываем меню
        initial_state = show_menu()
        game_result = runTetris(initial_state)

    while True:
        if not game_result:
            showText('Игра закончена')
            try:
                os.remove('tetris_save.dat')
            except FileNotFoundError:
                pass

            # После завершения игры возвращаемся в меню
            initial_state = show_menu()
            game_result = runTetris(initial_state)


if __name__ == '__main__':
    main()