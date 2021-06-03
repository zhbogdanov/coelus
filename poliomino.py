from copy import deepcopy
import numpy as np

NUM_OF_COLORS = 8

SHOW_RESULT = False

INPUT_DATA = [
    (4, 5), # Размер прямоугольника
    [((2, 2), 1)], # Прямоугольные полиомино
    [((3, 2), 2), ((2, 2), 2)] # L-образные полиомино
]

class FontColors:
    def __init__(self):
        self.colors = {}
        self.colors[0] = '\033[91m'
        self.colors[1] = '\033[92m'
        self.colors[2] = '\033[93m'
        self.colors[3] = '\033[94m'
        self.colors[4] = '\033[95m'
        self.colors[5] = '\033[96m'
        self.colors[6] = '\033[97m'
        self.colors[7] = '\033[99m'

    def get_color(self, i):
        return self.colors[i]

def get_class(coords, all_coords):
    for i in range(len(all_coords)):
        if coords in all_coords[i]:
            return i % NUM_OF_COLORS
    return NUM_OF_COLORS + 1

def print_color_matrix(matrix, coords):
    colors = FontColors()
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            color_class = get_class((i, j), coords) 
            print(' ' if color_class == 9 else colors.get_color(color_class) + '#' + '\033[0m', end='')
        print()

# Заполнение прямоугольника 
def fill_rectangular(matrix, width, heigh):
    for i in range(heigh):
        for j in range(width):
            matrix[i][j] = 1
    return matrix

# Сдвиг полиомино по вертикали
def shift_axis0(matrix, step_axis0):
    result = []
    for step in range(step_axis0 + 1):
        result.append(np.roll(matrix, step, axis=0))
    return result

# Сдвиг полиомино во всех направлениях
def shift_poliomino(matrix, step_axis0, step_axis1):
    result = []
    for step in range(step_axis1 + 1):   
        result.extend(shift_axis0(np.roll(matrix, step, axis=1), step_axis0))
    return result

class Poliomino:
    def __init__(self, pol_size, desk_w, desk_h, mode):
        self.mode = mode            # Прямоугольные или L-образные (R or L)
        self.heigh = pol_size[0]    # Длине левой "коемки" полиомино
        self.width = pol_size[1]    # Длине нижней "коемки" полиомино 
        self.desk_w = desk_w        # Ширина поля (по горизонтали)
        self.desk_h = desk_h        # Высота поля (по вертикали)
        self.orientation = []       # Повернутые в пространстве фигуры
        self.permutations = []      # Перестановки всех поворотов фигур 
        if mode == 'R':
            self.size = self.heigh * self.width
            # Либо полиомино прямоугольник и помещается только вдоль, либо полиомино квадрат
            if (self.heigh > self.desk_w or self.width > self.desk_h) or self.heigh == self.width:  
                self.rotate = [0]
            # Если полиоино прямоугольник и помещается только поперек 
            elif self.heigh > self.desk_h or self.width > self.desk_w:
                self.heigh, self.width = self.width, self.heigh
                self.rotate = [0]
            else:
                self.rotate = [0, 90]
        else:
            self.size = self.heigh + self.width - 1
            # Полиомино помещается только вдоль
            if self.heigh > self.desk_w or self.width > self.desk_h:
                self.rotate = [0, 180]
            # Полиомино помещается только поперек
            elif self.heigh > self.desk_h or self.width > self.desk_w:
                self.heigh, self.width = self.width, self.heigh
                self.rotate = [0, 180]
            # Полиомино - прямоугольник (на случай, если такой будет подан)
            elif self.heigh == 1 or self.width == 1:
                self.rotate = [0, 90]
            else:
                self.rotate = [0, 90, 180, 270] 

    def rotate_rectangular(self, angles):
        for angle in angles:
            buf_matrix = np.zeros((self.desk_h, self.desk_w))
            if angle == 0:
                self.orientation.append(deepcopy(fill_rectangular(buf_matrix, self.width, self.heigh)))
            elif angle == 90:
                self.orientation.append(deepcopy(fill_rectangular(buf_matrix, self.heigh, self.width)))

    def rotate_l_like(self, angles):
        for angle in angles:
            buf_matrix = np.zeros((self.desk_h, self.desk_w))
            if angle == 0:
                for i in range(self.heigh):
                    buf_matrix[i][0] = 1
                for j in range(self.width):
                    buf_matrix[self.heigh - 1][j] = 1
                self.orientation.append(deepcopy(buf_matrix))
            elif angle == 90:
                heigh, width = self.width, self.heigh
                for i in range(heigh):
                    buf_matrix[i][width - 1] = 1
                for j in range(width):
                    buf_matrix[heigh - 1][j] = 1
                self.orientation.append(deepcopy(buf_matrix))
            elif angle == 180:
                for i in range(self.heigh):
                    buf_matrix[i][self.width - 1] = 1
                for j in range(self.width):
                    buf_matrix[0][j] = 1
                self.orientation.append(deepcopy(buf_matrix))
            else:
                heigh, width = self.width, self.heigh
                for i in range(heigh):
                    buf_matrix[i][0] = 1
                for j in range(width):
                    buf_matrix[0][j] = 1
                self.orientation.append(deepcopy(buf_matrix))

    # Вычисляем расстояние от полиомино до границ доски 
    def add_permutations_length(self):
        for i in range(len(self.rotate)):
            if self.rotate[i] == 0 or self.rotate[i] == 180:
                dif_axis1 = self.desk_w - self.width
                dif_axis0 = self.desk_h - self.heigh
            else:
                dif_axis1 = self.desk_w - self.heigh
                dif_axis0 = self.desk_h - self.width
            self.permutations.extend(shift_poliomino(self.orientation[i], dif_axis0, dif_axis1))

    def get_permutation(self, index):
        return self.permutations[index]

    def get_permutations_length(self):
        return len(self.permutations)

    def get_size(self):
        return self.size

    def get_rotate(self):
        return self.rotate

