from datetime import datetime

import pandas as pd

# load all the data
from google_api import Api

data = pd.read_csv('bank_data/MCP_OPERATION_HISTORY_TEXT_20180914140551.txt', sep='\t', encoding="ISO-8859-2")


# clean data
data = data.rename(columns=lambda x: x.replace(' ', '_'))

data = data.drop(columns=['Data_waluty', 'Numer_referencyjny', 'Rachunek_odbiorcy/nadawcy'])

data = data[data.Typ_operacji != 'WYPŁATA KARTĽ']

data = data[~data.Tytułem.str.contains('Zasilenie rachunku', na=False)]
# data = data[~data.Tytułem.str.contains('Zasilenie rachunku') == True]

print(data)


def update_cells():
    api = Api()
    for index, transaction in data.iterrows():
        print(transaction)
        print(transaction['Waluta'])
        if transaction['Typ_operacji'] == 'ODSETKI OD DEPOZYTU':
            category = 'Odsetki'
            amount = transaction['Kwota_operacji']
            date = datetime.strptime(str(transaction['Data_księgowania']), '%Y%m%d')
            print((category, amount, date))
            api.update_expense_by_cat(category, amount, date)

    # api.update_expense_by_cat(category, amount, date)

update_cells()