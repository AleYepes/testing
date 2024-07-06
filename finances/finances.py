import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# pd.set_option('display.max_colwidth', None)

directory = r'/data/monthly_costs/'
columns = ['date', 'name', 'fin_date', 'value', 'account', 'nan', 'code']
dfs = []

for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath, sep='|', header=None, names=columns, encoding='latin1')
        dfs.append(df)
df = pd.concat(dfs)

df['date'] = pd.to_datetime(df['date'], dayfirst=True)
# df['consecutive'] = df['date'].dt.year + (df['date'].dt.month /12)
df = df.drop(['nan', 'fin_date', 'account'], axis=1)
df = df.drop_duplicates()


include = [
    "SUPER VINI",
    "ALCAMPO",
    "MARKET",
    "FRUTA",
    "mercadona",
    "carniceria",
    "veterinaria",
    "carref",
    "hiper",
    "papa jonhs",
    "polleria",
    "organic shop",
    "LIDL",
    "Simyo",
    "alejandro",
    "SANTIAGO",
    "Amon",
    "SEGUROS ADESLAS",
    "ELECTRICIDAD IBERDROLA",
    "AGUA CANAL",
    "LAS ROZAS",
    "ELECTRICIDAD FACTOR ENERGIA",
    "PESCADERIA",
    "dulce",
    "quesos",
    "paladar",
    "IBER LIMOSTAR"
    ]
include = [s.lower().strip() for s in include]

exclude = [
    "IKEA",
    "EL CORTE INGLES",
    "LEROY MERLIN",
    "AUTOESCUELA",
    "XE EUROPE",
    "Decorabano-Armilla",
    "Arciniega",
    "TRASPASO",
    "IBERIA",
    "COMISIONES",
    "INTERESES",
    "RECARGA",
    "IBERDROLA OTROS 2"
    ]
exclude = [s.lower().strip() for s in exclude]

def filter_rows(df):
    df_in  = df[df['name'].str.contains('|'.join(include), case=False, na=False)]
    df_in = df_in[~df_in['name'].str.contains('|'.join(exclude), case=False, na=False)]

    df_ex  = df[~df['name'].str.contains('|'.join(include), case=False, na=False)]
    df_ex = df_ex[df_ex['name'].str.contains('|'.join(exclude), case=False, na=False)]

    return df_in, df_ex

included_df, excluded_df = filter_rows(df)


month = 6
year = 2024
cash = 250 # 260 july
remainder = .16 

def filter_by_date(df, month, year):
    return df[(df['date'].dt.month == month) & (df['date'].dt.year == year)]

def calculate_share(df, month, year, cash, remainder):
    costs = filter_by_date(df, month, year)
    costs = costs[costs['value'] < 0]
    total_costs = costs.value.sum() - cash + remainder

    return total_costs/4
    
# My share
calculate_share(included_df, month, year, cash, remainder)