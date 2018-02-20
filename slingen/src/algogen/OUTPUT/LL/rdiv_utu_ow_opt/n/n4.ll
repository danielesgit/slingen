
For[ @it@; 0; @n@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ B_1 ], rdiv_utu_ow( U_11, B_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] = rdiv_utu_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,@n@-(@it@+@nb@)), h(@nb@,@n@,@n@-(@it@+@nb@))]#UpperTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))]);
	%% Equal( NL[ B_0 ], Plus( Times( Minus( B_1 ), Transpose( U_01 ) ), B_0 ) )
	@out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,0)] = -@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] * trans(@op0@[h(@n@-(@it@+@nb@),@n@,0), h(@nb@,@n@,@n@-(@it@+@nb@))]) + @out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,0)];
};
%% Equal( NL[ B_1 ], rdiv_utu_ow( U_11, B_1 ) )
@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(max(@n@-@nb@, 0)+@nb@))] = rdiv_utu_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,@n@-(max(@n@-@nb@, 0)+@nb@)), h(@nb@,@n@,@n@-(max(@n@-@nb@, 0)+@nb@))]#UpperTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(max(@n@-@nb@, 0)+@nb@))]);

