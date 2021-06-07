from copy import deepcopy
import numpy as np

NUM_OF_COLORS = 8

INPUT_DATA = [
    (4, 5), # Размер прямоугольника
    [((2, 2), 1)], # Прямоугольные полиомино
    [((3, 2), 2), ((2, 2), 2)] # L-образные полиомино
]

class FontColors:
    def __init__(self):
        self.colors = {}
        self.colors[1] = '\033[91m'
        self.colors[2] = '\033[92m'
        self.colors[3] = '\033[93m'
        self.colors[4] = '\033[94m'
        self.colors[5] = '\033[95m'
        self.colors[6] = '\033[96m'
        self.colors[7] = '\033[97m'
        self.colors[8] = '\033[99m'

    def get_color(self, i):
        return self.colors[i]

class Poliomino:
    def __init__(self, params=(0, 0), quantity = 0, desk_w = 1, desk_h = 1, mode = 'R'):
        self.width = params[0]
        self.height = params[1]            
        self.quantity = quantity 
        self.mode = mode     
        self.schema = {}     
        self.size = self.width * self.height if mode == 'R' else self.width + self.height - 1
        pos = 0
        if mode == 'R':  
            # Либо полиомино прямоугольник и помещается только вдоль, либо полиомино квадрат
            if (self.height > desk_w or self.width > desk_h) or self.height == self.width:  
                self.rotate = [0]
            # Если полиоино прямоугольник и помещается только поперек 
            elif self.height > desk_h or self.width > desk_w:
                self.height, self.width = self.width, self.height
                self.rotate = [0]
            else:
                self.rotate = [0, 90]
            for i in range(self.height):
                for j in range(self.width):
                    self.schema[pos] = [i, j]
                    pos += 1
        else: # mode = L                        
            self.schema[pos] = [0, 0]
            pos=1
            if self.height > desk_w or self.width > desk_h:
                self.rotate = [0, 180]
            # Полиомино помещается только поперек
            elif self.height > desk_h or self.width > desk_w:
                self.height, self.width = self.width, self.height
                self.rotate = [0, 180]
            else:
                self.rotate = [0, 90, 180, 270]
            for j in range(1, self.width):
                self.schema[pos] = [0, j]
                pos += 1
            for i in range(1, self.height):
                self.schema[pos] = [i, 0]
                pos += 1
        
    def rotate_(self, angle):
        if angle == 0:
            return self.schema
        result = deepcopy(self.schema)
        if angle == 90:
            for pos in range(len(self.schema)):
                result[pos][0] = -self.schema[pos][1]
                result[pos][1] = self.schema[pos][0]
        elif angle == 180:
            for pos in range(len(self.schema)):
                result[pos][0] = -self.schema[pos][0]
                result[pos][1] = -self.schema[pos][1]
        elif angle == 270:
            for pos in range(len(self.schema)):
                result[pos][0] = self.schema[pos][1]
                result[pos][1] = -self.schema[pos][0]
        return result

    def get_width(self):
        return self.width

    def get_rotate(self):
        return self.rotate

    def get_quantity(self):
        return self.quantity
    
    def get_size(self):
        return self.quantity * self.size

    def get_max(self):
        return max(self.width, self.height)
    
    def inc_quantity(self):
        self.quantity += 1

    def dec_quantity(self):
        self.quantity -= 1

    def get_schema_len(self):
        return len(self.schema)
    
class Desk:
    def __init__(self, params = [1, 1], buff = 1):
        self.height = params[1]
        self.width = params[0]
        self.decision_tree = []
        self.buff = buff
        self.poli_number = 1
        self.poli_buffer = []
        self.schema = np.zeros((self.height, self.width), dtype=int)
        self.num_of_tree = 0
        self.quantity_of_tree = 0

    def get_sizes(self):
        return self.width, self.height

    def get_pols_size(self):
        return self.width * self.height

    def get_schema_elem(self, i, j):
        return self.schema[i][j]

    def delete_poli(self, i, j, schema, last_pos):
        for pos in range(last_pos):
            self.schema[i + schema[pos][0]][j + schema[pos][1]] = 0

    def add_to_decision_tree(self, i, j, poli, angle, buff):
                                 # pos = 0         children =  1  2
        self.decision_tree.append([[i, j, poli, angle, buff], [], self.quantity_of_tree])
        tree_len = len(self.decision_tree) - 1
        self.decision_tree[self.quantity_of_tree][1].append(self.decision_tree[tree_len])
        self.quantity_of_tree = tree_len

    def put_poliomino_to_tree(self, i, j, poli, angle = 0, add_to_tree = False):
        schema = poli.rotate_(angle)
        buff_ = self.buff
        for pos in range(len(schema)): 
            new_i, new_j = i + schema[pos][0], j + schema[pos][1]
            if new_i < 0 or new_i >= self.height or new_j < 0 or new_j >= self.width or self.schema[new_i][new_j]:            
                self.delete_poli(i, j, schema, pos)
                self.buff = buff_         
                return False
            self.schema[new_i][new_j] = self.poli_number
            self.buff = max(new_i + 1, self.buff)
        poli.dec_quantity()

        if add_to_tree:
            self.add_to_decision_tree(i, j, poli, angle, buff_)
            self.poli_number += 1
        else:   
            self.poli_buffer = [i, j, poli, angle, buff_]
        return True

    def delete_node(self):
        if self.quantity_of_tree == 0:
            return False
        children = self.decision_tree[self.quantity_of_tree][1]
        for child in children:
            self.decision_tree.remove(child)
        self.quantity_of_tree = self.decision_tree[self.quantity_of_tree][2]
        return True

    def delete_poli_from_tree(self):
        if self.poli_buffer:
            [i, j, poli, angle, self.buff] = self.poli_buffer
            self.poli_buffer = []
        else: 
            [i, j, poli, angle, self.buff] = self.decision_tree[self.quantity_of_tree][0]
            if not self.delete_node():
                return -1, -1
            self.poli_number -= 1
        poli.inc_quantity()
        self.delete_poli(i, j, poli.rotate_(angle), poli.get_schema_len())
        return i, j

    def get_measure(self):
        measure = 0
        for i in range(self.buff):
            row_measure = self.schema[i][0] == 0
            for j in range(1, self.width):
                row_measure += (self.schema[i][j] == 0) + ((self.schema[i][j] == 1) & (self.schema[i][j-1] == 0)) * 0.5
            measure += row_measure * (1 + 0.25 * (self.buff - i - 1))
        return measure / self.buff

    def find_the_same_tree(self, poli, angle):
        if self.decision_tree != []:
            for child in self.decision_tree[self.quantity_of_tree][1]:
                data = child[0]
                if (poli == data[2]) and (angle == data[3]):
                    return False
        return True
    
    def print_color(self):
        color = FontColors()
        for i in range(self.buff):
            for j in range(self.width): 
                print(' ' if self.schema[i][j] == 0 else color.get_color(self.schema[i][j] % 8 + 1) + '#' + '\033[0m', end='')
            print()