# Смотрим помещается ли полиомино на доску 
def check_size(desk_w, desk_h, pol):
    return (desk_w < pol[0] or desk_h < pol[1]) and (desk_h < pol[0] or desk_w < pol[1])

def get_coords(matrix):
    coords = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i][j] == 1:
                coords.append((i, j))
    return coords

def main():
    desk_w, desk_h = INPUT_DATA[0][0], INPUT_DATA[0][1]
    poliominos = []

    # Инициализируем прямоугольные полиомино
    for elem in INPUT_DATA[1]: 
        if check_size(desk_w, desk_h, elem[0]):
            return False 
        for _ in range(elem[1]):
            poli = Poliomino(elem[0], desk_w, desk_h, 'R')
            poli.rotate_rectangular(poli.get_rotate())
            poli.add_permutations_length()
            poliominos.append(poli)

    # Инициализируем L-образные полиомино
    for elem in INPUT_DATA[2]:
        if check_size(desk_w, desk_h, elem[0]):
                return False 
        for _ in range(elem[1]):
            poli = Poliomino(elem[0], desk_w, desk_h, 'L')
            poli.rotate_l_like(poli.get_rotate())
            poli.add_permutations_length()
            poliominos.append(poli)

    # Если размер полиомино > размера поля => False
    if desk_w * desk_h < sum(elem.get_size() for elem in poliominos):
        return False      

    # Сортируем по размеру (от большего к меньшему)
    poliominos.sort(key=lambda x: x.get_size(), reverse=True)

    # Начинаем перебирать варианты 
    length_of_permutations = [elem.get_permutations_length() - 1 for elem in poliominos]    # Массив с длинами всевозможных перестановок для каждого полиомино
    current_permitation = [0] * len(poliominos)                                             # Текущая перестановка полиомино
    change_index = len(length_of_permutations) - 1                                          # Индекс по которому изменяем перестановку
    while True:
        result_desk = np.zeros((desk_h, desk_w))
        # Суммируем все перестановки, если фигуры наклыдваются друг на друга, то значение ячейки > 1
        coords = []
        for i in range(len(current_permitation)):
            permutation = poliominos[i].get_permutation(current_permitation[i])
            result_desk = result_desk + permutation
            coords.append(get_coords(permutation))
        if result_desk.max() == 1:
            if SHOW_RESULT:
                print_color_matrix(result_desk, coords)
            return True
        while True:
            # Если перестановок для полиомино с индексом change_index не осталось, переставляем предыдущее полиомино и начинаем переставлять все последующие 
            if current_permitation == length_of_permutations:
                return False
            if current_permitation[change_index] == length_of_permutations[change_index]:
                current_permitation[change_index] = 0
                change_index -= 1
            else:
                current_permitation[change_index] += 1
                change_index = len(length_of_permutations) - 1
                break
            
result = main()
print(result)
