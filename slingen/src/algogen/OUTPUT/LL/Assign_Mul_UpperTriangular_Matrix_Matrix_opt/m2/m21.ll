
For[ @it@; 0; @m2@-(@nb@); @nb@ ]
{
	%% Equal( NL[ v4_1 ], Assign_Mul_UpperTriangular_Matrix_Matrix( U0, v3_1 ) )
	@out0@[h(@m0@,@m0@,0), h(@nb@,@m2@,@it@)] = Assign_Mul_UpperTriangular_Matrix_Matrix_opt(@m0@, @nb@; @op0@[h(@m0@,@m0@,0), h(@m0@,@m0@,0)]#UpperTriangular#, @op1@[h(@m0@,@m0@,0), h(@nb@,@m2@,@it@)]);
};

