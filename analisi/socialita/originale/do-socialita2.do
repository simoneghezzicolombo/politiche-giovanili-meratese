append using socialita2014.dta
append using socialita2015.dta
append using socialita2016.dta
append using socialita2017.dta
append using socialita2018.dta
append using socialita2019.dta
append using socialita2020.dta
append using socialita2021.dta
append using socialita2022.dta


destring amici, replace ignore("")
drop if missing(amici)

destring amici2, replace ignore("")
drop if missing(amici2)

destring volon, replace ignore("")
drop if missing(volon)

destring atgra, replace ignore("")
drop if missing(atgra)

destring relam, replace ignore("")
drop if missing(relam)

// Step 1: Tabulate the distribution of amici by year and save frequencies
preserve
gen total = 1 
// Create a variable to count all observations
collapse (count) total, by(anno amici) 
// Count observations for each year and amici category

// Step 2: Calculate total observations per year
egen year_total = total(anno), by(anno)

// Step 3: Calculate percentages for each amici category within each year
gen pct_amici = 100 * total / year_total

drop total
reshape wide pct_amici, i(anno) j(amici)
twoway (line pct_amici1 anno, sort lcolor(blue)) ///
       (line pct_amici2 anno, sort lcolor(red)) ///
       (line pct_amici3 anno, sort lcolor(green)) ///
       (line pct_amici4 anno, sort lcolor(orange)) ///
       (line pct_amici5 anno, sort lcolor(purple)) ///
       (line pct_amici6 anno, sort lcolor(brown)) ///
       (line pct_amici7 anno, sort lcolor(black)), ///
    legend(label(1 "Tutti i giorni") label(2 "Più di una volta a settimana") ///
           label(3 "Una volta alla settimana") label(4 "Qualche volta al mese") ///
           label(5 "Qualche volta durante l'anno") label(6 "Mai") ///
           label(7 "Non ho amici")) ///
    ytitle("Percentuale (%)") ///
    xtitle("Anno") ///
    title("Evoluzione della frequenza di incontro con gli amici")
restore


// Create a placeholder variable to count rows
preserve
gen count_amici = 1

// Aggregate the data to count the number of occurrences for each `anno` and `amici`
collapse (sum) count_amici, by(anno amici)
// Calculate the total number of observations for each year
bysort anno (amici): egen total_year = total(count_amici)

// Check the results
list anno amici count_amici total_year if anno == 2013
// Calculate the percentage for each amici category
gen pct_amici = 100 * count_amici / total_year

// Verify the percentages add up to 100 within each year
bysort anno (amici): egen sum_pct = total(pct_amici)
list anno sum_pct if _n == 1
// Reshape to wide format
drop count_amici
reshape wide pct_amici, i(anno) j(amici)
twoway (line pct_amici1 anno, sort lcolor(blue)) ///
       (line pct_amici2 anno, sort lcolor(red)) ///
       (line pct_amici3 anno, sort lcolor(green)) ///
       (line pct_amici4 anno, sort lcolor(orange)) ///
       (line pct_amici5 anno, sort lcolor(purple)) ///
       (line pct_amici6 anno, sort lcolor(brown)) ///
       (line pct_amici7 anno, sort lcolor(black)), ///
    legend(label(1 "Tutti i giorni") label(2 "Più di una volta a settimana") ///
           label(3 "Una volta alla settimana") label(4 "Qualche volta al mese") ///
           label(5 "Qualche volta durante l'anno") label(6 "Mai") ///
           label(7 "Non ho amici")) ///
    ytitle("Percentuale (%)") ///
    xtitle("Anno") ///
    title("Evoluzione della frequenza di incontro con gli amici (Ponderata)")
list anno pct_amici1 pct_amici2 pct_amici3 pct_amici4 pct_amici5 pct_amici6 pct_amici7
restore

preserve
// Step 1: Create a placeholder variable to count rows
gen count_amici2 = 1

// Step 2: Collapse to count observations for each anno and amici2 category
collapse (sum) count_amici2, by(anno amici2)

// Step 3: Calculate total observations for each year
bysort anno: egen total_year = total(count_amici2)

// Step 4: Calculate percentages for each amici2 category
gen pct_amici2 = 100 * count_amici2 / total_year

