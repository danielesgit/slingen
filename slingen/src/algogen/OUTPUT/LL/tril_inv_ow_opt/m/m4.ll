
%% Equal( NL[ X_11 ], tril_inv_ow( L_11 ) )
@out0@[h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@))), h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@)))]#LowerTriangular# = tril_inv_ow_opt(min(@nb@,@m@), min(@nb@,@m@); @op0@[h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@))), h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@)))]#LowerTriangular#);
%% Equal( NL[ X_10 ], Times( Minus( X_11 ), L_10 ) )
@out0@[h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@))), h(@m@-(0+min(@nb@,@m@)),@m@,0)] = -@out0@[h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@))), h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@)))]#LowerTriangular# * @op0@[h(min(@nb@,@m@),@m@,@m@-(0+min(@nb@,@m@))), h(@m@-(0+min(@nb@,@m@)),@m@,0)];
For[ @it@; @nb@; @m@-(@nb@+1); @nb@ ]
{
	%% Equal( NL[ X_11 ], tril_inv_ow( L_11 ) )
	@out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@nb@,@m@,@m@-(@it@+@nb@))]#LowerTriangular# = tril_inv_ow_opt(@nb@, @nb@; @op0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@nb@,@m@,@m@-(@it@+@nb@))]#LowerTriangular#);
	%% Equal( NL[ X_21 ], Times( X_21, X_11 ) )
	@out0@[h(@it@,@m@,@m@-@it@), h(@nb@,@m@,@m@-(@it@+@nb@))] = @out0@[h(@it@,@m@,@m@-@it@), h(@nb@,@m@,@m@-(@it@+@nb@))] * @out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@nb@,@m@,@m@-(@it@+@nb@))]#LowerTriangular#;
	%% Equal( NL[ X_20 ], Plus( Times( Minus( X_21 ), L_10 ), X_20 ) )
	@out0@[h(@it@,@m@,@m@-@it@), h(@m@-(@it@+@nb@),@m@,0)] = -@out0@[h(@it@,@m@,@m@-@it@), h(@nb@,@m@,@m@-(@it@+@nb@))] * @op0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@m@-(@it@+@nb@),@m@,0)] + @out0@[h(@it@,@m@,@m@-@it@), h(@m@-(@it@+@nb@),@m@,0)];
	%% Equal( NL[ X_10 ], Times( Minus( X_11 ), L_10 ) )
	@out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@m@-(@it@+@nb@),@m@,0)] = -@out0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@nb@,@m@,@m@-(@it@+@nb@))]#LowerTriangular# * @op0@[h(@nb@,@m@,@m@-(@it@+@nb@)), h(@m@-(@it@+@nb@),@m@,0)];
};
%% Equal( NL[ X_11 ], tril_inv_ow( L_11 ) )
@out0@[h(@nb@,@m@,@m@-(max(@m@-@nb@, min(@m@,@nb@))+@nb@)), h(@nb@,@m@,@m@-(max(@m@-@nb@, min(@m@,@nb@))+@nb@))]#LowerTriangular# = tril_inv_ow_opt(@nb@, @nb@; @op0@[h(@nb@,@m@,@m@-(max(@m@-@nb@, min(@m@,@nb@))+@nb@)), h(@nb@,@m@,@m@-(max(@m@-@nb@, min(@m@,@nb@))+@nb@))]#LowerTriangular#);
%% Equal( NL[ X_21 ], Times( X_21, X_11 ) )
@out0@[h(max(@m@-@nb@, min(@m@,@nb@)),@m@,@m@-max(@m@-@nb@, min(@m@,@nb@))), h(@nb@,@m@,@m@-(max(@m@-@nb@, min(@m@,@nb@))+@nb@))] = @out0@[h(max(@m@-@nb@, min(@m@,@nb@)),@m@,@m@-max(@m@-@nb@, min(@m@,@nb@))), h(@nb@,@m@,@m@-(max(@m@-@nb@, min(@m@,@nb@))+@nb@))] * @out0@[h(@nb@,@m@,@m@-(max(@m@-@nb@, min(@m@,@nb@))+@nb@)), h(@nb@,@m@,@m@-(max(@m@-@nb@, min(@m@,@nb@))+@nb@))]#LowerTriangular#;

