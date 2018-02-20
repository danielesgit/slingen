
%% Equal( NL[ L_11, U_11 ], Assign_Mul_LowerUnitTriangular_UpperTriangular_SquaredMatrix( A_11 ) )
[@out0@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]#LowerTriangular#, @out1@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]#UpperTriangular#] = Assign_Mul_LowerUnitTriangular_UpperTriangular_SquaredMatrix_opt(min(@nb@,@m0@), min(@nb@,@m0@); @op0@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]);
%% Equal( NL[ U_12 ], ldiv_lni_ow( L_11, U_12 ) )
@out1@[h(min(@nb@,@m0@),@m0@,0), h(@m0@-(0+min(@nb@,@m0@)),@m0@,0+min(@nb@,@m0@))] = ldiv_lni_ow_opt(min(@nb@,@m0@), @m0@-(0+min(@nb@,@m0@)); @out0@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]#LowerTriangular#, @out1@[h(min(@nb@,@m0@),@m0@,0), h(@m0@-(0+min(@nb@,@m0@)),@m0@,0+min(@nb@,@m0@))]);
For[ @it@; @nb@; @m0@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ L_10 ], rdiv_unn_ow( U_00, A_10 ) )
	@out0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)] = rdiv_unn_ow_opt(@nb@, @it@; @out1@[h(@it@,@m0@,0), h(@it@,@m0@,0)]#UpperTriangular#, @op0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)]);
	%% Equal( NL[ A_11 ], Plus( Times( Minus( L_10 ), U_01 ), A_11 ) )
	@op0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)] = @op0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)] + -@out0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)] * @out1@[h(@it@,@m0@,0), h(@nb@,@m0@,@it@)];
	%% Equal( NL[ L_11, U_11 ], Assign_Mul_LowerUnitTriangular_UpperTriangular_SquaredMatrix( A_11 ) )
	[@out0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular#, @out1@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#UpperTriangular#] = Assign_Mul_LowerUnitTriangular_UpperTriangular_SquaredMatrix_opt(@nb@, @nb@; @op0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]);
	%% Equal( NL[ U_12 ], Plus( Times( Minus( L_10 ), U_02 ), A_12 ) )
	@out1@[h(@nb@,@m0@,@it@), h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@)] = @op0@[h(@nb@,@m0@,@it@), h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@)] + -@out0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)] * @out1@[h(@it@,@m0@,0), h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@)];
	%% Equal( NL[ U_12 ], ldiv_lni_ow( L_11, U_12 ) )
	@out1@[h(@nb@,@m0@,@it@), h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@)] = ldiv_lni_ow_opt(@nb@, @m0@-(@it@+@nb@); @out0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular#, @out1@[h(@nb@,@m0@,@it@), h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@)]);
};
%% Equal( NL[ L_10 ], rdiv_unn_ow( U_00, A_10 ) )
@out0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(max(@m0@-@nb@, min(@m0@,@nb@)),@m0@,0)] = rdiv_unn_ow_opt(@nb@, max(@m0@-@nb@, min(@m0@,@nb@)); @out1@[h(max(@m0@-@nb@, min(@m0@,@nb@)),@m0@,0), h(max(@m0@-@nb@, min(@m0@,@nb@)),@m0@,0)]#UpperTriangular#, @op0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(max(@m0@-@nb@, min(@m0@,@nb@)),@m0@,0)]);
%% Equal( NL[ A_11 ], Plus( Times( Minus( L_10 ), U_01 ), A_11 ) )
@op0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))] = @op0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))] + -@out0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(max(@m0@-@nb@, min(@m0@,@nb@)),@m0@,0)] * @out1@[h(max(@m0@-@nb@, min(@m0@,@nb@)),@m0@,0), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))];
%% Equal( NL[ L_11, U_11 ], Assign_Mul_LowerUnitTriangular_UpperTriangular_SquaredMatrix( A_11 ) )
[@out0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))]#LowerTriangular#, @out1@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))]#UpperTriangular#] = Assign_Mul_LowerUnitTriangular_UpperTriangular_SquaredMatrix_opt(@nb@, @nb@; @op0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))]);

