from enum import Enum, auto
from typing import *
from pyray import *
import os
import json
import math
import random
import user_interface
RESOLUTION_X = 1450
RESOLUTION_Y = 800
SETTINGS = {
    "GridSort": {
        "Active": True,
        "Operations": 5,
        "SwapInterval": 3.0, 
        "RotateInterval": 5.0,
        "GridSize": 2,
    },
    "BlindChess": {
        "Active": False,
    },
}
init_window(RESOLUTION_X, RESOLUTION_Y, "Optical-Sense")
set_target_fps(get_monitor_refresh_rate(get_current_monitor()))
if os.path.getsize("settings_data.json") == 0:
    with open("settings_data.json", "w") as settings_file:
        settings_file.write(json.dumps(SETTINGS, indent=4))
with open("settings_data.json", "r") as file:
    settings_data = json.load(file)
is_generating = False
is_playing = False
is_reviewing = False
is_intermission = False
is_settings = False
deep_settings = False
settings_buttons = {}
settings_buttons["grid_sort_active"] = user_interface.Button("Active:", 25, Rectangle(50 + measure_text("Active:", 25) + 10, 75, 25, 25))
settings_buttons["grid_sort_operations"] = user_interface.InputButton("Operations:", 25, Rectangle(50 + measure_text("Operations:", 25) + 10, 125, measure_text("00", 25), 25))
settings_buttons["grid_sort_swap_interval"] = user_interface.InputButton("Swap Interval:", 25, Rectangle(50 + measure_text("Swap Interval:", 25) + 10, 175, measure_text("000", 25), 25))
settings_buttons["grid_sort_rotate_interval"] = user_interface.InputButton("Rotate Interval:", 25, Rectangle(50 + measure_text("Rotate Interval:", 25) + 10, 225, measure_text("000", 25), 25))
settings_buttons["grid_sort_size"] = user_interface.InputButton("Grid Size:", 25, Rectangle(50 + measure_text("Grid Size:", 25) + 10, 275, measure_text("0", 25), 25))
settings_buttons["blind_chess_active"] = user_interface.Button("Active:", 25, Rectangle(50 + measure_text("Active", 25) + 10, 75, 25, 25))

settings_buttons["grid_sort_active"]._on = settings_data["GridSort"]["Active"]
settings_buttons["grid_sort_operations"].text = str(settings_data["GridSort"]["Operations"])
settings_buttons["grid_sort_swap_interval"].text = str(settings_data["GridSort"]["SwapInterval"])
settings_buttons["grid_sort_rotate_interval"].text = str(settings_data["GridSort"]["RotateInterval"])
settings_buttons["grid_sort_size"].text = str(settings_data["GridSort"]["GridSize"])
settings_buttons["blind_chess_active"]._on = settings_data["BlindChess"]["Active"]
blacklist_toggle = []
def redirect_settings():
    global deep_settings
    draw_text("Grid Sort Mode", 50, 80, 25, WHITE)
    draw_text("Blind Chess Mode", 50, 130, 25, WHITE)
    if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
        current_position = get_mouse_position()
        if check_collision_point_rec(current_position, Rectangle(50, 80, measure_text("Grid Sort Mode", 25), 25)):
            deep_settings = True
            settings_buttons["grid_sort_active"].toggle()
            settings_buttons["grid_sort_operations"].toggle()
            settings_buttons["grid_sort_swap_interval"].toggle()
            settings_buttons["grid_sort_rotate_interval"].toggle()
            settings_buttons["grid_sort_size"].toggle()
        elif check_collision_point_rec(current_position, Rectangle(50, 130, measure_text("Blind Chess Mode", 25), 25)):
            deep_settings = True
            settings_buttons["blind_chess_active"].toggle()
def rotate_square_matrix_clockwise(matrix: List[List[int]]):
    rotated_matrix = []
    for i in range(len(matrix)):
        rotated_matrix.append([])
        for j in range(len(matrix)):
            rotated_matrix[-1].append(matrix[len(matrix) - j - 1][i])
    return rotated_matrix
def transpose_square_matrix(matrix: List[List[int]]):
    transposed_matrix = []
    for i in range(len(matrix)):
        transposed_matrix.append([])
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            transposed_matrix[j].append(matrix[i][j])
    return transposed_matrix
def flatten_square_matrix(matrix: List[List[int]]):
    flattened_matrix = []
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            flattened_matrix.append(matrix[i][j])
    return flattened_matrix
grid_permutation = []
compared_grid_permutation = []
grid_operations = []
output_permutation = []
transposed_review_matrix = []
current_operation = 1
review_id = 1
operation_clock = 0
def reset_game():
    global is_playing
    global is_reviewing
    global grid_permutation
    global compared_grid_permutation
    global output_permutation
    global transposed_review_matrix
    global grid_operations
    global current_operation
    global operation_clock
    global review_id
    is_reviewing = False
    is_playing = False
    grid_permutation = []
    compared_grid_permutation = []
    output_permutation = []
    transposed_review_matrix = []
    grid_operations = []
    current_operation = 1
    operation_clock = 0
    review_id = 1
