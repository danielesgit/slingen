from core.expression import Equal, Times, Minus, Inverse, Transpose, NList, Predicate, PatternDot
import core.properties as props
from core.functional import RewriteRule, Constraint, Replacement

import Config
import PredicateMetadata as pm

pm.DB["ldiv_lni"] = pm.PredicateMetadata( "ldiv_lni", tuple() )
pm.DB["ldiv_lni"].overwrite = []
pm.DB["ldiv_lni_ow"] = pm.PredicateMetadata( "ldiv_lni_ow", tuple() )
pm.DB["ldiv_lni_ow"].overwrite = [(1,0)]
pm.DB["ldiv_lnn"] = pm.PredicateMetadata( "ldiv_lnn", tuple() )
pm.DB["ldiv_lnn"].overwrite = []
pm.DB["ldiv_lnn_ow"] = pm.PredicateMetadata( "ldiv_lnn_ow", tuple() )
pm.DB["ldiv_lnn_ow"].overwrite = [(1,0)]
pm.DB["ldiv_lnu"] = pm.PredicateMetadata( "ldiv_lnu", tuple() )
pm.DB["ldiv_lnu"].overwrite = []
pm.DB["ldiv_lnu_ow"] = pm.PredicateMetadata( "ldiv_lnu_ow", tuple() )
pm.DB["ldiv_lnu_ow"].overwrite = [(1,0)]
pm.DB["ldiv_lti"] = pm.PredicateMetadata( "ldiv_lti", tuple() )
pm.DB["ldiv_lti"].overwrite = []
pm.DB["ldiv_lti_ow"] = pm.PredicateMetadata( "ldiv_lti_ow", tuple() )
pm.DB["ldiv_lti_ow"].overwrite = [(1,0)]
pm.DB["ldiv_ltn"] = pm.PredicateMetadata( "ldiv_ltn", tuple() )
pm.DB["ldiv_ltn"].overwrite = []
pm.DB["ldiv_ltn_ow"] = pm.PredicateMetadata( "ldiv_ltn_ow", tuple() )
pm.DB["ldiv_ltn_ow"].overwrite = [(1,0)]
pm.DB["ldiv_ltu"] = pm.PredicateMetadata( "ldiv_ltu", tuple() )
pm.DB["ldiv_ltu"].overwrite = []
pm.DB["ldiv_ltu_ow"] = pm.PredicateMetadata( "ldiv_ltu_ow", tuple() )
pm.DB["ldiv_ltu_ow"].overwrite = [(1,0)]

pm.DB["ldiv_uni"] = pm.PredicateMetadata( "ldiv_uni", tuple() )
pm.DB["ldiv_uni"].overwrite = []
pm.DB["ldiv_uni_ow"] = pm.PredicateMetadata( "ldiv_uni_ow", tuple() )
pm.DB["ldiv_uni_ow"].overwrite = [(1,0)]
pm.DB["ldiv_unn"] = pm.PredicateMetadata( "ldiv_unn", tuple() )
pm.DB["ldiv_unn"].overwrite = []
pm.DB["ldiv_unn_ow"] = pm.PredicateMetadata( "ldiv_unn_ow", tuple() )
pm.DB["ldiv_unn_ow"].overwrite = [(1,0)]
pm.DB["ldiv_unu"] = pm.PredicateMetadata( "ldiv_unu", tuple() )
pm.DB["ldiv_unu"].overwrite = []
pm.DB["ldiv_unu_ow"] = pm.PredicateMetadata( "ldiv_unu_ow", tuple() )
pm.DB["ldiv_unu_ow"].overwrite = [(1,0)]
pm.DB["ldiv_uti"] = pm.PredicateMetadata( "ldiv_uti", tuple() )
pm.DB["ldiv_uti"].overwrite = []
pm.DB["ldiv_uti_ow"] = pm.PredicateMetadata( "ldiv_uti_ow", tuple() )
pm.DB["ldiv_uti_ow"].overwrite = [(1,0)]
pm.DB["ldiv_utn"] = pm.PredicateMetadata( "ldiv_utn", tuple() )
pm.DB["ldiv_utn"].overwrite = []
pm.DB["ldiv_utn_ow"] = pm.PredicateMetadata( "ldiv_utn_ow", tuple() )
pm.DB["ldiv_utn_ow"].overwrite = [(1,0)]
pm.DB["ldiv_utu"] = pm.PredicateMetadata( "ldiv_utu", tuple() )
pm.DB["ldiv_utu"].overwrite = []
pm.DB["ldiv_utu_ow"] = pm.PredicateMetadata( "ldiv_utu_ow", tuple() )
pm.DB["ldiv_utu_ow"].overwrite = [(1,0)]

