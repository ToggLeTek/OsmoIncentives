from logging import error
from util import *

# Variables
ASSETLIST = 'https://raw.githubusercontent.com/ToggLeTek/assetlists/main/osmosis-1/osmosis-frontier.assetlist.json'

# Load asset data and use it


def load_asset_data():
    token_data = load_json(ASSETLIST)['assets']
    token_dict = {x['symbol']: {'denom': x['base'], 'exponent': x['denom_units']
                                [-1]['exponent'], 'coingecko': ['coingecko_id']} for x in token_data}
    if token_dict is error:
        {x['symbol']: {'denom': x['base'], 'exponent': x['denom_units']
                       [-1]['exponent'], 'coingecko': ['null']} for x in token_data}
    return


ass = load_asset_data()
ass
