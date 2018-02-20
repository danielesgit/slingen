
%% Equal( NL[ L_11 ], Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric( L_11 ) )
@out0@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]#LowerTriangular# = Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric_opt(min(@nb@,@m0@), min(@nb@,@m0@); @out0@[h(min(@nb@,@m0@),@m0@,0), h(min(@nb@,@m0@),@m0@,0)]#LowerTriangular#);
For[ @it@; @nb@; @m0@-(@nb@); @nb@ ]
{
	%% Equal( NL[ L_10 ], rdiv_ltn_ow( L_00, K_10 ) )
	@out0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)] = rdiv_ltn_ow_opt(@nb@, @it@; @out0@[h(@it@,@m0@,0), h(@it@,@m0@,0)]#LowerTriangular#, @op0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)]);
	%% Equal( NL[ L_11 ], Plus( Times( Minus( L_10 ), Transpose( L_10 ) ), K_11 ) )
	@out0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular# = @op0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#Symmetric,LSMatAccess# + -@out0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)] * trans(@out0@[h(@nb@,@m0@,@it@), h(@it@,@m0@,0)]);
	%% Equal( NL[ L_11 ], Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric( L_11 ) )
	@out0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular# = Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric_opt(@nb@, @nb@; @out0@[h(@nb@,@m0@,@it@), h(@nb@,@m0@,@it@)]#LowerTriangular#);
};

