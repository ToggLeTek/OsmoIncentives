import json
import urllib.request
import datetime
from typing import Any, Callable
import Params

def load_json_(url : str) -> Any:
    return json.loads(urllib.request.urlopen(urllib.request.Request(url)).read().decode('utf-8'))


def cached_call(cache : dict[str, Any], key : str, f : Callable[[],Any]):
    r = cache.get(key)
    if r == None:
        r = f()
        cache[key] = r
    return r


query_cache : dict[str, Any] = {}
def load_json(url : str) -> Any:
    r = query_cache.get(url)
    while r == None:
        try:
            print("loading url: ", url)
            r = load_json_(url)
            query_cache[url] = r
        except:
            print("retrying: ", url)
            pass
    return r



def parse_percent(s : str) -> float:
    return float(s[:-1])/100

def parse_start_time(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s[:19],"%Y-%m-%dT%H:%M:%S")

def days_from_now(n : int) -> datetime.datetime:
    return datetime.datetime.now() + datetime.timedelta(days=7)

def write_csv(name : str, lines : list[str]) -> None:
    with open(name, "w+") as f:
        f.write("\n".join(lines))

def read_csv(name : str) -> list[list[str]]:
    with open(name, "r") as f:
        return [x.strip().split(",") for x in f.readlines()]

def categorize(l : list[str]) -> str:
    (base, asset) = based(l)
    if base == "OSMO":
        if asset in Params.Stables:
            return "OSMO_STABLE"
        if asset in Params.Majors:
            return "OSMO_MAJOR"
        else:
            return "OSMO_MINOR"
    elif base in Params.Stables:
        if asset in Params.Majors:
            return "MAJOR_STABLE"
        if asset in Params.Stables:
            return "STABLESWAP"
    return "OTHERS"



def based(l : list[str]) -> tuple[str, str]:
    a = l[0]
    b = l[1]
    if a == "OSMO":
        return ("OSMO",b)
    elif b == "OSMO":
        return ("OSMO",a)
    elif a == "USDC":
        return ("USDC",b)
    elif b == "USDC":
        return ("USDC",a)
    elif a == "DAI":
        return ("DAI",b)
    elif b == "DAI":
        return ("DAI",a)
    elif a == "EEUR":
        return ("EEUR", b)
    elif b == "EEUR":
        return ("EEUR", a)
    elif a == "ATOM":
        return ("ATOM",b)
    elif b == "ATOM":
        return ("ATOM",a)
    print("assets not based? : ", l)
    return ("","")
