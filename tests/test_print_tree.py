import pytest
import sys
from matrix_lang_interpreter.AST import *
from matrix_lang_interpreter.scanner import Scanner
from matrix_lang_interpreter.parser import Parser
from matrix_lang_interpreter.print_tree import TreePrinter


@pytest.fixture
def capture_stdout(monkeypatch):
    buffer = {'stdout': ''}

    def fake_write(s):
        # nonlocal buffer
        buffer['stdout'] += s
    
    monkeypatch.setattr(sys.stdout, 'write', fake_write)
    return buffer


def test_SpecialFunctions_Initializations(capture_stdout):
    scanner = Scanner()
    parser = Parser()
    test_input = \
'''
# special functions, initializations
A = zeros(5);  # create 5x5 matrix filled with zeros
B = ones(7);   # create 7x7 matrix filled with ones
I = eye(10);   # create 10x10 matrix filled with ones on diagonal and zeros elsewhere

# initialize 3x3 matrix with specific values
E1 = [ [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9] ] ;

A[1, 3] = 0 ;

x = 2;
y = 2.5;
'''
    expected_output = \
'''=
 | A
 | ZEROS
 |  | VECTOR
 |  |  | 5
=
 | B
 | ONES
 |  | VECTOR
 |  |  | 7
=
 | I
 | EYE
 |  | 10
=
 | E1
 | VECTOR
 |  | VECTOR
 |  |  | 1
 |  |  | 2
 |  |  | 3
 |  | VECTOR
 |  |  | 4
 |  |  | 5
 |  |  | 6
 |  | VECTOR
 |  |  | 7
 |  |  | 8
 |  |  | 9
=
 | REF
 |  | A
 |  | VECTOR
 |  |  | 1
 |  |  | 3
 | 0
=
 | x
 | 2
=
 | y
 | 2.5
'''
    ast = parser.parse(scanner.tokenize(test_input))
    ast.printTree()
    assert capture_stdout['stdout'] == expected_output

def test_Operators(capture_stdout):
    scanner = Scanner()
    parser = Parser()
    test_input = \
'''
# assignment operators
# binary operators
# transposition

C = -A;     # assignemnt with unary expression
C = B' ;    # assignemnt with matrix transpose
C = A+B ;   # assignemnt with binary addition
C = A-B ;   # assignemnt with binary substraction
C = A*B ;   # assignemnt with binary multiplication
C = A/B ;   # assignemnt with binary division
C = A.+B ;  # add element-wise A to B
C = A.-B ;  # substract B from A 
C = A.*B ;  # multiply element-wise A with B
C = A./B ;  # divide element-wise A by B

C += B ;  # add B to C 
C -= B ;  # substract B from C 
C *= A ;  # multiply A with C
C /= A ;  # divide A by C
'''
    expected_output = \
'''=
 | C
 | -
 |  | A
=
 | C
 | '
 |  | B
=
 | C
 | +
 |  | A
 |  | B
=
 | C
 | -
 |  | A
 |  | B
=
 | C
 | *
 |  | A
 |  | B
=
 | C
 | /
 |  | A
 |  | B
=
 | C
 | .+
 |  | A
 |  | B
=
 | C
 | .-
 |  | A
 |  | B
=
 | C
 | .*
 |  | A
 |  | B
=
 | C
 | ./
 |  | A
 |  | B
=
 | C
 | +
 |  | C
 |  | B
=
 | C
 | -
 |  | C
 |  | B
=
 | C
 | *
 |  | C
 |  | A
=
 | C
 | /
 |  | C
 |  | A
'''
    ast = parser.parse(scanner.tokenize(test_input))
    ast.printTree()
    assert capture_stdout['stdout'] == expected_output

def test_FlowControlInstructions(capture_stdout):
    scanner = Scanner()
    parser = Parser()
    test_input = \