chosen_gamemode = ""
while not window_should_close():
    begin_drawing()
    clear_background(BLACK)
    if is_generating:
        gamemode_options = []
        if settings_data["GridSort"]["Active"]:
            gamemode_options.append("Grid Sort")
        if settings_data["BlindChess"]["Active"]:
            gamemode_options.append("Blind Chess")
        chosen_gamemode = random.choice(gamemode_options)
        is_generating = False
        if chosen_gamemode == "Grid Sort":
            grid_size = settings_data["GridSort"]["GridSize"]
            grid_permutation = list(range(int(math.pow(settings_data["GridSort"]["GridSize"], 2))))
            compared_grid_permutation = list(range(int(math.pow(settings_data["GridSort"]["GridSize"], 2))))
            random.shuffle(grid_permutation)
            two_d_permutation = []
            transpose_input = []
            for i in range(grid_size):
                transpose_input.append([])
                for j in range(grid_size):
                    transpose_input[-1].append((i * grid_size) + j)
            transposed_review_matrix = flatten_square_matrix(transpose_square_matrix(transpose_input))
            for i in range(grid_size):
                two_d_permutation.append([])
                for j in range(grid_size):
                    two_d_permutation[-1].append(grid_permutation[(i * grid_size) + j])
            for i in range(settings_data["GridSort"]["Operations"]):
                if random.random() < 0.2:
                    direction = "Clockwise" 
                    if random.random() < 0.5:
                        direction = "CounterClockwise"
                    grid_operations.append({
                        "Operation": "Rotate",
                        "Direction": direction,
                    })
                    if direction == "Clockwise":
                        two_d_permutation = rotate_square_matrix_clockwise(two_d_permutation)
                    else:
                        for i in range(3):
                            two_d_permutation = rotate_square_matrix_clockwise(two_d_permutation)
                else:
                    if random.random() < 0.33:
                        grid_range = list(range(grid_size))
                        row = random.choice(grid_range)
                        grid_range.remove(row)
                        row_to_swap_with = random.choice(grid_range)
                        grid_operations.append({
                            "Operation": "SwapRow",
                            "Rows": (row, row_to_swap_with),
                        })
                        two_d_permutation[row], two_d_permutation[row_to_swap_with] = two_d_permutation[row_to_swap_with], two_d_permutation[row]
                    else:
                        grid_range = list(range(int(math.pow(grid_size, 2))))
                        grid_index = random.choice(grid_range)
                        grid_range.remove(grid_index)
                        index_to_swap_with = random.choice(grid_range)
                        grid_operations.append({
                            "Operation": "Swap",
                            "Indices": (grid_index, index_to_swap_with)
                        })
                        two_d_permutation[grid_index // grid_size][grid_index % grid_size], two_d_permutation[index_to_swap_with // grid_size][index_to_swap_with % grid_size] = two_d_permutation[index_to_swap_with // grid_size][index_to_swap_with % grid_size], two_d_permutation[grid_index // grid_size][grid_index % grid_size]
            for i in range(grid_size):
                for j in range(grid_size):
                    output_permutation.append(two_d_permutation[i][j])
            print(output_permutation)
            operation_clock = get_time()
        elif chosen_gamemode == "Blind Chess":
            pass
    if is_settings:
        if deep_settings:
            pass
        else:
            redirect_settings()
    else:
        draw_text("[S] Settings", 50, 30, 25, WHITE)
        draw_text("[Space] Start/Stop", int(RESOLUTION_X / 2) - int(measure_text("[Space] Start/Stop", 50) / 2), int(0.85 * (RESOLUTION_Y)), 50, WHITE)
        if is_playing:
            if chosen_gamemode == "Grid Sort":
                grid_size = settings_data["GridSort"]["GridSize"]
                cell_size = int(400 / grid_size)
                line_gap = 10
                if is_reviewing:
                    for i in range(grid_size):
                        for j in range(grid_size):
                            original_index = (i * grid_size) + j
                            if original_index == review_id - 1:
                                draw_rectangle(int((RESOLUTION_X / 2) - 150 - cell_size - ((cell_size + line_gap) * (grid_size - i - 1))), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), cell_size, cell_size, GREEN)
                            else:
                                draw_rectangle(int((RESOLUTION_X / 2) - 150 - cell_size - ((cell_size + line_gap) * (grid_size - i - 1))), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), cell_size, cell_size, PURPLE)
                    current_position = get_mouse_position()
                    break_outer_loop = False
                    for i in range(grid_size):
                        for j in range(grid_size):
                            original_index = (i * grid_size) + j
                            translated_index = (j * grid_size) + i
                            to_write = str(compared_grid_permutation[translated_index])
                            draw_rectangle(int((RESOLUTION_X / 2) + 150 + ((cell_size + line_gap) * i)), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), cell_size, cell_size, PURPLE)
                            draw_text(to_write, int((RESOLUTION_X / 2) + 150 + ((cell_size + line_gap) * i)), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), measure_text("0", cell_size), WHITE)
                            if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                                if check_collision_point_rec(current_position, Rectangle(int((RESOLUTION_X / 2) + 150 + ((cell_size + line_gap) * i)), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), cell_size, cell_size)):
                                    if output_permutation[transposed_review_matrix[review_id - 1]] == translated_index:
                                        review_id += 1
                                    else:
                                        break_outer_loop = True
                                        reset_game()
                                        break
                        if break_outer_loop:
                            break
                    if review_id == math.pow(settings_data["GridSort"]["GridSize"], 2) + 1:
                        reset_game()
                else:
                    operation_data = grid_operations[current_operation - 1]
                    specific_operation = operation_data["Operation"]
                    for i in range(grid_size):
                        for j in range(grid_size):
                            original_index = (i * grid_size) + j
                            translated_index = (j * grid_size) + i
                            to_write = str(grid_permutation[translated_index])
                            if specific_operation == "Swap" and (operation_data["Indices"][0] == translated_index or operation_data["Indices"][1] == translated_index):
                                draw_rectangle(int((RESOLUTION_X / 2) - 150 - cell_size - ((cell_size + line_gap) * (grid_size - i - 1))), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), cell_size, cell_size, RED)
                            elif specific_operation == "SwapRow" and (operation_data["Rows"][0] == j or operation_data["Rows"][1] == j):
                                draw_rectangle(int((RESOLUTION_X / 2) - 150 - cell_size - ((cell_size + line_gap) * (grid_size - i - 1))), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), cell_size, cell_size, RED)
                            elif specific_operation == "Rotate":
                                draw_rectangle(int((RESOLUTION_X / 2) - 150 - cell_size - ((cell_size + line_gap) * (grid_size - i - 1))), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), cell_size, cell_size, GREEN)
                            else:
                                draw_rectangle(int((RESOLUTION_X / 2) - 150 - cell_size - ((cell_size + line_gap) * (grid_size - i - 1))), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), cell_size, cell_size, PURPLE)
                            draw_text(to_write, int((RESOLUTION_X / 2) - 150 - cell_size - ((cell_size + line_gap) * (grid_size - i - 1))), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), measure_text("0", cell_size), WHITE)
                    for i in range(grid_size):
                        for j in range(grid_size):
                            translated_index = (j * grid_size) + i
                            to_write = str(compared_grid_permutation[translated_index])
                            draw_rectangle(int((RESOLUTION_X / 2) + 150 + ((cell_size + line_gap) * i)), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), cell_size, cell_size, PURPLE)
                            draw_text(to_write, int((RESOLUTION_X / 2) + 150 + ((cell_size + line_gap) * i)), int((RESOLUTION_Y / 2) + ((cell_size + line_gap) * (j - (grid_size / 2)))), measure_text("0", cell_size), WHITE)
                    interval = 0.0
                    if specific_operation == "Swap" or specific_operation == "SwapRow":
                        interval = settings_data["GridSort"]["SwapInterval"]
                    elif specific_operation == "Rotate":
                        interval = settings_data["GridSort"]["RotateInterval"]
                        draw_text(operation_data["Direction"] + " 90 Degrees", int((RESOLUTION_X / 2) - measure_text(operation_data["Direction"] + " 90 Degrees", 50) / 2), 50, 50, WHITE)
                    draw_text(str(current_operation), int((RESOLUTION_X / 2) - (measure_text(str(current_operation), 50) / 2)), int((RESOLUTION_Y / 2) - (measure_text(str(current_operation), 50) / 2)), 50, WHITE)
                    if get_time() - operation_clock > interval:
                        current_operation += 1
                        operation_clock = get_time()
                        if current_operation - 1 == settings_data["GridSort"]["Operations"]:
                            is_reviewing = True
            elif chosen_gamemode == "Blind Chess":
                pass
        if is_key_pressed(KeyboardKey.KEY_SPACE):
            if not is_playing:
                is_generating = True
                reset_game()
            is_playing = not is_playing
    if is_key_pressed(KeyboardKey.KEY_S):
        reset_game()
        if deep_settings:
            deep_settings = False
            for key, settings_object in settings_buttons.items():
                if settings_object._enabled:
                    blacklist_toggle.append(key)    
                    settings_object.toggle()
                else:
                    if key in blacklist_toggle:
                        blacklist_toggle.remove(key)
        else:
            is_settings = not is_settings
        settings_data["GridSort"]["Active"] = settings_buttons["grid_sort_active"]._on
        settings_data["GridSort"]["Operations"] = max(int(settings_buttons["grid_sort_operations"].text), 3)
        settings_data["GridSort"]["SwapInterval"] = max(float(settings_buttons["grid_sort_swap_interval"].text), 0.2)
        settings_data["GridSort"]["RotateInterval"] = max(float(settings_buttons["grid_sort_swap_interval"].text), 0.2)
        settings_data["GridSort"]["GridSize"] = max(int(settings_buttons["grid_sort_size"].text), 2)
        settings_data["BlindChess"]["Active"] = settings_buttons["blind_chess_active"]._on 
        with open("settings_data.json", "w") as file:
            json.dump(settings_data, file)
    for settings_object in settings_buttons.values():
        settings_object.update()
    end_drawing()
close_window()    
