
For[ @it@; 0; @m@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ B_1 ], ldiv_un_ow( B_1, U_11 ) )
	@out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)] = ldiv_un_ow_opt(@nb@, @n@; @out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)], @op1@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@nb@,@m@,@m@-(@it@+@nb@))]#UpperTriangular#);
	%% Equal( NL[ B_0 ], Plus( Times( Minus( U_01 ), B_1 ), B_0 ) )
	@out0@[h(@m@-(@it@+@nb@),@m@,0), h(@n@,@n@,0)] = -@op1@[h(@m@-(@it@+@nb@),@m@,0), h(@nb@,@m@,@m@-(@it@+@nb@))] * @out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)] + @out0@[h(@m@-(@it@+@nb@),@m@,0), h(@n@,@n@,0)];
};
%% Equal( NL[ B_1 ], ldiv_un_ow( B_1, U_11 ) )
@out0@[h(@nb@,@m@,@m@-(max(@m@-@nb@, 0)+@nb@)), h(@n@,@n@,0)] = ldiv_un_ow_opt(@nb@, @n@; @out0@[h(@nb@,@m@,@m@-(max(@m@-@nb@, 0)+@nb@)), h(@n@,@n@,0)], @op1@[h(@nb@,@m@,@m@-(max(@m@-@nb@, 0)+@nb@)), h(@nb@,@m@,@m@-(max(@m@-@nb@, 0)+@nb@))]#UpperTriangular#);

