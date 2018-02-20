
For[ @it@; 0; @m@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ B_1 ], ldiv_ut_ow( B_1, U_11 ) )
	@out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] = ldiv_ut_ow_opt(@nb@, @n@; @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)], @op1@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#UpperTriangular#);
	%% Equal( NL[ B_2 ], Plus( Times( Minus( Transpose( U_12 ) ), B_1 ), B_2 ) )
	@out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@n@,@n@,0)] = -trans(@op1@[h(@nb@,@m@,@it@), h(@m@-(@it@+@nb@),@m@,@it@+@nb@)]) * @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] + @out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@n@,@n@,0)];
};
%% Equal( NL[ B_1 ], ldiv_ut_ow( B_1, U_11 ) )
@out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@n@,@n@,0)] = ldiv_ut_ow_opt(@nb@, @n@; @out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@n@,@n@,0)], @op1@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@nb@,@m@,max(@m@-@nb@, 0))]#UpperTriangular#);

