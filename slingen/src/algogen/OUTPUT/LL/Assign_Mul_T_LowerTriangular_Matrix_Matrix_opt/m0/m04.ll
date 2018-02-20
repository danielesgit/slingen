
For[ @it@; 0; @m0@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ a_1 ], Assign_Mul_T_LowerTriangular_Matrix_Matrix( L0_11, a_1 ) )
	@out0@[h(@nb@,@m0@,@m0@-(@it@+@nb@)), h(@m2@,@m2@,0)] = Assign_Mul_T_LowerTriangular_Matrix_Matrix_opt(@nb@, @m2@; @op0@[h(@nb@,@m0@,@m0@-(@it@+@nb@)), h(@nb@,@m0@,@m0@-(@it@+@nb@))]#LowerTriangular#, @out0@[h(@nb@,@m0@,@m0@-(@it@+@nb@)), h(@m2@,@m2@,0)]);
	%% Equal( NL[ a_0 ], Plus( Times( Minus( Transpose( L0_10 ) ), a_1 ), a_0 ) )
	@out0@[h(@m0@-(@it@+@nb@),@m0@,0), h(@m2@,@m2@,0)] = @out0@[h(@m0@-(@it@+@nb@),@m0@,0), h(@m2@,@m2@,0)] + -trans(@op0@[h(@nb@,@m0@,@m0@-(@it@+@nb@)), h(@m0@-(@it@+@nb@),@m0@,0)]) * @out0@[h(@nb@,@m0@,@m0@-(@it@+@nb@)), h(@m2@,@m2@,0)];
};
%% Equal( NL[ a_1 ], Assign_Mul_T_LowerTriangular_Matrix_Matrix( L0_11, a_1 ) )
@out0@[h(@nb@,@m0@,@m0@-(max(@m0@-@nb@, 0)+@nb@)), h(@m2@,@m2@,0)] = Assign_Mul_T_LowerTriangular_Matrix_Matrix_opt(@nb@, @m2@; @op0@[h(@nb@,@m0@,@m0@-(max(@m0@-@nb@, 0)+@nb@)), h(@nb@,@m0@,@m0@-(max(@m0@-@nb@, 0)+@nb@))]#LowerTriangular#, @out0@[h(@nb@,@m0@,@m0@-(max(@m0@-@nb@, 0)+@nb@)), h(@m2@,@m2@,0)]);

