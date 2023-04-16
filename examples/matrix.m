A = eye(3);
B = ones(3, 3);
C = A + B;

D = zeros(3, 4);
D[0, 1] = 42;
print D;
print D[0, 1];
