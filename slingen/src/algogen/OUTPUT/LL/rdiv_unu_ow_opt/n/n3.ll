
%% Equal( NL[ B_1 ], rdiv_unu_ow( U_11, B_1 ) )
@out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,0)] = rdiv_unu_ow_opt(@m@, min(@nb@,@n@); @op0@[h(min(@nb@,@n@),@n@,0), h(min(@nb@,@n@),@n@,0)]#UpperTriangular#, @out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,0)]);
For[ @it@; @nb@; @n@-(@nb@); @nb@ ]
{
	%% Equal( NL[ B_1 ], Plus( Times( Minus( B_0 ), U_01 ), A_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = -@out0@[h(@m@,@m@,0), h(@it@,@n@,0)] * @op0@[h(@it@,@n@,0), h(@nb@,@n@,@it@)] + @op1@[h(@m@,@m@,0), h(@nb@,@n@,@it@)];
	%% Equal( NL[ B_1 ], rdiv_unu_ow( U_11, B_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = rdiv_unu_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,@it@), h(@nb@,@n@,@it@)]#UpperTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)]);
};

