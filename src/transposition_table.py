import numpy as np
from enum import Enum

# flag options for entry
class Flag(Enum):
    EXACT = 0
    LOWER_BOUND = 1
    UPPER_BOUND = 2

class HashEntry:
    def __init__(self, zobrist, best_move, depth, value, flag, age):
        self.zobrist = zobrist
        self.best_move = best_move
        self.depth = depth
        self.value = value
        self.flag = flag
        self.age = age

    def json(self):
        return {
            'zobrist': self.zobrist,
            'best_move': str(self.best_move),
            'depth': self.depth,
            'value': self.value,
            'flag': self.flag.name,
            'age': self.age
        }

# 2^20 + 7 (prime number)
table_size = 1048583

class TranspositionTable:

    def __init__(self):
        self.table = np.empty(table_size, dtype = HashEntry)

    # There are different replacement schemes that can be used -- always replace, replace by depth, deep + always
    # This is currently using replace by depth
    def replace(self, hash_entry):
        index = hash_entry.zobrist % table_size
        stored_entry = self.table[index]

        if not stored_entry or hash_entry.age > stored_entry.age or hash_entry.depth > stored_entry.depth:
            np.put(self.table, index, hash_entry)

    def get(self, zobrist, depth):
        index = zobrist % table_size

        stored_entry = self.table[index]

        # do not return entry if zobrist does not match (collision occurred)
        if stored_entry and zobrist == stored_entry.zobrist and stored_entry.depth >= depth:
            return stored_entry

        return None
