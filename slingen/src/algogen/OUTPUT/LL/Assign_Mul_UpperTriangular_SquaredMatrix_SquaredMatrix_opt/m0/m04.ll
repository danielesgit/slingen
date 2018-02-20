
For[ @it@; 0; @m0@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ M8_1 ], Assign_Mul_UpperTriangular_SquaredMatrix_SquaredMatrix( U0_11, M8_1 ) )
	@out0@[h(@nb@,@m0@,@m0@-(@it@+@nb@)), h(@m2@,@m2@,0)] = Assign_Mul_UpperTriangular_SquaredMatrix_SquaredMatrix_opt(@nb@, @m2@; @op0@[h(@nb@,@m0@,@m0@-(@it@+@nb@)), h(@nb@,@m0@,@m0@-(@it@+@nb@))]#UpperTriangular#, @out0@[h(@nb@,@m0@,@m0@-(@it@+@nb@)), h(@m2@,@m2@,0)]);
	%% Equal( NL[ M8_0 ], Plus( Times( Minus( U0_01 ), M8_1 ), M8_0 ) )
	@out0@[h(@m0@-(@it@+@nb@),@m0@,0), h(@m2@,@m2@,0)] = -@op0@[h(@m0@-(@it@+@nb@),@m0@,0), h(@nb@,@m0@,@m0@-(@it@+@nb@))] * @out0@[h(@nb@,@m0@,@m0@-(@it@+@nb@)), h(@m2@,@m2@,0)] + @out0@[h(@m0@-(@it@+@nb@),@m0@,0), h(@m2@,@m2@,0)];
};
%% Equal( NL[ M8_1 ], Assign_Mul_UpperTriangular_SquaredMatrix_SquaredMatrix( U0_11, M8_1 ) )
@out0@[h(@nb@,@m0@,@m0@-(max(@m0@-@nb@, 0)+@nb@)), h(@m2@,@m2@,0)] = Assign_Mul_UpperTriangular_SquaredMatrix_SquaredMatrix_opt(@nb@, @m2@; @op0@[h(@nb@,@m0@,@m0@-(max(@m0@-@nb@, 0)+@nb@)), h(@nb@,@m0@,@m0@-(max(@m0@-@nb@, 0)+@nb@))]#UpperTriangular#, @out0@[h(@nb@,@m0@,@m0@-(max(@m0@-@nb@, 0)+@nb@)), h(@m2@,@m2@,0)]);

