
For[ @it@; 0; @n@-(@nb@); @nb@ ]
{
	%% Equal( NL[ B_1 ], ldiv_uti_ow( U, A_1 ) )
	@out0@[h(@m@,@m@,0), h(@nb@,@n@,@it@)] = ldiv_uti_ow_opt(@m@, @nb@; @op0@[h(@m@,@m@,0), h(@m@,@m@,0)]#UpperTriangular#, @op1@[h(@m@,@m@,0), h(@nb@,@n@,@it@)]);
};

