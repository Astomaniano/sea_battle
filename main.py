import pygame
import random

# Инициализация pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
GRID_SIZE = 10
CELL_SIZE = 30
SHIP_SIZES = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1] #  размеры кораблей

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Инициализация экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Морской бой")

# Игровое поле
player_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
computer_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def draw_grids(player_grid, computer_grid):
    # Рисуем сетку для поля игрока
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(30 + x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)
    draw_ships(player_grid, (30, 0))  # Координаты смещения для поля игрока
    draw_shots(player_grid, (30, 0))  # Координаты смещения для поля игрока

    # Рисуем сетку для поля компьютера
    offset_x = SCREEN_WIDTH // 2  # Смещение для поля компьютера по горизонтали
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(offset_x + x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)
    draw_shots(computer_grid, (offset_x, 0))  # Координаты смещения для поля компьютера
def check_ship_placement(grid, x, y, size, orientation):
    # Проверяем, можно ли разместить корабль в данной позиции
    if orientation == 'horizontal' and x + size > GRID_SIZE:
        return False  # Корабль выходит за правую границу поля
    if orientation == 'vertical' and y + size > GRID_SIZE:
        return False  # Корабль выходит за нижнюю границу поля

    for i in range(-1, size + (1 if orientation == 'horizontal' else 2)):
        for j in range(-1, 2 if orientation == 'horizontal' else size + 1):
            x_index = x + (i if orientation == 'horizontal' else j)
            y_index = y + (j if orientation == 'horizontal' else i)
            if 0 <= x_index < GRID_SIZE and 0 <= y_index < GRID_SIZE:
                if grid[y_index][x_index] == 1:
                    return False  # Соприкосновение с другим кораблем
    return True

def place_ships_randomly(grid, ship_sizes):
    sorted_ship_sizes = sorted(ship_sizes, reverse=True)  # Сортируем корабли по убыванию
    while sorted_ship_sizes:
        size = sorted_ship_sizes.pop(0)  # Берем самый большой корабль
        placed = False
        attempts = 0
        max_attempts = 1000
        while not placed:
            attempts += 1
            if attempts > max_attempts:
                # Если не удаётся разместить корабль, сбрасываем поле и начинаем заново
                print(f"Перезапуск размещения кораблей. Не удалось разместить корабль размером {size}.")
                grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                sorted_ship_sizes = sorted(ship_sizes, reverse=True)  # Снова сортируем корабли
                break  # Выходим из текущего цикла, начинаем размещение заново
            orientation = random.choice(['horizontal', 'vertical'])
            x = random.randint(0, GRID_SIZE - (size if orientation == 'horizontal' else 1))
            y = random.randint(0, GRID_SIZE - (size if orientation == 'vertical' else 1))
            if check_ship_placement(grid, x, y, size, orientation):
                if orientation == 'horizontal':
                    for i in range(size):
                        grid[y][x + i] = 1
                else:  # vertical
                    for i in range(size):
                        grid[y + i][x] = 1
                placed = True

def draw_ships(grid, offset):
    offset_x, offset_y = offset
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] == 1:
                top_left_x = offset_x + x * CELL_SIZE
                top_left_y = offset_y + y * CELL_SIZE
                ship_rect = pygame.Rect(top_left_x, top_left_y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GRAY, ship_rect)

