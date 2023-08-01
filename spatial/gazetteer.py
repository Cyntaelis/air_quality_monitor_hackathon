#ZCTA = zip code tabulation area
import pandas as pd

GAZETTEER_FILE = "./data/2022_Gaz_zcta_national.tsv"

def validate_zip(zip):
    return isinstance(zip, str) and zip.isnumeric() and len(zip)==5

def get_zip_dict():
    retval = {}
    zcta_df = pd.read_csv(GAZETTEER_FILE, sep="\t",dtype=str)
    #"INTPTLONG gets read with a trailing \n" 
    zcta_df.columns = zcta_df.columns.str.rstrip() 
    for zipcode in zcta_df[["GEOID","INTPTLAT","INTPTLONG"]].values.tolist():
        retval[str(zipcode[0])] = (zipcode[1],zipcode[2].rstrip())
    return retval

if __name__ == "__main__":
    zip = "10020"
    assert(validate_zip(zip))
    assert(get_zip_dict()[zip] == (40.759174,-73.980715))
    print("TEST PASS")