
%% Equal( NL[ B_1 ], ldiv_ln_ow( L_11, B_1 ) )
@out0@[h(min(@nb@,@m@),@m@,0), h(@n@,@n@,0)] = ldiv_ln_ow_opt(min(@nb@,@m@), @n@; @op0@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#LowerTriangular#, @out0@[h(min(@nb@,@m@),@m@,0), h(@n@,@n@,0)]);
For[ @it@; @nb@; @m@-(@nb@); @nb@ ]
{
	%% Equal( NL[ B_1 ], Plus( Times( Minus( L_10 ), B_0 ), A_1 ) )
	@out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] = -@op0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)] * @out0@[h(@it@,@m@,0), h(@n@,@n@,0)] + @op1@[h(@nb@,@m@,@it@), h(@n@,@n@,0)];
	%% Equal( NL[ B_1 ], ldiv_ln_ow( L_11, B_1 ) )
	@out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] = ldiv_ln_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular#, @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)]);
};

