import requests
from datetime import datetime
from pprint import pprint

from brownie import web3

API_URL = "https://barn.api.cow.fi/mainnet/api/v1/"


def _cow_sell(
    sell_token,
    mantissa_sell,
    buy_token,
    mantissa_buy,
    deadline,
    coef,
    destination,
    origin,
):
    # make sure mantissa is an integer
    assert type(mantissa_sell) == int

    # get the fee and exact amount to buy after fee
    fee_and_quote_payload = {
        "sellToken": sell_token,
        "buyToken": buy_token,
        "sellAmountBeforeFee": mantissa_sell,
    }
    print("FEE AND QUOTE PAYLOAD:")
    pprint(fee_and_quote_payload)
    print("")

    r = requests.get(API_URL + "feeAndQuote/sell", params=fee_and_quote_payload)
    print("FEE AND QUOTE RESPONSE:")
    pprint(r.json())
    print("")
    assert r.ok and r.status_code == 200

    # grab values needed to post the order to the api
    fee_amount = int(r.json()["fee"]["amount"])

    if mantissa_buy:
        # overwrite quote in case order has a limit
        assert type(mantissa_buy) == int
        buy_amount_after_fee = mantissa_buy
    else:
        # simplify for now, for quicker test flow
        buy_amount_after_fee = int(int(r.json()["buyAmountAfterFee"]) * coef)

    # add deadline to current block timestamp
    ts_now = datetime.timestamp(datetime.now())
    deadline = int(ts_now + deadline)

    # submit order
    order_payload = {
        "sellToken": sell_token,
        "buyToken": buy_token,
        "receiver": destination,
        "sellAmount": str(mantissa_sell - fee_amount),
        "buyAmount": str(buy_amount_after_fee),
        "validTo": str(
            deadline
        ),  # tweak deadline cause we're forking on the past, so validTo will end-up being on the past...
        "appData": web3.keccak(text="speed_scoped_module_test").hex(),
        "feeAmount": str(fee_amount),
        "kind": "sell",
        "partiallyFillable": False,
        "sellTokenBalance": "erc20",
        "buyTokenBalance": "erc20",
        "signingScheme": "presign",
        "signature": origin,
        "from": origin,
    }

    print("ORDER PAYLOAD")
    pprint(order_payload)
    print("")

    r = requests.post(f"{API_URL}orders", json=order_payload)
    order_uid = r.json()
    print("ORDER RESPONSE")
    pprint(order_uid)
    print("")
    assert r.ok and r.status_code == 201

    return order_payload, order_uid


def _get_order_for_processor(
    processor,
    sell_token,
    mantissa_sell,
    buy_token,
    mantissa_buy=None,
    deadline=60 * 60,
    coef=1,
):
    order_payload, order_uid = _cow_sell(
        sell_token,
        mantissa_sell,
        buy_token,
        mantissa_buy,
        deadline,
        coef,
        destination=processor.address,
        origin=processor.address,
    )
    order_payload["kind"] = str(processor.KIND_SELL())
    order_payload["sellTokenBalance"] = str(processor.BALANCE_ERC20())
    order_payload["buyTokenBalance"] = str(processor.BALANCE_ERC20())
    order_payload.pop("signingScheme")
    order_payload.pop("signature")
    order_payload.pop("from")
    order_payload = tuple(order_payload.values())

    return order_payload, order_uid


def test_swap_to_weth(
    speed_module,
    bribes_processor,
    executor,
    bribes_tokens_claimable,
    round_20_tokens,
    interface,
):
    for symbol in round_20_tokens:
        addr = bribes_tokens_claimable[symbol]
        bal = interface.ERC20(addr).balanceOf(bribes_processor)

        if bal > 0:
            print(
                f" ==== About to process {symbol} with a balance of {bal} for WETH.... ==== \n"
            )
            order_payload, order_uid = _get_order_for_processor(
                sell_token=addr,
                mantissa_sell=int(bal),
                buy_token="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
                coef=0.99,
                processor=bribes_processor,
            )

            data = bribes_processor.sellBribeForWeth.encode_input(
                order_payload, order_uid
            )

            speed_module.checkTransactionAndExecute(
                bribes_processor.address,
                data,
                {"from": executor},
            )
