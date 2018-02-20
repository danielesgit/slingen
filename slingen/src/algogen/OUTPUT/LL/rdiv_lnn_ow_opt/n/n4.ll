
For[ @it@; 0; @n@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ B_1 ], rdiv_lnn_ow( L_11, B_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] = rdiv_lnn_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,@n@-(@it@+@nb@)), h(@nb@,@n@,@n@-(@it@+@nb@))]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))]);
	%% Equal( NL[ B_0 ], Plus( Times( Minus( B_1 ), L_10 ), B_0 ) )
	@out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,0)] = -@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] * @op0@[h(@nb@,@n@,@n@-(@it@+@nb@)), h(@n@-(@it@+@nb@),@n@,0)] + @out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,0)];
};
%% Equal( NL[ B_1 ], rdiv_lnn_ow( L_11, B_1 ) )
@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(max(@n@-@nb@, 0)+@nb@))] = rdiv_lnn_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,@n@-(max(@n@-@nb@, 0)+@nb@)), h(@nb@,@n@,@n@-(max(@n@-@nb@, 0)+@nb@))]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(max(@n@-@nb@, 0)+@nb@))]);