def draw_shots(grid, offset):
    offset_x, offset_y = offset
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            center_x = offset_x + x * CELL_SIZE + CELL_SIZE // 2
            center_y = offset_y + y * CELL_SIZE + CELL_SIZE // 2
            if grid[y][x] == 2:  # Попадание
                pygame.draw.circle(screen, RED, (center_x, center_y), CELL_SIZE // 4)
            elif grid[y][x] == 3:  # Промах
                pygame.draw.circle(screen, WHITE, (center_x, center_y), CELL_SIZE // 4)

def get_grid_position(mouse_pos):
    x, y = mouse_pos
    grid_x = x // CELL_SIZE
    grid_y = y // CELL_SIZE
    return grid_x, grid_y

def make_shot(grid, x, y):
    # Проверяем, что выстрел попадает в пределы поля
    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
        if grid[y][x] == 1:  # Попадание в корабль
            grid[y][x] = 2  # Маркируем попадание
            return True
        elif grid[y][x] == 0:  # Промах
            grid[y][x] = 3  # Маркируем промах
    return False


def computer_turn(grid, shots):
    hit = False
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if (x, y) not in shots:  # Проверяем, что по этим координатам еще не стреляли
            shots.add((x, y))  # Добавляем координаты в список сделанных выстрелов
            hit = make_shot(grid, x, y)
            if not hit:
                break  # Промах - компьютер заканчивает стрельбу
    return hit

def mark_destroyed_ship(grid, x, y):
    # Эта функция должна вызываться, когда корабль уничтожен
    # Отмечаем клетки вокруг уничтоженного корабля
    for i in range(x-1, x+2):
        for j in range(y-1, y+2):
            if 0 <= i < GRID_SIZE and 0 <= j < GRID_SIZE and grid[j][i] == 0:
                grid[j][i] = 3  # Маркируем клетку как проверенную

def count_hit_ships(grid):
    return sum(cell == 2 for row in grid for cell in row)

def check_victory(grid):
    total_ship_cells = sum(SHIP_SIZES)  # Общее количество клеток, занимаемых кораблями
    hit_cells = count_hit_ships(grid)
    return hit_cells == total_ship_cells

def draw_text(surface, text, color, font, size, x, y):
    font = pygame.font.Font(font, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def draw_button(surface, text, text_color, button_color, font, size, x, y, width, height):
    font = pygame.font.Font(font, size)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()
    button_rect = pygame.Rect(x, y, width, height)
    text_rect.center = button_rect.center

    pygame.draw.rect(surface, button_color, button_rect)  # Задаем цвет фона кнопки
    surface.blit(text_surface, text_rect)
    return button_rect

def show_menu():
    menu_running = True
    while menu_running:
        screen.fill(BLUE)
        draw_text(screen, "Правила игры:", WHITE, None, 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(screen, "1. Игроки ходят по очереди", WHITE, None, 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 40)
        draw_text(screen, "2. больше никаких правил, В БОЙ!", WHITE, None, 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 70)
        # ... (добавьте остальные правила по аналогии)

        start_button = draw_button(screen, "В БОЙ!", WHITE, RED, None, 30, SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2, 150, 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                return False  # Завершить программу
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    menu_running = False

    return True  # Перейти к игре

def get_ships_count_by_type(grid, ship_sizes):
    ship_count_by_type = {size: 0 for size in ship_sizes}

    def is_ship_start(x, y):
        # Проверяем, является ли клетка началом корабля
        if grid[y][x] != 1:
            return False
        if x > 0 and grid[y][x - 1] == 1:
            return False
        if y > 0 and grid[y - 1][x] == 1:
            return False
        return True

    def ship_length(x, y, orientation):
        # Возвращает длину корабля, начиная с клетки (x, y)
        length = 0
        if orientation == 'horizontal':
            while x + length < GRID_SIZE and grid[y][x + length] == 1:
                length += 1
        else:
            while y + length < GRID_SIZE and grid[y + length][x] == 1:
                length += 1
        return length

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if is_ship_start(x, y):
                for orientation in ['horizontal', 'vertical']:
                    length = ship_length(x, y, orientation)
                    if length in ship_count_by_type:
                        ship_count_by_type[length] += 1
                        mark_ship_as_counted(grid, x, y, length, orientation)
                        break  # Переходим к следующей клетке после подсчета корабля

    # Сбрасываем состояние считанных кораблей обратно в 1
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] == 'counted':
                grid[y][x] = 1

    # Подсчитываем корабли в соответствии с заданными размерами
    final_count_by_type = {size: 0 for size in SHIP_SIZES}
    for size, count in ship_count_by_type.items():
        final_count_by_type[size] = count  # Прямое присвоение количества кораблей

    return final_count_by_type

def is_ship_at(grid, x, y, size, orientation):
    # Проверяем, находится ли корабль заданного размера и ориентации в данной позиции
    if orientation == 'horizontal' and x + size <= GRID_SIZE:
        return all(grid[y][x+i] == 1 for i in range(size))
    elif orientation == 'vertical' and y + size <= GRID_SIZE:
        return all(grid[y+i][x] == 1 for i in range(size))
    return False

def mark_ship_as_counted(grid, x, y, length, orientation):
    # Отмечаем клетки корабля как 'counted', чтобы избежать их повторного подсчета
    for i in range(length):
        if orientation == 'horizontal':
            grid[y][x + i] = 'counted'
        else:  # vertical
            grid[y + i][x] = 'counted'

def draw_ships_count_table(surface, player_ships_count, computer_ships_count, offset_x, offset_y):
    # Отображаем заголовки для таблицы
    draw_text(surface, "Игрок", WHITE, None, 24, offset_x, offset_y)
    draw_text(surface, "Противник", WHITE, None, 24, offset_x + 100, offset_y)

    # Отображаем количество кораблей каждого типа
    y_offset = offset_y + 30
    for ship_size in sorted(set(SHIP_SIZES), reverse=True):
        draw_text(surface, f"{ship_size}:", WHITE, None, 24, offset_x, y_offset)
        draw_text(surface, str(player_ships_count.get(ship_size, 0)), WHITE, None, 24, offset_x + 50, y_offset)
        draw_text(surface, str(computer_ships_count.get(ship_size, 0)), WHITE, None, 24, offset_x + 150, y_offset)
        y_offset += 30

# Игровой цикл

def game_loop():

    running = True
    player_turn = True
    computer_shots = set()  # Множество для хранения сделанных выстрелов компьютера
    victory_message = ""  # Добавлено объявление переменной

    # Расстановка кораблей
    place_ships_randomly(player_grid, SHIP_SIZES)
    place_ships_randomly(computer_grid, SHIP_SIZES)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] >= SCREEN_WIDTH // 2:  # Игрок может стрелять только в правую часть экрана
                    grid_x, grid_y = get_grid_position((mouse_pos[0] - SCREEN_WIDTH // 2, mouse_pos[1]))
                    if make_shot(computer_grid, grid_x, grid_y):
                        if check_victory(computer_grid):
                            victory_message = "Игрок победил!"
                            running = False
                    else:
                        player_turn = False  # Если игрок промахнулся, ход переходит к компьютеру


        # Ход компьютера
        if not player_turn and running:  # Добавлено условие running, чтобы избежать хода компьютера после победы игрока
            pygame.time.wait(500)  # Задержка перед ходом компьютера для визуализации
            computer_hit = computer_turn(player_grid, computer_shots)
            while computer_hit:
                pygame.time.wait(500)  # Задержка для визуализации последовательных выстрелов
                computer_hit = computer_turn(player_grid, computer_shots)
                if check_victory(player_grid):
                    victory_message = "Компьютер победил!"
                    running = False
                    break  # Выход из цикла, если компьютер победил
            player_turn = True  # После промаха компьютера ход переходит к игроку

        # Получаем количество кораблей каждого типа
        player_ships_count = get_ships_count_by_type(player_grid, SHIP_SIZES)
        computer_ships_count = get_ships_count_by_type(computer_grid, SHIP_SIZES)

        # Отрисовка
        screen.fill(BLUE)
        draw_grids(player_grid, computer_grid)

        # Устанавливаем координаты для таблицы, чтобы избежать наложения
        table_offset_x = GRID_SIZE * CELL_SIZE + 20  # Отступ слева от игрового поля
        table_offset_y = 350
        # Отступ сверху экрана
        draw_ships_count_table(screen, player_ships_count, computer_ships_count, table_offset_x, table_offset_y)

        if not running and victory_message:
            draw_text(screen, victory_message, RED, None, 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        pygame.display.flip()

        if not running:
            pygame.time.wait(3000)  # Задержка, чтобы игрок увидел сообщение


if show_menu():
    game_loop()

pygame.quit()