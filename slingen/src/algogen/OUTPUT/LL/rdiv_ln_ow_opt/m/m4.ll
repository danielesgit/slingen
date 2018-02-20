
For[ @it@; 0; @m@-(@nb@); @nb@ ]
{
	% Equal( NL[ B_1 ], rdiv_ln_ow( A_1, L ) )
	@out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)] = rdiv_ln_ow_opt(@nb@, @n@; @op0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@n@,@n@,0)], @op1@[h(@n@,@n@,0), h(@n@,@n@,0)]#LowerTriangular#);
};

