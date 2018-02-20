
%% Equal( NL[ B_1 ], ldiv_uti_ow( U_11, B_1 ) )
@out0@[h(min(@nb@,@m@),@m@,0), h(@n@,@n@,0)] = ldiv_uti_ow_opt(min(@nb@,@m@), @n@; @op0@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#UpperTriangular#, @out0@[h(min(@nb@,@m@),@m@,0), h(@n@,@n@,0)]);
For[ @it@; @nb@; @m@-(@nb@); @nb@ ]
{
	%% Equal( NL[ B_1 ], Plus( Times( Minus( Transpose( U_01 ) ), B_0 ), A_1 ) )
	@out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] = -trans(@op0@[h(@it@,@m@,0), h(@nb@,@m@,@it@)]) * @out0@[h(@it@,@m@,0), h(@n@,@n@,0)] + @op1@[h(@nb@,@m@,@it@), h(@n@,@n@,0)];
	%% Equal( NL[ B_1 ], ldiv_uti_ow( U_11, B_1 ) )
	@out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] = ldiv_uti_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#UpperTriangular#, @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)]);
};

