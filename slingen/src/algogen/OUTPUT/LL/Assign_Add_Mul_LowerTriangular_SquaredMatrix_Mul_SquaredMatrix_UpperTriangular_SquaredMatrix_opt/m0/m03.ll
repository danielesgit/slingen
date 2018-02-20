
%% Equal( NL[ X_1 ], Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix( L_11, X_1, U ) )
@out0@[h(min(@nb@,@m0@),@m0@,0), h(@m2@,@m2@,0)] = Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix_opt(min(@nb@,@m0@), @m2@; @op0@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]#LowerTriangular#, @out0@[h(min(@nb@,@m0@),@m0@,0), h(@m2@,@m2@,0)], @op2@[h(@m2@,@m2@,0), h(@m2@,@m2@,0)]#UpperTriangular#);
For[ @it@; @nb@; @m0@-(@nb@); @nb@ ]
{
	%% Equal( NL[ X_1 ], Plus( Times( Minus( L_10 ), X_0 ), C_1 ) )
	@out0@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)] = -@op0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)] * @out0@[h(@it@,@m0@,0), h(@m2@,@m2@,0)] + @op1@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)];
	%% Equal( NL[ X_1 ], Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix( L_11, X_1, U ) )
	@out0@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)] = Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix_opt(@nb@, @m2@; @op0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular#, @out0@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)], @op2@[h(@m2@,@m2@,0), h(@m2@,@m2@,0)]#UpperTriangular#);
};

