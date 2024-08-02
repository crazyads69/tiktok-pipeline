import pandas as pd
import datetime
import json


def read_traindata():
    df = pd.read_csv("traindata.csv")
    return df
