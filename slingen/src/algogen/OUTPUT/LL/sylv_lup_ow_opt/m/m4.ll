
For[ @it@; 0; @m@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ X_1 ], sylv_lup_ow( L_11, X_1, U ) )
	@out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] = sylv_lup_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular#, @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)], @op2@[h(@n@,@n@,0), h(@n@,@n@,0)]#UpperTriangular#);
	%% Equal( NL[ X_2 ], Plus( Times( Minus( L_21 ), X_1 ), X_2 ) )
	@out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@n@,@n@,0)] = -@op0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@nb@,@m@,@it@)] * @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] + @out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@n@,@n@,0)];
};
%% Equal( NL[ X_1 ], sylv_lup_ow( L_11, X_1, U ) )
@out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@n@,@n@,0)] = sylv_lup_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@nb@,@m@,max(@m@-@nb@, 0))]#LowerTriangular#, @out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@n@,@n@,0)], @op2@[h(@n@,@n@,0), h(@n@,@n@,0)]#UpperTriangular#);

