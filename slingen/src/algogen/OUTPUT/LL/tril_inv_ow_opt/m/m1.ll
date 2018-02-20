
%% Equal( NL[ X_11 ], tril_inv_ow( L_11 ) )
@out0@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#LowerTriangular# = tril_inv_ow_opt(min(@nb@,@m@), min(@nb@,@m@); @op0@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#LowerTriangular#);
%% Equal( NL[ X_21 ], Times( L_21, X_11 ) )
@out0@[h(@m@-(0+min(@nb@,@m@)),@m@,0+min(@nb@,@m@)), h(min(@nb@,@m@),@m@,0)] = @op0@[h(@m@-(0+min(@nb@,@m@)),@m@,0+min(@nb@,@m@)), h(min(@nb@,@m@),@m@,0)] * @out0@[h(min(@nb@,@m@),@m@,0), h(min(@nb@,@m@),@m@,0)]#LowerTriangular#;
For[ @it@; @nb@; @m@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ X_11 ], tril_inv_ow( L_11 ) )
	@out0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular# = tril_inv_ow_opt(@nb@, @nb@; @op0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular#);
	%% Equal( NL[ X_21 ], Times( L_21, X_11 ) )
	@out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@nb@,@m@,@it@)] = @op0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@nb@,@m@,@it@)] * @out0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular#;
	%% Equal( NL[ X_20 ], Plus( Times( Minus( X_21 ), X_10 ), X_20 ) )
	@out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@it@,@m@,0)] = -@out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@nb@,@m@,@it@)] * @out0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)] + @out0@[h(@m@-(@it@+@nb@),@m@,@it@+@nb@), h(@it@,@m@,0)];
	%% Equal( NL[ X_10 ], Times( Minus( X_11 ), X_10 ) )
	@out0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)] = -@out0@[h(@nb@,@m@,@it@), h(@nb@,@m@,@it@)]#LowerTriangular# * @out0@[h(@nb@,@m@,@it@), h(@it@,@m@,0)];
};
%% Equal( NL[ X_11 ], tril_inv_ow( L_11 ) )
@out0@[h(@nb@,@m@,max(@m@-@nb@, min(@m@,@nb@))), h(@nb@,@m@,max(@m@-@nb@, min(@m@,@nb@)))]#LowerTriangular# = tril_inv_ow_opt(@nb@, @nb@; @op0@[h(@nb@,@m@,max(@m@-@nb@, min(@m@,@nb@))), h(@nb@,@m@,max(@m@-@nb@, min(@m@,@nb@)))]#LowerTriangular#);
%% Equal( NL[ X_10 ], Times( Minus( X_11 ), X_10 ) )
@out0@[h(@nb@,@m@,max(@m@-@nb@, min(@m@,@nb@))), h(max(@m@-@nb@, min(@m@,@nb@)),@m@,0)] = -@out0@[h(@nb@,@m@,max(@m@-@nb@, min(@m@,@nb@))), h(@nb@,@m@,max(@m@-@nb@, min(@m@,@nb@)))]#LowerTriangular# * @out0@[h(@nb@,@m@,max(@m@-@nb@, min(@m@,@nb@))), h(max(@m@-@nb@, min(@m@,@nb@)),@m@,0)];

