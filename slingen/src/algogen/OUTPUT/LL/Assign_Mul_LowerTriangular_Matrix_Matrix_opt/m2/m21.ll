
For[ @it@; 0; @m2@-(@nb@); @nb@ ]
{
	%% Equal( NL[ t0_1 ], Assign_Mul_LowerTriangular_Matrix_Matrix( L0, y_1 ) )
	@out0@[h(@m0@,@m0@,0), h(@nb@,@m2@,@it@)] = Assign_Mul_LowerTriangular_Matrix_Matrix_opt(@m0@, @nb@; @op0@[h(@m0@,@m0@,0), h(@m0@,@m0@,0)]#LowerTriangular#, @op1@[h(@m0@,@m0@,0), h(@nb@,@m2@,@it@)]);
};

