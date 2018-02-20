
For[ @it@; 0; @m2@-(@nb@); @nb@ ]
{
	%% Equal( NL[ M6_1 ], Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix( U0, M5_1 ) )
	@out0@[h(@m0@,@m0@,0), h(@nb@,@m2@,@it@)] = Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix_opt(@m0@, @nb@; @op0@[h(@m0@,@m0@,0), h(@m0@,@m0@,0)]#UpperTriangular#, @op1@[h(@m0@,@m0@,0), h(@nb@,@m2@,@it@)]);
};