pm.DB["rdiv_lni"] = pm.PredicateMetadata( "rdiv_lni", tuple() )
pm.DB["rdiv_lni"].overwrite = []
pm.DB["rdiv_lni_ow"] = pm.PredicateMetadata( "rdiv_lni_ow", tuple() )
pm.DB["rdiv_lni_ow"].overwrite = [(1,0)]
pm.DB["rdiv_lnn"] = pm.PredicateMetadata( "rdiv_lnn", tuple() )
pm.DB["rdiv_lnn"].overwrite = []
pm.DB["rdiv_lnn_ow"] = pm.PredicateMetadata( "rdiv_lnn_ow", tuple() )
pm.DB["rdiv_lnn_ow"].overwrite = [(1,0)]
pm.DB["rdiv_lnu"] = pm.PredicateMetadata( "rdiv_lnu", tuple() )
pm.DB["rdiv_lnu"].overwrite = []
pm.DB["rdiv_lnu_ow"] = pm.PredicateMetadata( "rdiv_lnu_ow", tuple() )
pm.DB["rdiv_lnu_ow"].overwrite = [(1,0)]
pm.DB["rdiv_lti"] = pm.PredicateMetadata( "rdiv_lti", tuple() )
pm.DB["rdiv_lti"].overwrite = []
pm.DB["rdiv_lti_ow"] = pm.PredicateMetadata( "rdiv_lti_ow", tuple() )
pm.DB["rdiv_lti_ow"].overwrite = [(1,0)]
pm.DB["rdiv_ltn"] = pm.PredicateMetadata( "rdiv_ltn", tuple() )
pm.DB["rdiv_ltn"].overwrite = []
pm.DB["rdiv_ltn_ow"] = pm.PredicateMetadata( "rdiv_ltn_ow", tuple() )
pm.DB["rdiv_ltn_ow"].overwrite = [(1,0)]
pm.DB["rdiv_ltu"] = pm.PredicateMetadata( "rdiv_ltu", tuple() )
pm.DB["rdiv_ltu"].overwrite = []
pm.DB["rdiv_ltu_ow"] = pm.PredicateMetadata( "rdiv_ltu_ow", tuple() )
pm.DB["rdiv_ltu_ow"].overwrite = [(1,0)]

pm.DB["rdiv_uni"] = pm.PredicateMetadata( "rdiv_uni", tuple() )
pm.DB["rdiv_uni"].overwrite = []
pm.DB["rdiv_uni_ow"] = pm.PredicateMetadata( "rdiv_uni_ow", tuple() )
pm.DB["rdiv_uni_ow"].overwrite = [(1,0)]
pm.DB["rdiv_unn"] = pm.PredicateMetadata( "rdiv_unn", tuple() )
pm.DB["rdiv_unn"].overwrite = []
pm.DB["rdiv_unn_ow"] = pm.PredicateMetadata( "rdiv_unn_ow", tuple() )
pm.DB["rdiv_unn_ow"].overwrite = [(1,0)]
pm.DB["rdiv_unu"] = pm.PredicateMetadata( "rdiv_unu", tuple() )
pm.DB["rdiv_unu"].overwrite = []
pm.DB["rdiv_unu_ow"] = pm.PredicateMetadata( "rdiv_unu_ow", tuple() )
pm.DB["rdiv_unu_ow"].overwrite = [(1,0)]
pm.DB["rdiv_uti"] = pm.PredicateMetadata( "rdiv_uti", tuple() )
pm.DB["rdiv_uti"].overwrite = []
pm.DB["rdiv_uti_ow"] = pm.PredicateMetadata( "rdiv_uti_ow", tuple() )
pm.DB["rdiv_uti_ow"].overwrite = [(1,0)]
pm.DB["rdiv_utn"] = pm.PredicateMetadata( "rdiv_utn", tuple() )
pm.DB["rdiv_utn"].overwrite = []
pm.DB["rdiv_utn_ow"] = pm.PredicateMetadata( "rdiv_utn_ow", tuple() )
pm.DB["rdiv_utn_ow"].overwrite = [(1,0)]
pm.DB["rdiv_utu"] = pm.PredicateMetadata( "rdiv_utu", tuple() )
pm.DB["rdiv_utu"].overwrite = []
pm.DB["rdiv_utu_ow"] = pm.PredicateMetadata( "rdiv_utu_ow", tuple() )
pm.DB["rdiv_utu_ow"].overwrite = [(1,0)]

