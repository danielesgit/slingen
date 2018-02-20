
For[ @it@; 0; @m0@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ t0_1 ], Assign_Mul_LowerTriangular_Matrix_Matrix( L0_11, t0_1 ) )
	@out0@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)] = Assign_Mul_LowerTriangular_Matrix_Matrix_opt(@nb@, @m2@; @op0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular#, @out0@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)]);
	%% Equal( NL[ t0_2 ], Plus( Times( Minus( L0_21 ), t0_1 ), t0_2 ) )
	@out0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@m2@,@m2@,0)] = @out0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@m2@,@m2@,0)] + -@op0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@nb@,@m0@,@it@)] * @out0@[h(@nb@,@m0@,@it@), h(@m2@,@m2@,0)];
};
%% Equal( NL[ t0_1 ], Assign_Mul_LowerTriangular_Matrix_Matrix( L0_11, t0_1 ) )
@out0@[h(@nb@,@m0@,max(@m0@-@nb@, 0)), h(@m2@,@m2@,0)] = Assign_Mul_LowerTriangular_Matrix_Matrix_opt(@nb@, @m2@; @op0@[h(@nb@,@m0@,max(@m0@-@nb@, 0)), h(@nb@,@m0@,max(@m0@-@nb@, 0))]#LowerTriangular#, @out0@[h(@nb@,@m0@,max(@m0@-@nb@, 0)), h(@m2@,@m2@,0)]);

