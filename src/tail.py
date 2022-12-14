import code
import json
import os
import requests
from classes import Abi, Address, Event, EventArg
import time
from web3 import Web3


ETH_NODE_WEBSOCKET = os.environ["ETH_NODE_WEBSOCKET"]
ETHERSCAN_API_KEY = os.environ["ETHERSCAN_API_KEY"]

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# standard slot for storing address of a proxy's implementation contract
# see https://eips.ethereum.org/EIPS/eip-1967 for details
PROXY_IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"

# polling time for checking for next block; can be short since processing events in block is slow
POLL_TIME_SECONDS=1

 # should be in some type of  persistent storage; we map zero address to empty abi since it
 # appears often while searching for proxy implementations
contract_abis : "dict[str,Abi]" = {ZERO_ADDRESS: []}

w3 = Web3(Web3.WebsocketProvider(ETH_NODE_WEBSOCKET))


def get_contract_abi(address: Address) -> Abi:
    """
    Retrieve a contract's ABI from Etherscan.
    """

    if address in contract_abis:
        return contract_abis[address]

    url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={ETHERSCAN_API_KEY}"

    try:
        response = requests.get(url, timeout=5)
    except Exception:
        # TODO: real error handling
        return []

    if response.json()["status"] == "1":
        abi = json.loads(response.json()["result"])
        contract_abis[address] = abi
        return abi

    return []


def abi_to_event_signatures(abi: Abi) -> "dict[str,Event]":
    """
    Given a contract ABI as a list of Python dictionaries, extract events and return a dict mapping
    their hashed signature to the
    """

    signatures: dict[str, Event] = {}

    for event_abi in filter(lambda x: x["type"] == "event", abi):
        name = event_abi["name"]
        args = [
            EventArg(name=i["name"], type=i["type"], indexed=i["indexed"])
            for i in event_abi["inputs"]
        ]
        event = Event(name=name, args=args)
        signatures[event.keccak()] = event

    return signatures


def get_proxied_to(addr: Address) -> Address:
    """
    If we believe that a contract is a proxy, try to find the contract it proxies to. We do this by
    reading the EIP-1967 storage slot. If the contract isn't a proxy this result could be the zero
    address or a bytestring that corresponds to some other contract, but that's not a huge deal since
    we're just trying to find matching event ABIs.
    """

    # there's also some older proxy slots that were used before EIP-1967 that you could add in
    proxied_addr = w3.eth.get_storage_at(addr, PROXY_IMPLEMENTATION_SLOT)

    return "0x" + proxied_addr.hex()[26:]


def log_to_event(log) -> Event:
    """
    Given a log, return an Event object.
    """

    addr = log['address']
    event = Event(contract=addr)
    proxied_to = None

    topics = log["topics"]
    abi = get_contract_abi(addr)
    signatures = abi_to_event_signatures(abi)

    # if not found, try looking at proxied contract.
    # we should persist a failed proxy lookup to reduce calls.
    if topics[0].hex() not in signatures:
        proxied_to = get_proxied_to(addr)
        abi = get_contract_abi(proxied_to)
        signatures = abi_to_event_signatures(abi)

    if topics[0].hex() in signatures:
        event = signatures[topics[0].hex()]
        event.contract = addr
        event.proxied_to = proxied_to

    # decode topics to get values for indexed args
    indexed_args = [arg for arg in event.args if arg.indexed]
    for arg, topic in zip(indexed_args, topics[1:]):
        arg.value = w3.codec.decode_single(arg.type, topic)

    # decode data to get values for unindexed args
    unindexed_args = [arg for arg in event.args if not arg.indexed]
    if len(unindexed_args) > 0:
        data = Web3.toBytes(hexstr=log["data"])
        decoded_data = w3.codec.decode_abi([a.type for a in unindexed_args], data)
        for arg, decoded_arg in zip(unindexed_args, decoded_data):
            arg.value = decoded_arg

    return event


if __name__ == "__main__":
    last_block = 0

    while True:
        cur_block = w3.eth.get_block_number()
        if cur_block != last_block:
            for log in w3.eth.get_logs({}):
                event = log_to_event(log)
                proxy_out = (
                    f", ProxiedTo {event.proxied_to}" if event.proxied_to else ""
                )
                print(
                    f"[Block {cur_block}] [Contract {event.contract}{proxy_out}] {event.full_signature()}"
                )
            last_block = cur_block
        time.sleep(POLL_TIME_SECONDS)