'''
# control flow instruction

N = 10;
M = 20;

if(N==10)
    print "N==10";
else if(N!=10)
    print "N!=10";

if(N>5) {
    print "N>5";
}
else if(N>=0) {
    print "N>=0";
}

if(N<10) {
    print "N<10", "Ala ma kota";
}
else if(N<=15)
    print "N<=15";

k = 10;
while(k>0)
    k = k - 1;

while(k>0) {
    if(k<5)
        i = 1;
    else if(k<10)
        i = 2;   
    else
        i = 3;
    
    k = k - 1;
}

for i = 1:N
  for j = i:M
    print i, j;
 
for i = 1:N {
    if(i<=N/16)
        print i;
    else if(i<=N/8)
        break;
    else if(i<=N/4)
        continue;
    else if(i<=N/2)
        return 0;
}

{
  N = 100;
  M = 200;  
}
'''
    expected_output = \
'''=
 | N
 | 10
=
 | M
 | 20
IF
 | ==
 |  | N
 |  | 10
THEN
 | PRINT
 |  | N==10
ELSE
 | IF
 |  | !=
 |  |  | N
 |  |  | 10
 | THEN
 |  | PRINT
 |  |  | N!=10
IF
 | >
 |  | N
 |  | 5
THEN
 | PRINT
 |  | N>5
ELSE
 | IF
 |  | >=
 |  |  | N
 |  |  | 0
 | THEN
 |  | PRINT
 |  |  | N>=0
IF
 | <
 |  | N
 |  | 10
THEN
 | PRINT
 |  | N<10
 |  | Ala ma kota
ELSE
 | IF
 |  | <=
 |  |  | N
 |  |  | 15
 | THEN
 |  | PRINT
 |  |  | N<=15
=
 | k
 | 10
WHILE
 | >
 |  | k
 |  | 0
 | =
 |  | k
 |  | -
 |  |  | k
 |  |  | 1
WHILE
 | >
 |  | k
 |  | 0
 | IF
 |  | <
 |  |  | k
 |  |  | 5
 | THEN
 |  | =
 |  |  | i
 |  |  | 1
 | ELSE
 |  | IF
 |  |  | <
 |  |  |  | k
 |  |  |  | 10
 |  | THEN
 |  |  | =
 |  |  |  | i
 |  |  |  | 2
 |  | ELSE
 |  |  | =
 |  |  |  | i
 |  |  |  | 3
 | =
 |  | k
 |  | -
 |  |  | k
 |  |  | 1
FOR
 | i
 | RANGE
 |  | 1
 |  | N
 | FOR
 |  | j
 |  | RANGE
 |  |  | i
 |  |  | M
 |  | PRINT
 |  |  | i
 |  |  | j
FOR
 | i
 | RANGE
 |  | 1
 |  | N
 | IF
 |  | <=
 |  |  | i
 |  |  | /
 |  |  |  | N
 |  |  |  | 16
 | THEN
 |  | PRINT
 |  |  | i
 | ELSE
 |  | IF
 |  |  | <=
 |  |  |  | i
 |  |  |  | /
 |  |  |  |  | N
 |  |  |  |  | 8
 |  | THEN
 |  |  | BREAK
 |  | ELSE
 |  |  | IF
 |  |  |  | <=
 |  |  |  |  | i
 |  |  |  |  | /
 |  |  |  |  |  | N
 |  |  |  |  |  | 4
 |  |  | THEN
 |  |  |  | CONTINUE
 |  |  | ELSE
 |  |  |  | IF
 |  |  |  |  | <=
 |  |  |  |  |  | i
 |  |  |  |  |  | /
 |  |  |  |  |  |  | N
 |  |  |  |  |  |  | 2
 |  |  |  | THEN
 |  |  |  |  | RETURN
 |  |  |  |  |  | 0
=
 | N
 | 100
=
 | M
 | 200
'''
    ast = parser.parse(scanner.tokenize(test_input))
    ast.printTree()
    assert capture_stdout['stdout'] == expected_output
