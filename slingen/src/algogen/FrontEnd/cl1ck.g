@@eol_comments :: /#.*?$/

program = header:header declarations:declarations equations:equations $ ;

header = "program" name:id ;
declarations = { @+:declaration } ;
equations = { @+:equation } ;

declaration = (vartype:"Scalar" name:id "<" iotype:io ">" ";")
            | (vartype:"Vector" name:id dims:dim_vector "<" iotype:io ["," ow:ow] ">" ";")
            | (vartype:"Matrix" name:id dims:dim_matrix "<" iotype:io { "," props+:prop } ["," ow:ow] ">" ";") ;
equation = lhs:expression "=" rhs:expression ";" ;

dim_vector = "(" @+:id ")" ;
dim_matrix = "(" @+:id "," @+:id ")";
io = "Input" | "Output";
prop = @:"Square" | @:"Rectangular"
     | @:"Diagonal" | @:"LowerTriangular" | @:"UpperTriangular" | @:"UnitDiagonal" | @:"ImplicitUnitDiagonal"
     | @:"Symmetric" | @:"Non-singular" | @:"SPD"
     | @:"LowerStorage" | @: "UpperStorage" ;
ow = "overwrites" "(" @:id ")" ;

expression = args:term { ops+:("+" | "-") args:term }+ | @:term ;
term =  ops+:"-" args+:term | args:factor { ops+:"*" args:factor }+ | @:factor ;
factor = "(" @:expression ")" | func:unary "(" arg:expression  ")" |
         @:id | @:constant ;
unary = "trans" | "inv";

id = ?/[a-zA-Z][a-zA-Z0-9_]*/? ;
constant = ?/[0-9]+(\.[0-9]+)?([Ee][+-]?[0-9]+)?/? ;
