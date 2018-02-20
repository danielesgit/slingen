format long


%Read input matrices
u = dlmread(strcat(execpath, '/u.txt'));
x = dlmread(strcat(execpath, '/x.txt'));
z = dlmread(strcat(execpath, '/z.txt'));

F = dlmread(strcat(execpath, '/F.txt'));
B = dlmread(strcat(execpath, '/B.txt'));
H = dlmread(strcat(execpath, '/H.txt'));
P = dlmread(strcat(execpath, '/P.txt'));
Q = dlmread(strcat(execpath, '/Q.txt'));
R = dlmread(strcat(execpath, '/R.txt'));

%Compute:
% Predict
% y = F*x + B*u;
% Y = F*P*F^T + Q;

% Update
% x = y + Y*H^T*(H*Y*H^T + R)^-1*( z - H*y );
% P = Y - Y*H^T*(H*Y*H^T + R)^-1*H*Y;

y = F*x + B*u;
Y = F*P*F' + Q;

v0 = z - H*y;
M1 = H*Y;
M2 = Y*H';
M3 = M1*H' + R;

U = chol(M3);
v1 = U'\v0;
v2 = U\v1;

M4 = U'\M1;
M5 = U\M4;

x = y + M2*v2;
P = Y - M2*M5;

dlmwrite(strcat(execpath, '/x-out.txt'), x, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/P-out.txt'), P, 'precision', '%.14f');

exit