
For[ @it@; 0; @n@-(@nb@+1); @nb@ ]
{
	% Equal( NL[ B_1 ], rdiv_ln_ow( B_1, L_11 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] = rdiv_ln_ow_opt(@m@, @nb@; @out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))], @op1@[h(@nb@,@n@,@n@-(@it@+@nb@)), h(@nb@,@n@,@n@-(@it@+@nb@))]#LowerTriangular#);
	% Equal( NL[ B_0 ], Plus( Times( Minus( B_1 ), L_10 ), B_0 ) )
	@out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,0)] = -@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] * @op1@[h(@nb@,@n@,@n@-(@it@+@nb@)), h(@n@-(@it@+@nb@),@n@,0)] + @out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,0)];
};
% Equal( NL[ B_1 ], rdiv_ln_ow( B_1, L_11 ) )
@out0@[h(@m@,@m@,0), h(min(@nb@, mod(@n@,@nb@)),@n@,@n@-(max(@n@-mod(@n@,@nb@), 0)+min(@nb@, mod(@n@,@nb@))))] = rdiv_ln_ow_opt(@m@, min(@nb@, mod(@n@,@nb@)); @out0@[h(@m@,@m@,0), h(min(@nb@, mod(@n@,@nb@)),@n@,@n@-(max(@n@-mod(@n@,@nb@), 0)+min(@nb@, mod(@n@,@nb@))))], @op1@[h(min(@nb@, mod(@n@,@nb@)),@n@,@n@-(max(@n@-mod(@n@,@nb@), 0)+min(@nb@, mod(@n@,@nb@)))), h(min(@nb@, mod(@n@,@nb@)),@n@,@n@-(max(@n@-mod(@n@,@nb@), 0)+min(@nb@, mod(@n@,@nb@))))]#LowerTriangular#);

