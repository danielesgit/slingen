format long


%Read input matrices
a = dlmread(strcat(execpath, '/a.txt'));
b = dlmread(strcat(execpath, '/b.txt'));
t = dlmread(strcat(execpath, '/t.txt'));

v1 = dlmread(strcat(execpath, '/v1.txt'));
v2 = dlmread(strcat(execpath, '/v2.txt'));
z1 = dlmread(strcat(execpath, '/z1.txt'));
z2 = dlmread(strcat(execpath, '/z2.txt'));
x0 = dlmread(strcat(execpath, '/x0.txt'));
y = dlmread(strcat(execpath, '/y.txt'));

A = dlmread(strcat(execpath, '/A.txt'));
W = dlmread(strcat(execpath, '/W.txt'));

%Compute:
%y1 = a*v1 + t*z1;
%y2 = a*v2 + t*z2;
%x  = x0 + b*(trans(W)*y1 - trans(A)*y2);
%z1 = y1 - W*x;
%z2 = y2 -(y - Ax);
%v1 = a*v1 + t*z1;
%v2 = a*v2 + t*z2;

y1 = a*v1 + t*z1;
y2 = a*v2 + t*z2;
x  = x0 + b*(W'*y1 - A'*y2);
z1 = y1 - W*x;
z2 = y2 -(y - A*x);
v1 = a*v1 + t*z1;
v2 = a*v2 + t*z2;

dlmwrite(strcat(execpath, '/v1-out.txt'), v1, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/v2-out.txt'), v2, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/y1-out.txt'), y1, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/y2-out.txt'), y2, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/z1-out.txt'), z1, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/z2-out.txt'), z2, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/x-out.txt'), x, 'precision', '%.14f');

exit