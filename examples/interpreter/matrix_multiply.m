A = [[1,2,3],
     [4,5,6],
     [6,7,8],
     [9,10,11]];
B = eye(3);
print A @ B;

print '';

B = [[4, 5],
     [1, 2],
     [0, 2]];
print A @ B;

print '';

B = [1, 2, 3];
print A @ B;
print B @ A.T;

print '';

A = [4, 3, 2];
B = [1, 2, 3];
print A @ B;
