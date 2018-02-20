
For[ @it@; 0; @m@-(@nb@); @nb@ ]
{
	%% Equal( NL[ B_1 ], rdiv_ltn_ow( L, A_1 ) )
	@out0@[h(@nb@,@m@,@it@), h(@n@,@n@,0)] = rdiv_ltn_ow_opt(@nb@, @n@; @op0@[h(@n@,@n@,0), h(@n@,@n@,0)]#LowerTriangular#, @op1@[h(@nb@,@m@,@it@), h(@n@,@n@,0)]);
};