# Смотрим помещается ли полиомино на доску 
def check_size(desk_w, desk_h, pol):
    return (desk_w < pol[0] or desk_h < pol[1]) and (desk_h < pol[0] or desk_w < pol[1])

def find_next_polim(polis, pos = 0):
    for i in range(pos, len(polis)):
        if polis[i].get_quantity():
            return polis[i], i 
    return None, 0

def find_free_cell(desk, i = 0, j = 0):
    if j >= desk.get_sizes()[0]:
        j = 0
        i += 1
    for i_ in range(i, desk.get_sizes()[1]):
        j = j * (i_ == i)
        for j_ in range(j, desk.get_sizes()[0]):
            if desk.get_schema_elem(i_, j_) == 0:
                return i_, j_
    return -1, -1

def main():
    desk = Desk(INPUT_DATA[0])
    desk_w, desk_h = desk.get_sizes()

    poliominos = []
    # Инициализируем прямоугольные полиомино
    for elem in INPUT_DATA[1]: 
        if check_size(desk_w, desk_h, elem[0]):
            return False 
        poliominos.append(Poliomino(elem[0], elem[1], desk_w, desk_h, 'R'))
    # Инициализируем L-образные полиомино
    for elem in INPUT_DATA[2]: 
        if check_size(desk_w, desk_h, elem[0]):
            return False 
        poliominos.append(Poliomino(elem[0], elem[1], desk_w, desk_h, 'L'))

    pols_quantity = sum(elem.get_quantity() for elem in poliominos) 
    pols_size = sum(elem.get_size() for elem in poliominos)
    # Если суммарная площадь полиомино > площади стола => нельзя разместить
    if pols_size > desk.get_pols_size():
        return False 

    # Сортируем по размеру (от большего к меньшему)
    poliominos.sort(key=lambda x: x.get_max(), reverse=True)

    # Создаем дерево дерешений с нулевым полиомино в узле 
    desk.put_poliomino_to_tree(0, 0, Poliomino(), 0, True)
    num = 0

    # Добавляем первый полиомино 
    desk.put_poliomino_to_tree(0, 0, poliominos[num], 0, True)
    pols_quantity -= 1

    i_start = 0
    j_start = poliominos[num].get_width()

    best_fit = []

    max_measure = desk.get_pols_size()
    measure = max_measure

    poli, num = find_next_polim(poliominos)

    while pols_quantity:
        i_buf, j_buf = i_start, j_start
        if poli:
            for angle in poli.get_rotate():     
                while i_start != -1: 
                    if not desk.find_the_same_tree(poli, angle):
                        break
                    if desk.put_poliomino_to_tree(i_start, j_start, poli, angle):
                        new_measure = desk.get_measure()
                        if new_measure < measure:
                            measure = new_measure
                            best_fit = [i_start, j_start, poli, angle]
                        i, _ = desk.delete_poli_from_tree()
                        if i == -1:
                            return False
                    i_start, j_start = find_free_cell(desk, i_start, j_start + 1)

                i_start, j_start = i_buf, j_buf

        poli, num = find_next_polim(poliominos, num+1)

        if not poli:   
            if best_fit != []: # Если нашли самый подходящий полиомино => размещаем в дереве      
                desk.put_poliomino_to_tree(best_fit[0], best_fit[1], best_fit[2], best_fit[3], True)
                pols_quantity -= 1
                i_start, j_start = find_free_cell(desk, i_start, j_start)
                best_fit, num = [], 0
                measure = max_measure
            else:
                i_start, j_start = find_free_cell(desk, i_start, j_start + 1)
                if i_start == -1:
                    desk.delete_poli_from_tree()
                    pols_quantity += 1
                    i_start, j_start = find_free_cell(desk)
                best_fit = []
            
            poli, num = find_next_polim(poliominos)
                
    desk.print_color()                
    return True

print(main())
