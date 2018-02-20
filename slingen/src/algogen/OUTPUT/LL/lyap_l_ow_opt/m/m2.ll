@T64@: triangular<@m@, u, tinout>;
@T74@: matrix<@nb@, @nb@, tinout>;

%% Equal( NL[ T64_11 ], Transpose( L_11 ) )
@T64@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#UpperTriangular# = trans(@op0@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#LowerTriangular#);
%% Equal( NL[ X_11 ], lyap_l_ow( L_11, X_11 ) )
@out0@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#Symmetric,LSMatAccess# = lyap_l_ow_opt(min(@nb@,@m@), min(@nb@,@m@); @op0@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#LowerTriangular#, @out0@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#Symmetric,LSMatAccess#);
For[ @it@; @nb@; @m@-(@nb@); @nb@ ]
{
	%% Equal( NL[ T64_01 ], Transpose( L_10 ) )
	@T64@[h(@it@,@m@,0), h(@nb@,@m@,@it@)] = trans(@op0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)]);
	%% Equal( NL[ T64_11 ], Transpose( L_11 ) )
	@T64@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#UpperTriangular# = trans(@op0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular#);
	%% Equal( NL[ X_10 ], Plus( Times( Minus( L_10 ), X_00 ), C_10 ) )
	@out0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)] = -@op0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)] * @out0@[h(@it@,@m@,0), h(@it@,@m@,0)]#Symmetric,LSMatAccess# + @op1@[h(@nb@,@m@,@it@), h(@it@,@m@,0)];
	%% Equal( NL[ X_10 ], sylv_lup_ow( L_11, X_10, T64_00 ) )
	@out0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)] = sylv_lup_ow_opt(@nb@, @it@; @op0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular#, @out0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)], @T64@[h(@it@,@m@,0), h(@it@,@m@,0)]#UpperTriangular#);
	%% Equal( NL[ T74 ], Plus( Times( Minus( L_10 ), Transpose( X_10 ) ), C_11 ) )
	@T74@[h(@nb@,@nb@,0), h(@nb@,@nb@,0)] = -@op0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)] * trans(@out0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)]) + @op1@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#Symmetric,LSMatAccess#;
	%% Equal( NL[ X_11 ], Plus( Times( Minus( X_10 ), T64_01 ), T74 ) )
	@out0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#Symmetric,LSMatAccess# = -@out0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)] * @T64@[h(@it@,@m@,0), h(@nb@,@m@,@it@)] + @T74@[h(@nb@,@nb@,0), h(@nb@,@nb@,0)];
	%% Equal( NL[ X_11 ], lyap_l_ow( L_11, X_11 ) )
	@out0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#Symmetric,LSMatAccess# = lyap_l_ow_opt(@nb@, @nb@; @op0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular#, @out0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#Symmetric,LSMatAccess#);
};

