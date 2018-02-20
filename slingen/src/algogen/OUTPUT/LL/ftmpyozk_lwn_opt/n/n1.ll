
%% Equal( NL[ D_1 ], ftmpyozk_lwn( A, B_11, D_1 ) )
@out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,0)] = ftmpyozk_lwn_opt(@m@, min(@nb@,@n@); @op0@[h(@m@,@m@,0), h(@m@,@m@,0)]#LowerTriangular#, @op1@[h(min(@nb@,@n@),@n@,0), h(min(@nb@,@n@),@n@,0)]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,0)]);
For[ @it@; @nb@; @n@-(@nb@); @nb@ ]
{
	%% Equal( NL[ D_1 ], Plus( Times( Minus( D_0 ), Transpose( B_10 ) ), C_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = -@out0@[h(@m@,@m@,0), h(@it@,@n@,0)] * trans(@op1@[h(@nb@,@n@,@it@), h(@it@,@n@,0)]) + @op2@[h(@m@,@m@,0), h(@nb@,@n@,@it@)];
	%% Equal( NL[ D_1 ], ftmpyozk_lwn( A, B_11, D_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = ftmpyozk_lwn_opt(@m@, @nb@; @op0@[h(@m@,@m@,0), h(@m@,@m@,0)]#LowerTriangular#, @op1@[h(@nb@,@n@,@it@), h(@nb@,@n@,@it@)]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)]);
};

