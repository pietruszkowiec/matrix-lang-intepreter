from copy import deepcopy


class BinExpr:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __eq__(self, other):
        return type(self) == type(other) \
            and self.op == other.op \
            and self.left == other.left \
            and self.right == other.right

    def __str__(self):
        return f'(BinExpr({self.op}, {str(self.left)}, {str(self.right)})'

    __repr__ = __str__

class UnExpr:
    def __init__(self, op, child):
        self.op = op
        self.child = child

    def __eq__(self, other):
        return type(self) == type(other) \
            and self.op == other.op \
            and self.child == other.child

    def __str__(self):
        return f'UnExpr({self.op}, {str(self.child)})'

    __repr__ = __str__

class AssignExpr:
    def __init__(self, id, right):
        self.id = id
        self.right = right

    def __eq__(self, other):
        return type(self) == type(other) \
            and self.id == other.id \
            and self.right == other.right

    def __str__(self):
        return f'AssignExpr({str(self.id)}, {str(self.right)})'

    __repr__ = __str__

class Id:
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return type(self) == type(other) \
            and self.id == other.id

    def __str__(self):
        return f'Id({str(self.id)})'

    __repr__ = __str__

class Matrix:
    def __init__(self, m=0, n=0, array=[]):
        self.array = deepcopy(array)
        if self.array:
            self.m = len(self.array)
            self.n = len(self.array[0])
        else:
            self.m = m
            self.n = n

    def __eq__(self, other):
        return self.m == other.m and self.n == other.n \
            and self.array == other.array

    def append(self, innerlist):
        self.array.append(innerlist)
        self.m += 1
        self.n = len(innerlist)
        return self

class Zeros(Matrix):
    def __init__(self, size):
        super().__init__(size, size)

    def __str__(self):
        return f'Zeros({str(self.m)})'

    __repr__ = __str__

class Ones(Matrix):
    def __init__(self, size):
        super().__init__(size, size)

    def __str__(self):
        return f'Ones({str(self.m)})'

    __repr__ = __str__

class Eye(Matrix):
    def __init__(self, size):
        super().__init__(size, size)

    def __str__(self):
        return f'Eye({str(self.m)})'

    __repr__ = __str__
