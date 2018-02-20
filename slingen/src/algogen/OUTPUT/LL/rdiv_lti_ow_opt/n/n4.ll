
For[ @it@; 0; @n@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ B_1 ], rdiv_lti_ow( L_11, B_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = rdiv_lti_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,@it@), h(@nb@,@n@,@it@)]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)]);
	%% Equal( NL[ B_2 ], Plus( Times( Minus( B_1 ), Transpose( L_21 ) ), B_2 ) )
	@out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,@it@+@nb@)] = -@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] * trans(@op0@[h(@n@-(@it@+@nb@),@n@,@it@+@nb@), h(@nb@,@n@,@it@)]) + @out0@[h(@m@,@m@,0), h(@n@-(@it@+@nb@),@n@,@it@+@nb@)];
};
%% Equal( NL[ B_1 ], rdiv_lti_ow( L_11, B_1 ) )
@out0@[h(@m@,@m@,0), h(@nb@,@n@,max(@n@-@nb@, 0))] = rdiv_lti_ow_opt(@m@, @nb@; @op0@[h(@nb@,@n@,max(@n@-@nb@, 0)), h(@nb@,@n@,max(@n@-@nb@, 0))]#LowerTriangular#, @out0@[h(@m@,@m@,0), h(@nb@,@n@,max(@n@-@nb@, 0))]);

