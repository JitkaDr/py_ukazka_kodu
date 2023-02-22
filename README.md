# Python - ukazka kodu

## Výstup: 
vyexportovat excel, který bude mít formát jako sheet 'Example table' v souboru Bank clients.xlsx

## Zadání: 
úrokovou sazbu zjisti podle tabulky interest_rates
max_výše hypotéky je 9x roční příjem 
pokud člověk není z České republiky, automaticky přičti k jeho úrokové sazbě 0,2%
hypotéku nemůžeme dát člověku, který je v našem registru dlužníků (debtor list) a dluží více než svůj roční příjem
hypotéku nemůžeme poskytnout lidem mladším 20 let, mužům starším 50 let a ženám starším 55 let

## Technické parametry:
script bude načítat excel s názvem Bank clients.xlsx z podsložky data
exportovat pak bude do stejné složky excel s názvem clients_mortgage_offers.xlsx