A = PatternDot("A")
B = PatternDot("B")
X = PatternDot("X")

trsm2lgen_rules = [
    # X = i(t(A)) B -> ldiv_lni
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isLowerTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_lni", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_lni_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isLowerTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_lni_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_lnu
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isLowerTriangular() and A.isUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_lnu", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_lnu_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isLowerTriangular() and A.isUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_lnu_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_lnn
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_lnn", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Minus([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Minus([ Predicate("ldiv_lnn", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_lnn_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_lnn_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Minus([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Minus([ Predicate("ldiv_lnn_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_lti
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isLowerTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_lti", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_lti_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isLowerTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_lti_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_ltu
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isLowerTriangular() and A.isUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_ltu", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_ltu_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isLowerTriangular() and A.isUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_ltu_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_ltn
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_ltn", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_ltn_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_ltn_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),

    # X = i(t(A)) B -> ldiv_uni
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isUpperTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_uni", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_uni_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isUpperTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_uni_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_unu
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isUpperTriangular() and A.isUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_unu", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_unu_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isUpperTriangular() and A.isUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_unu_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_unn
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isUpperTriangular() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_unn", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_unn_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Inverse([ A ]), B ]) ]),
            Constraint("A.isUpperTriangular() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_unn_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_uti
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isUpperTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_uti", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_uti_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isUpperTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_uti_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_utu
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isUpperTriangular() and A.isUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_utu", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_utu_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isUpperTriangular() and A.isUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_utu_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_utn
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isUpperTriangular() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_utn", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> ldiv_utn_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ Transpose([ Inverse([ A ]) ]), B ]) ]),
            Constraint("A.isUpperTriangular() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("ldiv_utn_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),

    # X = i(t(A)) B -> rdiv_lni
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isLowerTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_lni", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_lni_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isLowerTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_lni_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_lnu
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isLowerTriangular() and A.isUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_lnu", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_lnu_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isLowerTriangular() and A.isUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_lnu_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_lnn
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_lnn", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_lnn_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_lnn_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_lti
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isLowerTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_lti", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_lti_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isLowerTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_lti_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_ltu
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isLowerTriangular() and A.isUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_ltu", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_ltu_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isLowerTriangular() and A.isUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_ltu_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_ltn
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_ltn", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_ltn_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isLowerTriangular() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_ltn_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),

    # X = i(t(A)) B -> rdiv_uni
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isUpperTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_uni", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_uni_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isUpperTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_uni_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_unu
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isUpperTriangular() and A.isUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_unu", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_unu_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isUpperTriangular() and A.isUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_unu_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_unn
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isUpperTriangular() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_unn", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_unn_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Inverse([ A ]) ]) ]),
            Constraint("A.isUpperTriangular() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_unn_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_uti
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isUpperTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_uti", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_uti_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isUpperTriangular() and A.isImplicitUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_uti_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_utu
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isUpperTriangular() and A.isUnitDiagonal() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_utu", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_utu_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isUpperTriangular() and A.isUnitDiagonal() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_utu_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_utn
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isUpperTriangular() and X.st_info[1].name == X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_utn", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
    # X = i(t(A)) B -> rdiv_utn_ow
    RewriteRule(
        (
            Equal([ NList([ X ]), Times([ B, Transpose([ Inverse([ A ]) ]) ]) ]),
            Constraint("A.isUpperTriangular() and X.st_info[1].name != X.name")
        ),
        Replacement(
            lambda d:
                Equal([ NList([ d["X"] ]), Predicate("rdiv_utn_ow", [d["A"], d["B"]], 
                          [d["A"].get_size(), d["B"]. get_size()]) ])
        )
    ),
]
