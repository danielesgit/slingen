
For[ @it@; 0; @n@-(@nb@); @nb@ ]
{
	%% Equal( NL[ B_1 ], ldiv_ut_ow( A_1, U ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = ldiv_ut_ow_opt(@m@, @nb@; @op0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)], @op1@[h(@m@,@m@,0), h(@m@,@m@,0)]#UpperTriangular#);
};

