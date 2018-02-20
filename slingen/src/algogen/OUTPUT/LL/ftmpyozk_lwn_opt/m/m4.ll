
For[ @it@; 0; @m@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ D_1 ], ftmpyozk_lwn( A_11, B, D_1 ) )
	@out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] = ftmpyozk_lwn_opt(@nb@, @n@; @op0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular#, @op1@[h(@n@,@n@,0), h(@n@,@n@,0)]#LowerTriangular#, @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)]);
	%% Equal( NL[ D_2 ], Plus( Times( Minus( A_21 ), D_1 ), D_2 ) )
	@out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@n@,@n@,0)] = -@op0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@nb@,@m@,@it@)] * @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] + @out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@n@,@n@,0)];
};
%% Equal( NL[ D_1 ], ftmpyozk_lwn( A_11, B, D_1 ) )
@out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@n@,@n@,0)] = ftmpyozk_lwn_opt(@nb@, @n@; @op0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@nb@,@m@,max(@m@-@nb@, 0))]#LowerTriangular#, @op1@[h(@n@,@n@,0), h(@n@,@n@,0)]#LowerTriangular#, @out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@n@,@n@,0)]);

