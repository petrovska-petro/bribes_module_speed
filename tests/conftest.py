import pytest
from brownie import web3, interface, SpeedScopedModule


@pytest.fixture
def deployer(accounts):
    return accounts[0]


@pytest.fixture
def governance(accounts):
    return accounts[1]


@pytest.fixture
def executor(accounts):
    return accounts[2]


@pytest.fixture
def multi_merkle_stash():
    return "0x378Ba9B73309bE80BF4C2c027aAD799766a7ED5A"


@pytest.fixture
def bribes_processor():
    return interface.IBribesProcessor("0xb2Bf1d48F2C2132913278672e6924efda3385de2")


@pytest.fixture
def settlement(bribes_processor):
    return interface.IGPv2Settlement(bribes_processor.SETTLEMENT())


@pytest.fixture
def strategy_vested_cvx():
    return interface.IStrategyCVX("0x898111d1F4eB55025D0036568212425EE2274082")


@pytest.fixture
def bribes_tokens_claimable():
    return {
        "CVX": "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
        "BADGER": "0x3472A5A71965499acd81997a54BBA8D852C6E53d",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "SPELL": "0x090185f2135308bad17527004364ebcc2d37e5f6",
        "ALCX": "0xdbdb4d16eda451d0503b854cf79d55697f90c8df",
        "NSBT": "0x9D79d5B61De59D882ce90125b18F74af650acB93",
        "MATIC": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
        "FXS": "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0",
        "LDO": "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",
        "TRIBE": "0xc7283b66Eb1EB5FB86327f08e1B5816b0720212B",
        "OGN": "0x8207c1FfC5B6804F6024322CcF34F29c3541Ae26",
        "MTA": "0xa3BeD4E1c75D00fa6f4E5E6922DB7261B5E9AcD2",
        "ANGLE": "0x31429d1856aD1377A8A0079410B297e1a9e214c2",
        "T": "0xCdF7028ceAB81fA0C6971208e83fa7872994beE5",
        "UST": "0xa693B19d2931d498c5B318dF961919BB4aee87a5",  # USTv2 (wormhole)
        "LFT": "0xB620Be8a1949AA9532e6a3510132864EF9Bc3F82",
        "FLX": "0x6243d8CEA23066d098a15582d81a598b4e8391F4",
        "GRO": "0x3Ec8798B81485A254928B70CDA1cf0A2BB0B74D7",
        "STG": "0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6",
        "EURS": "0xdB25f211AB05b1c97D595516F45794528a807ad8",
        "USDN": "0x674C6Ad92Fd080e4004b2312b45f796a192D27a0",
    }


@pytest.fixture
def round_20_tokens():
    return ["ALCX", "FXS", "STG", "USDN"]


@pytest.fixture
def confirm_signed():
    # https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41#code#F14#L40
    return int(
        web3.solidityKeccak(["string"], ["GPv2Signing.Scheme.PreSign"]).hex(), 16
    )


@pytest.fixture
def safe():
    return interface.IGnosisSafe("0x86cbD0ce0c087b482782c181dA8d191De18C8275")


@pytest.fixture
def speed_module(deployer, governance, safe):
    return SpeedScopedModule.deploy(governance, safe.address, {"from": deployer})


@pytest.fixture(autouse=True)
def config_module(
    safe, speed_module, governance, executor, bribes_processor, strategy_vested_cvx
):
    # enable module
    safe.enableModule(speed_module.address, {"from": safe})
    assert speed_module.address in safe.getModules()

    # add executor
    speed_module.addExecutor(executor, {"from": governance})

    # allow targets
    speed_module.setTargetAllowed(bribes_processor.address, True, {"from": governance})
    speed_module.setTargetAllowed(
        strategy_vested_cvx.address, True, {"from": governance}
    )

    # scoped down
    speed_module.setScoped(bribes_processor.address, True, {"from": governance})
    speed_module.setScoped(strategy_vested_cvx.address, True, {"from": governance})

    # allow signatures
    claim_bribes_from_votium = "0xa308025c"
    speed_module.setAllowedFunction(
        strategy_vested_cvx.address,
        claim_bribes_from_votium,
        True,
        {"from": governance},
    )

    sell_bribes_for_weth = "0x34ea5b15"
    speed_module.setAllowedFunction(
        bribes_processor.address,
        sell_bribes_for_weth,
        True,
        {"from": governance},
    )

    swap_weth_for_badger = "0x772a8f36"
    speed_module.setAllowedFunction(
        bribes_processor.address,
        swap_weth_for_badger,
        True,
        {"from": governance},
    )

    swap_weth_for_cvx = "0x118a0252"
    speed_module.setAllowedFunction(
        bribes_processor.address,
        swap_weth_for_cvx,
        True,
        {"from": governance},
    )
