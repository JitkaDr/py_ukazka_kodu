import pandas as pd
import os
from datetime import datetime
import math
import logging


def get_logger(level="INFO", log_to_file=True):
    log = logging.getLogger()
    log.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # log to console
    log_console = logging.StreamHandler()
    log_console.setFormatter(formatter)
    log.addHandler(log_console)

    # log to file
    if log_to_file:
        now = datetime.now()
        now_str = now.strftime("%Y_%m_%d_%H%M%S")

        logs_folder = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_folder): os.makedirs(logs_folder)
        log_file = logging.FileHandler(os.path.join(logs_folder, f"log_{now_str}.log"), "w")
        log_file.setFormatter(formatter)
        log.addHandler(log_file)

    return log


log = get_logger()

# naimportovat excel soubor
current = os.getcwd()
file = os.path.join(current, "data", "Bank clients.xlsx")
df_clients = pd.read_excel(file, sheet_name='clients')
df_debtors = pd.read_excel(file, sheet_name='debtor_list')
df_rates = pd.read_excel(file, sheet_name='interest_rates')
log.info("data nactena")

# zmena datovych typu v df
df_clients["id"] = df_clients["id"].astype("str")
df_debtors["rodne_cislo"] = df_debtors["rodne_cislo"].astype(str) 

# zjisteni pohlavi dle RC
def zjisti_pohlavi(rc:str) -> str:

    rozhodne_cislo = int(rc[2])
    if rozhodne_cislo > 1:
        return "Female"
    else:
        return "Male"


df_clients["gender"] = df_clients.apply(lambda row: zjisti_pohlavi(row["id"]), axis=1)
log.info("zjisteno pohlavi klientu")

# zjisteni data narozeni dle RC
def zjisti_vek_klienta(rc:str) -> str:
    
    # zmen na prislusny mesic, pokud je to zena
    zacatek_mesice = int(rc[2])
    if zacatek_mesice >= 5:
        zacatek_mesice -= 5

    datum_narozeni = rc[4:6] + "." + str(zacatek_mesice) + rc[3] + "." + "19" + rc[:2]
    datum_nar_obj = datetime.strptime(datum_narozeni, "%d.%m.%Y")
    now = datetime.now()
    vek_ve_dnech = (now - datum_nar_obj).days
    vek_v_rocich = vek_ve_dnech/365.25
    vek_v_rocich = math.floor(vek_v_rocich)

    return vek_v_rocich
    

df_clients["client_age"] = df_clients.apply(lambda row: zjisti_vek_klienta(row ["id"]), axis=1)
log.info("zjisten vek klientu")

# odstran klienty dle veku
df_male_clients = df_clients.loc[(df_clients["client_age"] >= 20) & (df_clients["client_age"] <= 50) & (df_clients["gender"] == "Male")]
df_female_clients = df_clients.loc[(df_clients["client_age"] >= 20) & (df_clients["client_age"] <= 55) & (df_clients["gender"] == "Female")]
df_clients = df_male_clients.append(df_female_clients)

# odstran dluzniky
df_client_debtors =  pd.merge(df_clients, df_debtors, left_on='id', right_on='rodne_cislo', how='inner')

def zjisti_prilisnou_vysi_dluhu(prijem:int, dluh:int) -> bool:
    if prijem*12 < dluh:
        return True
    else:
        return False


df_client_debtors["dluzi_prilis"] = df_client_debtors.apply(lambda row: zjisti_prilisnou_vysi_dluhu(row ["month_salary"], row["nesplacena_jistina"]), axis=1)
df_client_debtors = df_client_debtors.loc[(df_client_debtors["dluzi_prilis"] == True)]
df_clients = df_clients.loc[~df_clients["id"].isin(df_client_debtors["id"])]

del df_debtors
del df_client_debtors
log.info("zjisteni klienti, kteri dosahnou na hypoteku")

# dalsi krok - zjisteni urokove sazby
def zjisti_urokovou_sazbu(pohlavi, vek, zeme_puvodu):
   
    df_gender_rate = df_rates.loc[df_rates["gender"] == pohlavi]

    for milnik in df_gender_rate["min_age"]:
        if vek >= milnik:
            stavajici_milnik = milnik
        else:
            break

    df_gender_rate = df_gender_rate.loc[df_gender_rate["min_age"] == stavajici_milnik]

    urokova_sazba = df_gender_rate.iloc[0]["interest_rate"]
    if zeme_puvodu != "Czech Republic":
        urokova_sazba = urokova_sazba + 0.2
    return urokova_sazba


df_clients["interest_rate"] = df_clients.apply(lambda row: zjisti_urokovou_sazbu(row["gender"], row["client_age"], row["country"]), axis=1)
log.info("zjistena urokova sazba klientu")

# zjisteni maximalni vyse hypoteky
df_clients["maximalni_hypoteka"] = df_clients["month_salary"]*108
log.info("pridani info o maximalni vysi hypoteky")

# uprava df na pozadovane sloupce + jejich nazvu
df_clients = df_clients[["name", "surname", "phone", "email", "interest_rate", "maximalni_hypoteka"]]
df_clients = df_clients.rename(columns={"name":"jmeno", "surname":"prijmeni", "phone":"telefon", "interest_rate":"urokova_sazba", "maximalni_hypoteka":"max_vyse_hypoteky"})

# nahradit NaN hodnoty
df_clients['telefon'] = df_clients['telefon'].fillna("pouze email")
file = os.path.join(current, "data", "clients_mortgage_offers.xlsx")
df_clients.to_excel(file, sheet_name="client_data", index=False)
log.info("soubor uspesne vyexportovan")
log.info("skript byl uspesny")

