
%% Equal( NL[ B_1 ], rdiv_uti_ow( U_11, B_1 ) )
@out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@)))] = rdiv_uti_ow_opt(@m@, min(@nb@,@n@); @op0@[h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@))), h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@)))]#UpperTriangular#, @out0@[h(@m@,@m@,0), h(min(@nb@,@n@),@n@,@n@-(0+min(@nb@,@n@)))]);
For[ @it@; @nb@; @n@-(@nb@); @nb@ ]
{
	%% Equal( NL[ B_1 ], Plus( Times( Minus( B_2 ), Transpose( U_12 ) ), A_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] = -@out0@[h(@m@,@m@,0), h(@it@,@n@,@n@-@it@)] * trans(@op0@[h(@nb@,@n@,@n@-(@it@+@nb@)), h(@it@,@n@,@n@-@it@)]) + @op1@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))];
	%% Equal( NL[ B_1 ], rdiv_uti_ow( U_11, B_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))] = rdiv_uti_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,@n@-(@it@+@nb@)), h(@nb@,@n@,@n@-(@it@+@nb@))]#UpperTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@n@-(@it@+@nb@))]);
};