drop count_amici2
// Step 5: Reshape to wide format
reshape wide pct_amici2, i(anno) j(amici2)
twoway (line pct_amici21 anno, sort lcolor(red)) ///
       (line pct_amici22 anno, sort lcolor(blue)) ///
       (line pct_amici23 anno, sort lcolor(green)), ///
    legend(label(1 "No") label(2 "Sì") label(3 "Non so")) ///
    ytitle("Percentuale (%)") ///
    xtitle("Anno") ///
    title("Evoluzione della variabile AMICI2 (Ponderata)") ///
    note("Fonte: Rielaborazione su Stata di analisi Istat 'INDAGINE: Multiscopo sulle famiglie: aspetti della vita quotidiana' (2013-2022)")
restore


// Generate a new variable and initialize it to 0
gen new_var = 0

// Assign value 1 if either condition is met
replace new_var = 1 if volon == 4 | atgra == 6

tab new_var

preserve
// Step 1: Create a placeholder variable to count rows
gen count = 1

// Step 2: Collapse to count observations for new_var by year
collapse (sum) count_new_var = new_var count, by(anno)

// Step 3: Calculate the percentage of new_var = 1 for each year
gen pct_new_var = 100 * count_new_var / count
twoway (line pct_new_var anno, sort lcolor(blue) lwidth(medium)), ///
    ytitle("Percentuale (%)") ///
    xtitle("Anno") ///
    title("Evoluzione: Giovani che hanno svolto attività gratuita") ///
    note("Fonte: Rielaborazione su Stata di analisi Istat 'INDAGINE: Multiscopo sulle famiglie: aspetti della vita quotidiana' (2013-2022)")
list anno count_new_var count pct_new_var
restore

preserve
// Step 1: Create a placeholder variable to count rows
gen count_relam = 1

// Step 2: Aggregate the data by year and relam category
collapse (sum) count_relam, by(anno relam)
// Calculate the total number of observations for each year
bysort anno (relam): egen total_year = total(count_relam)

// Verify the results
list anno relam count_relam total_year if anno == 2013
// Calculate the percentage for each relam category
gen pct_relam = 100 * count_relam / total_year
// Sort data by year
sort anno

// Smooth percentages for each relam category (moving average with window 3 years)
gen pct_relam_smooth = pct_relam
tsset anno relam
capture drop pct_relam_smooth
tssmooth ma pct_relam_smooth = pct_relam, window(1 1 1)
// Reshape to wide format for plotting
drop count_relam pct_relam
reshape wide pct_relam_smooth, i(anno) j(relam)
twoway (line pct_relam_smooth1 anno, sort lcolor(blue)) ///
       (line pct_relam_smooth2 anno, sort lcolor(red)) ///
       (line pct_relam_smooth3 anno, sort lcolor(green)) ///
       (line pct_relam_smooth4 anno, sort lcolor(orange)), ///
    legend(label(1 "Molto") label(2 "Abbastanza") ///
           label(3 "Poco") label(4 "Per niente")) ///
    ytitle("Percentuale (%)") ///
    xtitle("Anno") ///
    title("Evoluzione della soddisfazione delle relazioni con amici (Ponderata e Smussata)") ///
    note("Fonte: Rielaborazione su Stata di analisi Istat 'INDAGINE: Multiscopo sulle famiglie: aspetti della vita quotidiana' (2013-2022)")
list anno pct_relam_smooth1 pct_relam_smooth2 pct_relam_smooth3 pct_relam_smooth4, clean
restore


preserve
// Filter for "Molto soddisfatto" (relam == 1)
gen is_molto = (relam == 1)

// Aggregate the count of "Molto soddisfatto" by year
collapse (sum) count_molto = is_molto (count) total_year = relam, by(anno)
// Calculate the percentage for "Molto soddisfatto"
gen pct_molto = 100 * count_molto / total_year
// Set the time variable
tsset anno

// Apply moving average smoothing
tssmooth ma pct_molto_smooth = pct_molto, window(3 1 1)
twoway (line pct_molto_smooth anno, sort lcolor(blue)), ///
    ytitle("Percentuale (%)") ///
    xtitle("Anno") ///
    title("Evoluzione della soddisfazione (Molto soddisfatto, ponderata e smussata)") ///
    note("Fonte: Rielaborazione su Stata di analisi Istat 'INDAGINE: Multiscopo sulle famiglie: aspetti della vita quotidiana' (2013-2022)")
list anno pct_molto pct_molto_smooth, clean
restore
