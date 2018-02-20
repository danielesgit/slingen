
For[ @it@; 0; @m2@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ X_1 ], Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix( L, X_1, U_11 ) )
	@out0@[h(@m0@,@m0@,0), h(@nb@,@m2@,@it@)] = Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix_opt(@m0@, @nb@; @op0@[h(@m0@,@m0@,0), h(@m0@,@m0@,0)]#LowerTriangular#, @out0@[h(@m0@,@m0@,0), h(@nb@,@m2@,@it@)], @op2@[h(@nb@,@m2@,@it@), h(@nb@,@m2@,@it@)]#UpperTriangular#);
	%% Equal( NL[ X_2 ], Plus( Times( Minus( X_1 ), U_12 ), X_2 ) )
	@out0@[h(@m0@,@m0@,0), h(@m2@-(@it@+@nb@),@m2@,@it@+@nb@)] = -@out0@[h(@m0@,@m0@,0), h(@nb@,@m2@,@it@)] * @op2@[h(@nb@,@m2@,@it@), h(@m2@-(@it@+@nb@),@m2@,@it@+@nb@)] + @out0@[h(@m0@,@m0@,0), h(@m2@-(@it@+@nb@),@m2@,@it@+@nb@)];
};
%% Equal( NL[ X_1 ], Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix( L, X_1, U_11 ) )
@out0@[h(@m0@,@m0@,0), h(@nb@,@m2@,max(@m2@-@nb@, 0))] = Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix_opt(@m0@, @nb@; @op0@[h(@m0@,@m0@,0), h(@m0@,@m0@,0)]#LowerTriangular#, @out0@[h(@m0@,@m0@,0), h(@nb@,@m2@,max(@m2@-@nb@, 0))], @op2@[h(@nb@,@m2@,max(@m2@-@nb@, 0)), h(@nb@,@m2@,max(@m2@-@nb@, 0))]#UpperTriangular#);

