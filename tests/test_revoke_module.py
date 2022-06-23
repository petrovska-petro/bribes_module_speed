from brownie import reverts


def test_revoke_whitelisting(safe, speed_module, strategy_vested_cvx, executor):
    # https://etherscan.io/address/0x34cfac646f301356faa8b21e94227e3583fe3f5f#code#L171
    SENTINEL_MODULES = "0x0000000000000000000000000000000000000001"
    safe.disableModule(SENTINEL_MODULES, speed_module.address, {"from": safe})

    with reverts("Method can only be called from an enabled module"):
        speed_module.checkTransactionAndExecute(
            strategy_vested_cvx.address,
            "0xa308025c",
            {"from": executor},
        )
