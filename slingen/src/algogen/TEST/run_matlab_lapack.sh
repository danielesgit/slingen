#!/usr/bin/env bash

./Cl1ck --matlab --opt DB_Ops/Factorizations/chol_l.ck || exit
./Cl1ck --matlab --opt DB_Ops/Inverse/tril_inv.ck || exit
./Cl1ck --matlab --opt DB_Ops/ControlTheory/sylv_lup.ck DB_Ops/ControlTheory/lyap_l.ck || exit
