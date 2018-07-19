from typing import Set
from typing import Dict
from typing import List
from typing import Tuple
import os
import random
import time
import sys


# FUNCTIONS
def get_raw_xs() -> List[Tuple[int, str]]:
    OUTPUT_PATH: str = os.path.join(RES_PATH, "OUTPUT")
    SOL_PATH: str = os.path.join(OUTPUT_PATH, "ris.sol")
    with open(SOL_PATH, 'r') as sol:
        xs: List[Tuple[int, str]] = []
        for line in sol:
            if line.startswith("x"):
                parts: List[str] = line.strip().split()
                node = int(parts[0][1:])
                val = parts[1]
                if val != '0':
                    xs.append((node, val))
    return xs


def clean_xs(xs: List[Tuple[int, str]]) -> List[Tuple[int, float]]:
    clean_xs: List[Tuple[int, float]] = []
    for t in xs:
        node: int = t[0]
        val_str = t[1]
        if 'e' not in val_str:
            val: float = float(val_str)
        elif 'e' in val_str:
            parts: List[str] = val_str.split('e-')
            base: float = float(parts[0])
            exp: int = int(parts[1])
            div: int = 10 ** exp
            val: float = base / div
        clean_xs.append((node, val))
    #print(clean_xs)
    return clean_xs


def loadparams() -> Dict[str, str]:
    with open(PARAMS_PATH, 'r') as f:
        params: Dict[str, str] = dict()
        for line in f:
            if '=' in line:
                parts: List[str] = line.strip().split("=")
                params[parts[0]] = parts[1]
    return params


def assertWeights(k: int, weights_sum: float) -> None:
    #print("sum of weights: ", weights_sum)
    #print("k: ", k)
    if abs(k - weights_sum) > 1:
        raise Exception("error in weights sum! diff is ", abs(k - weights_sum))


def selectSeeds(weights: List[float], k: int, nodes: List[int]) -> Set[int]:
    weights_sum: float = sum(weights)
    assertWeights(k, weights_sum)
    seeds: Set[int] = set()
    while len(seeds) < k:
        seeds.add(nodes[select_node(weights, weights_sum)])
    return sorted(seeds)


def select_node(weights: List[float], weights_sum: float) -> int:
    num: float = random.uniform(0, weights_sum)
    for i, w in enumerate(weights):
        num -= w
        if (num <= 0):
            return i
    raise Exception("no node selected")




def save_seeds(seeds: List[int]) -> None:
    with open(PARAMS_PATH, 'r') as f:
        lines: List[str] = f.readlines()
        new_lines: List[str] = []
        for line in lines:
            if line.startswith("seeds"):
                parts: list[str] = line.split("=")
                line = parts[0] + "=" + str(seeds)[1:-1]
                print("changes seeds line to: ", line)
            new_lines.append(line)

    with open(PARAMS_PATH, 'w') as f:
        for line in new_lines:
            f.write(line)
    print("Finished writing to ", PARAMS_PATH)


# MAIN
if len(sys.argv) != 2:
    print("Required exactly one additional argument. Recieved: ", len(sys.argv) - 1)
    exit(-1)
RES_PATH: str = sys.argv[1]
PARAMS_PATH: str = os.path.join(RES_PATH, "IM", "params.txt")

start_time = time.time()
try:
    params: Dict[str, str] = loadparams()
except:
    print("Error loading params. Resources path: ", RES_PATH)
    exit(-1)
xs: List[Tuple[int, float]] = clean_xs(get_raw_xs())
nodes: List[int] = [t[0] for t in xs]
weights: List[float] = [t[1] for t in xs]
seeds: List[int] = selectSeeds(weights, int(params["k"]), nodes)
save_seeds(seeds)
print(str(seeds)[1:-1])
print("--- %s seconds ---" % (time.time() - start_time))
