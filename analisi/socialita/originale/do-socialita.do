keep eta etami reg regmf amici amici2 vicini relam temlib pgrvo pcult volon atgra biblio13

keep if regmf == 030

gen etami = .

replace etami = 004 if eta >= 11 & eta <= 13
replace etami = 005 if eta >= 14 & eta <= 15
replace etami = 006 if eta >= 16 & eta <= 17
replace etami = 007 if eta >= 18 & eta <= 19
fre etami

gen adolescente = 0
replace adolescente = 1 if etami == 005 | etami == 006 | etami == 007
keep if adolescente == 1

fre amici amici2 vicini relam temlib pgrvo pcult volon atgra biblio1

///2013
keep if regmf == 030

gen adolescente = 0
replace adolescente = 1 if etami == 005 | etami == 006
fre adolescente
keep if adolescente == 1

keep etami regmf amici amici2 vicini relam temlib pgrvo pcult volon atgra adolescente anno

fre amici amici2 vicini relam temlib pgrvo pcult volon atgr adolescente