
% Equal( NL[ B_1 ], rdiv_ln_ow( B_1, L_11 ) )
@out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@)))] = rdiv_ln_ow_opt(@m@, min(@nb@,@n@); @out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@)))], @op1@[h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@))), h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@)))]#LowerTriangular#);
For[ @it@; @nb@; @n@-(@nb@); @nb@ ]
{
	% Equal( NL[ B_1 ], Plus( Times( Minus( B_2 ), L_21 ), A_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] = -@out0@[h(@m@,@m@,0), h(@it@,@n@,@n@-@it@)] * @op1@[h(@it@,@n@,@n@-@it@), h(@nb@,@n@,@n@-(@it@+@nb@))] + @op0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))];
	% Equal( NL[ B_1 ], rdiv_ln_ow( B_1, L_11 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] = rdiv_ln_ow_opt(@m@, @nb@; @out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))], @op1@[h(@nb@,@n@,@n@-(@it@+@nb@)), h(@nb@,@n@,@n@-(@it@+@nb@))]#LowerTriangular#);
};

