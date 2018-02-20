
%% Equal( NL[ B_1 ], rdiv_lnu_ow( L_11, B_1 ) )
@out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@)))] = rdiv_lnu_ow_opt(@m@, min(@nb@,@n@); @op0@[h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@))), h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@)))]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@)))]);
For[ @it@; @nb@; @n@-(@nb@); @nb@ ]
{
	%% Equal( NL[ B_1 ], Plus( Times( Minus( B_2 ), L_21 ), A_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] = -@out0@[h(@m@,@m@,0), h(@it@,@n@,@n@-@it@)] * @op0@[h(@it@,@n@,@n@-@it@), h(@nb@,@n@,@n@-(@it@+@nb@))] + @op1@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))];
	%% Equal( NL[ B_1 ], rdiv_lnu_ow( L_11, B_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] = rdiv_lnu_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,@n@-(@it@+@nb@)), h(@nb@,@n@,@n@-(@it@+@nb@))]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))]);
};

