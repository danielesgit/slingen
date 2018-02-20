
%% Equal( NL[ L_11 ], Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric( L_11 ) )
@out0@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]#LowerTriangular# = Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric_opt(min(@nb@,@m0@), min(@nb@,@m0@); @out0@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]#LowerTriangular#);
%% Equal( NL[ L_21 ], rdiv_ltn_ow( L_11, L_21 ) )
@out0@[h(@m0@-(0+min(@nb@,@m0@)),@m0@,0+min(@nb@,@m0@)), h(min(@nb@,@m0@),@m0@,0)] = rdiv_ltn_ow_opt(@m0@-(0+min(@nb@,@m0@)), min(@nb@,@m0@); @out0@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]#LowerTriangular#, @out0@[h(@m0@-(0+min(@nb@,@m0@)),@m0@,0+min(@nb@,@m0@)), h(min(@nb@,@m0@),@m0@,0)]);
For[ @it@; @nb@; @m0@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ L_11 ], Plus( Times( Minus( L_10 ), Transpose( L_10 ) ), K_11 ) )
	@out0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular# = @op0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#Symmetric,LSMatAccess# + -@out0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)] * trans(@out0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)]);
	%% Equal( NL[ L_11 ], Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric( L_11 ) )
	@out0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular# = Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric_opt(@nb@, @nb@; @out0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular#);
	%% Equal( NL[ L_21 ], Plus( Times( Minus( L_20 ), Transpose( L_10 ) ), K_21 ) )
	@out0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@nb@,@m0@,@it@)] = @op0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@nb@,@m0@,@it@)] + -@out0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@it@,@m0@,0)] * trans(@out0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)]);
	%% Equal( NL[ L_21 ], rdiv_ltn_ow( L_11, L_21 ) )
	@out0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@nb@,@m0@,@it@)] = rdiv_ltn_ow_opt(@m0@-(@it@+@nb@), @nb@; @out0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular#, @out0@[h(@m0@-(@it@+@nb@),@m0@,@it@+@nb@), h(@nb@,@m0@,@it@)]);
};
%% Equal( NL[ L_11 ], Plus( Times( Minus( L_10 ), Transpose( L_10 ) ), K_11 ) )
@out0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))]#LowerTriangular# = @op0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))]#Symmetric,LSMatAccess# + -@out0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(max(@m0@-@nb@, min(@m0@,@nb@)),@m0@,0)] * trans(@out0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(max(@m0@-@nb@, min(@m0@,@nb@)),@m0@,0)]);
%% Equal( NL[ L_11 ], Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric( L_11 ) )
@out0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))]#LowerTriangular# = Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric_opt(@nb@, @nb@; @out0@[h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@))), h(@nb@,@m0@,max(@m0@-@nb@, min(@m0@,@nb@)))]#LowerTriangular#);

