from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data
from io import StringIO

import streamlit as st
import pandas as pd
import requests 
import datetime

from spatial import gazetteer
from spatial import haversine

PROD_TTL = 3600 #1 hour
TESTING_TTL = 1
CACHE_TTL = TESTING_TTL 

RADIUS = 20 #RADIUS*2 by RADIUS*2 square before sphere projection curvature
AIRNOW_DATA_ENDPOINT = "https://www.airnowapi.org/aq/data/"


def get_times(delta=1):
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%dT%H")
    shifted_time = current_time - datetime.timedelta(hours=1)
    shifted_time_str = shifted_time.strftime("%Y-%m-%dT%H")
    return current_time_str, shifted_time_str

class AirnowConnection(ExperimentalBaseConnection[requests.session]):

    def _connect(self, **kwargs) -> requests.session: 
        self.airnow_key = self._secrets["airnow_key"]
        self.session = requests.session()
        return self.session
    
    def cursor(self):
        return self.session

    def query(self, query: str, ttl: int = CACHE_TTL, **kwargs):

        if not gazetteer.validate_zip(query):
            return None

        @st.cache_data
        def get_zip_dict():
            return gazetteer.get_zip_dict()

        zip_dict = get_zip_dict()
        if query not in zip_dict:
            return None
            
        #TODO: denotebookify this, break out this use case, and add more of the other data products
        #@st.cache_data(ttl=ttl)
        def _query(query: str, **kwargs) -> pd.DataFrame:

            coords = zip_dict[query]
            time_date_offset, time_date = get_times()
            bounding_box = haversine.bounding_box(coords[0], coords[1], RADIUS)
            params = {
                "startDate": time_date,
                "endDate": time_date_offset,
                "parameters": "OZONE,PM25,PM10",
                "BBOX": bounding_box, 
                "dataType": "B",
                "format": "text/csv",
                "verbose": 1,
                "monitorType": 0,
                "includerawconcentrations": 0,
                "API_KEY": self.airnow_key
            }

            rs = self.session
            response = rs.get(AIRNOW_DATA_ENDPOINT, params=params)

            if response.status_code != 200:
                return None
            
            df = pd.read_csv(StringIO(response.text),
                            names = ["Latitude","Longitude","Time",
                                    "Type","Concentration","Unit",
                                    "AQI","Danger","Site Name",
                                    "drop1","drop2","drop3"]
                            ).drop(["drop1","drop2","drop3"],axis=1)

            if len(df.index) == 0: #no stations within 20mi
                return df 

            danger_conv = {
                "-999":"",
                "1":"",
                "2":"[!]",
                "3":"[!!]",
                "4":"[!!!]",
                "5":"[!!!]",
                "6":"[!!!]"
            }

            df["Concentration/Unit"] = df["Concentration"].astype(str) + " "\
                  + df["Unit"] + " " + df["Danger"].apply(lambda x:str(danger_conv[str(x)]))
     
            pivoted_df = df.pivot_table(index=["Site Name","Latitude","Longitude",], 
                        columns=["Type"], 
                        values=["Concentration/Unit"], 
                        aggfunc="first"
                        ).fillna("-").reset_index()
            
            pivoted_df[["Station Angle", "Station Distance"]] = pivoted_df.apply(
                lambda x:haversine.haversine(coords[0],coords[1],x["Latitude"][0],x["Longitude"][0]),
                axis=1).tolist()
            
            pivoted_df["Station Direction"] = pivoted_df["Station Angle"].apply(haversine.degrees_to_direction)

            #removed as temp fix for rural zips with incomplete data
            # pivoted_df = pivoted_df[pd.MultiIndex.from_tuples([
            #             ("Site Name",               ""),
            #             ("Latitude",                ""),
            #             ("Longitude",               ""),
            #             ("Concentration/Unit", "PM2.5"),
            #             ("Concentration/Unit",  "PM10"),
            #             ("Concentration/Unit", "OZONE"),
            #             ("Station Distance",        ""),
            #             ("Station Direction",       ""),
            #             ])]
            
            
            pivoted_df.sort_values(by="Station Distance").head(60)

            return pivoted_df
        
        return _query(query, **kwargs)

