import json
import os

from brownie import reverts
from brownie.exceptions import VirtualMachineError

# based on: https://github.com/Badger-Finance/badger-multisig/blob/225e5ba20711ad67732bd896434223b46ff49881/great_ape_safe/ape_api/badger.py#L90
def _generate_data(strategy, merkle, claimable_tokens, safe):
    aggregate = {"tokens": [], "indexes": [], "amounts": [], "proofs": []}
    for symbol, token_addr in claimable_tokens.items():
        directory = "data/Votium/merkle/"
        try:
            last_json = sorted(os.listdir(directory + symbol))[-1]
        except FileNotFoundError:
            # given token is not a votium reward
            continue
        with open(directory + symbol + f"/{last_json}") as f:
            try:
                leaf = json.load(f)["claims"][strategy.address]
            except KeyError:
                # no claimables for the strat for this particular token
                continue
            try:
                strategy.claimBribeFromVotium.call(
                    merkle,
                    token_addr,
                    leaf["index"],
                    strategy.address,
                    leaf["amount"],
                    leaf["proof"],
                    {"from": safe},
                )
            except VirtualMachineError as e:
                if str(e) == "revert: Drop already claimed.":
                    continue
                if str(e) == "revert: SafeERC20: low-level call failed":
                    # $ldo claim throws this on .call, dont know why
                    pass
                if str(e) == "revert: amount should be > 0":
                    # i think jumps for USDN, but it should be there
                    pass
                else:
                    raise
            aggregate["tokens"].append(token_addr)
            aggregate["indexes"].append(leaf["index"])
            aggregate["amounts"].append(leaf["amount"])
            aggregate["proofs"].append(leaf["proof"])
    if len(aggregate["tokens"]) > 0:
        data = strategy.claimBribesFromVotium.encode_input(
            merkle,
            strategy.address,
            aggregate["tokens"],
            aggregate["indexes"],
            aggregate["amounts"],
            aggregate["proofs"],
        )
    return data


def test_bribes_claim(
    speed_module,
    strategy_vested_cvx,
    bribes_processor,
    safe,
    multi_merkle_stash,
    executor,
    deployer,
    bribes_tokens_claimable,
    interface,
):
    round_20 = ["ALCX", "FXS", "STG", "USDN"]
    check_balances = {}
    # initial balances for ALCX, FXS, STG & USDN
    for symbol in round_20:
        bal = interface.ERC20(bribes_tokens_claimable[symbol]).balanceOf(
            bribes_processor
        )
        check_balances[symbol] = bal

    # trigger claim
    with reverts("function-not-allowed!"):
        speed_module.checkTransactionAndExecute(
            strategy_vested_cvx.address,
            "0xa308025d",  # 'claimBribeFromVotium': "0xba083627"
            {"from": executor},
        )

    with reverts("not-executor!"):
        speed_module.checkTransactionAndExecute(
            strategy_vested_cvx.address,
            "0xa308025d",  # 'claimBribeFromVotium': "0xba083627"
            {"from": deployer},
        )

    speed_module.checkTransactionAndExecute(
        strategy_vested_cvx.address,
        _generate_data(
            strategy_vested_cvx, multi_merkle_stash, bribes_tokens_claimable, safe
        ),
        {"from": executor},
    )

    # here we know that for ALCX, FXS, STG & USDN balances should increase in the processor
    print("print", check_balances)
    for symbol in round_20:
        bal = interface.ERC20(bribes_tokens_claimable[symbol]).balanceOf(
            bribes_processor
        )
        assert bal > check_balances[symbol]
