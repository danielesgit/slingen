
For[ @it@; 0; @m@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ B_1 ], ldiv_ltn_ow( L_11, B_1 ) )
	@out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)] = ldiv_ltn_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@nb@,@m@,@m@-(@it@+@nb@))]#LowerTriangular#, @out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)]);
	%% Equal( NL[ B_0 ], Plus( Times( Minus( Transpose( L_10 ) ), B_1 ), B_0 ) )
	@out0@[h(@m@-(@it@+@nb@),@m@,0), h(@n@,@n@,0)] = -trans(@op0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@m@-(@it@+@nb@),@m@,0)]) * @out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)] + @out0@[h(@m@-(@it@+@nb@),@m@,0), h(@n@,@n@,0)];
};
%% Equal( NL[ B_1 ], ldiv_ltn_ow( L_11, B_1 ) )
@out0@[h(@nb@,@m@,@m@-(max(@m@-@nb@, 0)+@nb@)), h(@n@,@n@,0)] = ldiv_ltn_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,@m@-(max(@m@-@nb@, 0)+@nb@)), h(@nb@,@m@,@m@-(max(@m@-@nb@, 0)+@nb@))]#LowerTriangular#, @out0@[h(@nb@,@m@,@m@-(max(@m@-@nb@, 0)+@nb@)), h(@n@,@n@,0)]);

