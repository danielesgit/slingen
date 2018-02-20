
For[ @it@; 0; @n@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ B_1 ], rdiv_unn_ow( U_11, B_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = rdiv_unn_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,@it@), h(@nb@,@n@,@it@)]#UpperTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)]);
	%% Equal( NL[ B_2 ], Plus( Times( Minus( B_1 ), U_12 ), B_2 ) )
	@out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,@it@+@nb@)] = -@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] * @op0@[h(@nb@,@n@,@it@), h(@n@-(@it@+@nb@),@n@,@it@+@nb@)] + @out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,@it@+@nb@)];
};
%% Equal( NL[ B_1 ], rdiv_unn_ow( U_11, B_1 ) )
@out0@[h(@m@,@m@,0), h(@nb@,@n@,max(@n@-@nb@, 0))] = rdiv_unn_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,max(@n@-@nb@, 0)), h(@nb@,@n@,max(@n@-@nb@, 0))]#UpperTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,max(@n@-@nb@, 0))]);

