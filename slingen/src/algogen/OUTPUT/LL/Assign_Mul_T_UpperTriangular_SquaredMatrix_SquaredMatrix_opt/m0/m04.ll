
For[ @it@; 0; @m0@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ M6_1 ], Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix( U0_11, M6_1 ) )
	@out0@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)] = Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix_opt(@nb@, @m2@; @op0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#UpperTriangular#, @out0@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)]);
	%% Equal( NL[ M6_2 ], Plus( Times( Minus( Transpose( U0_12 ) ), M6_1 ), M6_2 ) )
	@out0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@m2@,@m2@,0)] = -trans(@op0@[h(@nb@,@m0@,@it@), h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@)]) * @out0@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)] + @out0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@m2@,@m2@,0)];
};
%% Equal( NL[ M6_1 ], Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix( U0_11, M6_1 ) )
@out0@[h(@nb@,@m0@,max(@m0@-@nb@, 0)), h(@m2@,@m2@,0)] = Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix_opt(@nb@, @m2@; @op0@[h(@nb@,@m0@,max(@m0@-@nb@, 0)), h(@nb@,@m0@,max(@m0@-@nb@, 0))]#UpperTriangular#, @out0@[h(@nb@,@m0@,max(@m0@-@nb@, 0)), h(@m2@,@m2@,0)]);

