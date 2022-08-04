from util import *
import Params
import parseDenom
import parseStaking
from typing import Any, Callable

INTERBLOC = "https://api.osmosis.interbloc.org/osmosis"
IMPERATOR = "https://api-osmosis.imperator.co/"
CURVE = "https://stats.curve.fi/raw-stats/apys.json"
ASSETLIST = "https://raw.githubusercontent.com/ToggLeTek/assetlists/main/osmosis-1/osmosis-frontier.assetlist.json"
MINTSCAN = "https://dashboard-mintscan.s3.ap-northeast-2.amazonaws.com/chains/apr.json"
GECKO_OSMO = "https://api.coingecko.com/api/v3/simple/price?ids=osmosis&vs_currencies=usd"


def load_pool(pid: int):
    return load_json(INTERBLOC+"/gamm/v1beta1/pools/"+str(pid))


def load_volume(pid: int):
    return load_json(IMPERATOR+"pools/v2/volume/"+str(pid)+"/chart")


def load_gauge_ids(pid: int) -> dict[str, int]:
    gs = load_json(INTERBLOC+"pool-incentives/v1beta1/gauge-ids/" +
                   str(pid))["gauge_ids_with_duration"]
    return {g["duration"]: int(g["gauge_id"]) for g in gs}


def load_distr_info():
    return load_json(INTERBLOC+"pool-incentives/v1beta1/distr_info")["distr_info"]


def load_denom_price():
    token_data = load_json(IMPERATOR+"tokens/v2/all")
    return {x["symbol"]: {"price": float(x["price"]), "denom": x["denom"]} for x in token_data}


def coin_gecko_price():
    gecko_data = load_json(GECKO_OSMO)['usd']
    return gecko_data

def load_total_lp_spend() -> float:
    daily_osmo_issuance = float(load_json(
        INTERBLOC+"mint/v1beta1/epoch_provisions")["epoch_provisions"])/1000000
    lp_mint_proportion = float(load_json(INTERBLOC+"mint/v1beta1/params")
                               ["params"]["distribution_proportions"]["pool_incentives"])
    return Params.total_incentive_share * daily_osmo_issuance * lp_mint_proportion * coin_gecko_price()


def staking_data():
    asset_data = load_json(MINTSCAN)['data']
    return {x["denom"]: x["stakingAPR"] for x in asset_data}

# osmo_stake_apr

# FIXME pagination limits on the gauges query, pagination limit kicked in and hid older gauges, should be fine to return to no pagination in September


def load_external_gauges(pid: int) -> dict[str, Any]:
    tokens = load_tokens()
    symbols = load_symbols()
    gauges_data = load_json(
        INTERBLOC+"incentives/v1beta1/gauges?pagination.limit=25000")["data"]

    is_external: Callable[[dict[str, Any]], bool] = lambda g: all([
        g["distribute_to"]["denom"] == "gamm/pool/" +
        str(pid),  # paid to this pool
        # not perpetual (so this math works)
        not g["is_perpetual"],
        int(g["num_epochs_paid_over"]) > int(
            g["filled_epochs"]) + 7,   # won't end in the next week
        parse_start_time(g["start_time"]) < days_from_now(
            7),  # started or starts in next week
        len(g["coins"]) == 1 and g["coins"][0]["denom"].startswith("ibc")
        # single asset + ibc assets only for simplicity of lookup (grouped for short circuit)
    ])

    external_gauges: dict[str, Any] = {}
    for g in gauges_data:
        if is_external(g):
            denom = g["coins"][0]["denom"]
            symbol = symbols.get(denom, None)
            if symbol == None:
                continue
            exponent = tokens[symbol]["exponent"]
            amount = int(g["coins"][0]["amount"])/pow(10, exponent)
            price = tokens[symbol]["price"]
            epochs = int(g["num_epochs_paid_over"])
            filled_epochs = int(g["filled_epochs"])

            external_gauges[g["id"]] = {
                "symbol": symbol,
                "amount": amount,
                "start_time": g["start_time"],
                "epochs": epochs,
                "filled_epochs": filled_epochs,
                "epochs_remaining": epochs - filled_epochs,
                "daily_value": amount * price / epochs
            }
    return external_gauges
