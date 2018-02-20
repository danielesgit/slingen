
%% Equal( NL[ X_1 ], sylv_lup_ow( L, X_1, U_11 ) )
@out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,0)] = sylv_lup_ow_opt(@m@, min(@nb@,@n@); @op0@[h(@m@,@m@,0), h(@m@,@m@,0)]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,0)], @op2@[h(min(@nb@,@n@),@n@,0), h(min(@nb@,@n@),@n@,0)]#UpperTriangular#);
For[ @it@; @nb@; @n@-(@nb@); @nb@ ]
{
	%% Equal( NL[ X_1 ], Plus( Times( Minus( X_0 ), U_01 ), C_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = -@out0@[h(@m@,@m@,0), h(@it@,@n@,0)] * @op2@[h(@it@,@n@,0), h(@nb@,@n@,@it@)] + @op1@[h(@m@,@m@,0), h(@nb@,@n@,@it@)];
	%% Equal( NL[ X_1 ], sylv_lup_ow( L, X_1, U_11 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = sylv_lup_ow_opt(@m@, @nb@; @op0@[h(@m@,@m@,0), h(@m@,@m@,0)]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)], @op2@[h(@nb@,@n@,@it@), h(@nb@,@n@,@it@)]#UpperTriangular#);
};

