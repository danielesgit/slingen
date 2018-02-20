
%% Equal( NL[ B_1 ], ldiv_unu_ow( U_11, B_1 ) )
@out0@[h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@))), h(@n@,@n@,0)] = ldiv_unu_ow_opt(min(@nb@,@m@), @n@; @op0@[h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@))), h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@)))]#UpperTriangular#, @out0@[h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@))), h(@n@,@n@,0)]);
For[ @it@; @nb@; @m@-(@nb@); @nb@ ]
{
	%% Equal( NL[ B_1 ], Plus( Times( Minus( U_12 ), B_2 ), A_1 ) )
	@out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)] = -@op0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@it@,@m@,@m@-@it@)] * @out0@[h(@it@,@m@,@m@-@it@), h(@n@,@n@,0)] + @op1@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)];
	%% Equal( NL[ B_1 ], ldiv_unu_ow( U_11, B_1 ) )
	@out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)] = ldiv_unu_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@nb@,@m@,@m@-(@it@+@nb@))]#UpperTriangular#, @out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)]);
};

