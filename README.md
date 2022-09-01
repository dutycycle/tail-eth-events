# tail-eth-events

## Overview

Small utility to tail events in the Ethereum log from the current block onward, in human readable(-ish) format. For example:

```
[Block 15454857] [Contract 0xDe07f45688cb6CfAaC398c1485860e186D55996D]  Transfer(indexed address sender=0x353d601aae0fc29908bb46a26cac562ad1a5bff2,indexed address receiver=0x0000000000000000000000000000000000000000,uint256 value=17268575233016576578)
[Block 15454857] [Contract 0x8eF11c51a666C53Aeeec504f120cd1435E451342]  Withdraw(indexed address owner=0x353d601aae0fc29908bb46a26cac562ad1a5bff2,uint256 shares=17268575233016576578,uint256 amount=18257840581989549385)
[Block 15454857] [Contract 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2]  Transfer(indexed address src=0x7685cd3ddd862b8745b1082a6acb19e14eaa74f3,indexed address dst=0xbeefbabeea323f07c59926295205d3b7a17e8638,uint256 wad=610600133740867388)
[Block 15454857] [Contract 0xba5BDe662c17e2aDFF1075610382B9B691296350, ProxiedTo 0x31acaaea0529894e7c3a5c70d3f9ee6d7804684f] Transfer(indexed address from=0xbeefbabeea323f07c59926295205d3b7a17e8638,indexed address to=0x7685cd3ddd862b8745b1082a6acb19e14eaa74f3,uint256 value=4724999999999999737856)
[Block 15454857] [Contract 0x7685cD3ddD862b8745B1082A6aCB19E14EAA74F3]  Anonymous/Unknown()
[Block 15454857] [Contract 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48]  Anonymous/Unknown()
```

It uses [web3.py](https://github.com/ethereum/web3.py) to get all log data in the current block. Then, for each log entry, it attempts to find the contract ABI, including for proxied contracts, using the [Etherscan API](https://etherscan.io/apis). If it can find the ABI it will decode the event arguments using the ABI.

Short polling is used to check when a new block is mined.

## Usage

Set the following environment variables:

```
ETH_NODE_WEBSOCKET= # wss url of your eth node provider
ETHERSCAN_API_KEY=
```

And run the script with:

```
python3 src/tail.py
```

Unit tests can we run with:

```
nosetest
```

## Future Work

* [topic0](https://github.com/wmitsuda/topic0) is a repository of event signatures, which could partially replace the current contract ABI lookup.
* Contract ABIs could/should be persisted in some long-term storage. A lightweight approach is to use [sqlitedict](https://github.com/RaRe-Technologies/sqlitedict)
* Similarly, failed proxy lookups should also be persisted, so we don't do it each time we miss the event ABI.
* Since log entries are independent, event processing should be done via multithreading.
* Better testing, error handling, etc...