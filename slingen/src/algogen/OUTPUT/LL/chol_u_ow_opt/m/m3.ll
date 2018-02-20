
For[ @it@; 0; @m@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ U_11 ], chol_u_ow( U_11 ) )
	@out0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#UpperTriangular# = chol_u_ow_opt(@nb@, @nb@; @out0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#UpperTriangular#);
	%% Equal( NL[ U_12 ], ldiv_ut_ow( U_12, U_11 ) )
	@out0@[h(@nb@,@m@,@it@), h(@m@-(@it@+@nb@),@m@,@it@+@nb@)] = ldiv_ut_ow_opt(@nb@, @m@-(@it@+@nb@); @out0@[h(@nb@,@m@,@it@), h(@m@-(@it@+@nb@),@m@,@it@+@nb@)], @out0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#UpperTriangular#);
	%% Equal( NL[ U_22 ], Plus( Times( Minus( Transpose( U_12 ) ), U_12 ), U_22 ) )
	@out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@m@-(@it@+@nb@),@m@,@it@+@nb@)]#UpperTriangular# = -trans(@out0@[h(@nb@,@m@,@it@), h(@m@-(@it@+@nb@),@m@,@it@+@nb@)]) * @out0@[h(@nb@,@m@,@it@), h(@m@-(@it@+@nb@),@m@,@it@+@nb@)] + @out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@m@-(@it@+@nb@),@m@,@it@+@nb@)]#UpperTriangular#;
};
%% Equal( NL[ U_11 ], chol_u_ow( U_11 ) )
@out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@nb@,@m@,max(@m@-@nb@, 0))]#UpperTriangular# = chol_u_ow_opt(@nb@, @nb@; @out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@nb@,@m@,max(@m@-@nb@, 0))]#UpperTriangular#);

