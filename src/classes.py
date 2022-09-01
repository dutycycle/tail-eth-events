from dataclasses import dataclass, field
from typing import Any
from web3 import Web3

Abi = "list[dict]"
Address = str


@dataclass
class EventArg:
    name: str = ""
    type: str = "bytes32"
    value: Any = None
    indexed: bool = False


@dataclass
class Event:
    contract: Address = None
    name: str = "Anonymous/Unknown"
    args: "list[EventArg]" = field(default_factory=list)
    proxied_to: Address = None

    def full_signature(self) -> str:
        args_str = ",".join(
            [
                f"{'indexed ' if a.indexed else ''}{a.type} {a.name}={a.value}"
                for a in self.args
            ]
        )
        return f"{self.name}({args_str})"

    def abi_signature(self) -> str:
        args_str = ",".join([a.type for a in self.args])
        return f"{self.name}({args_str})"

    def keccak(self) -> str:
        return Web3.keccak(text=self.abi_signature()).hex()
