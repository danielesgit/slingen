format long


%Read input matrices
K = dlmread(strcat(execpath, '/K.txt'));
y = dlmread(strcat(execpath, '/y.txt'));
X = dlmread(strcat(execpath, '/X.txt'));
x = dlmread(strcat(execpath, '/x.txt'));

%Compute:
%L*trans(L) = K;
%L0*t0 = y;
%trans(L0)*a = t1;
%kx = X*x;
%f = trans(kx)*y;
%L0*v = t2;
%var = trans(x)*x - trans(kx)*kx;
%lp  = trans(y)*y;

L   = chol(K, 'lower');
y   = L\y;
y   = L'\y;
kx  = X*x;
f   = kx'*y;
kx  = L\kx;
var = x'*x - kx'*kx;
lp  = y'*y;

dlmwrite(strcat(execpath, '/L-out.txt'), L, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/y-out.txt'), y, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/kx-out.txt'), kx, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/f-out.txt'), f, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/var-out.txt'), var, 'precision', '%.14f');
dlmwrite(strcat(execpath, '/lp-out.txt'), lp, 'precision', '%.14f');

exit