# Matrix Lang Interpreter

Interpreter for simple python-like language.

## Example programs

### Triangle drawing

    for i = 1:10 print "*" * i;

### Primes generation

    for n = 2:100 {
        p = 1;
        for d = 2:n-1 {
            nc = n;
            while (nc > 0) nc -= d;
            if (nc == 0) {
                p = 0;
                break;
            }
        }
        if (p == 1) print n;
    }

### Matrix multiplication

    A = [[1, 2, 3],
         [4, 5, 6],
         [6, 7, 8],
         [9,10,11]];
    B = eye(3);
    C = A @ B;
    print C;
    print C[0];
    print C[0][1] == C[0, 1];

### Computing PI

    pi = 0.0;
    n = 1;
    prec = 100000;
    for i = 1:prec {
        pi += 4.0 / n - 4.0 / (n + 2);
        n += 4;
    }
    print pi;

## How to run?

    pip3 install -r requirements.txt
    python3 main.py [source_file]
