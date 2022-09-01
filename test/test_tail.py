import unittest
import json
from src.classes import Event
import src.tail as tail


class TestEventtail(unittest.TestCase):
    def test_get_contract_abi(self):
        abi = tail.get_contract_abi("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        expected_abi = json.loads(open("test/fixtures/weth_abi.json").read())
        self.assertEqual(abi, expected_abi)

    def test_abi_to_event_signatures(self):
        abi = tail.get_contract_abi("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        signatures = tail.abi_to_event_signatures(abi)

        self.assertIn(
            # Classic Transfer event
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            signatures,
        )

        event = signatures[
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
        ]
        self.assertEqual(event.name, "Transfer")

    def test_get_proxied_to(self):
        proxied_to = tail.get_proxied_to("0x949b3B3c098348b879C9e4F15cecc8046d9C8A8c")
        self.assertEqual(proxied_to, "0xfe7de3c1e1bd252c67667b56347cabfc6df08df4")
