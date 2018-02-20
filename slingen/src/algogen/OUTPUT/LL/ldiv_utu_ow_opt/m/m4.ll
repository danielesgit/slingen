
For[ @it@; 0; @m@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ B_1 ], ldiv_utu_ow( U_11, B_1 ) )
	@out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] = ldiv_utu_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#UpperTriangular#, @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)]);
	%% Equal( NL[ B_2 ], Plus( Times( Minus( Transpose( U_12 ) ), B_1 ), B_2 ) )
	@out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@n@,@n@,0)] = -trans(@op0@[h(@nb@,@m@,@it@), h(@m@-(@it@+@nb@),@m@,@it@+@nb@)]) * @out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] + @out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@n@,@n@,0)];
};
%% Equal( NL[ B_1 ], ldiv_utu_ow( U_11, B_1 ) )
@out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@n@,@n@,0)] = ldiv_utu_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@nb@,@m@,max(@m@-@nb@, 0))]#UpperTriangular#, @out0@[h(@nb@,@m@,max(@m@-@nb@, 0)), h(@n@,@n@,0)]);

