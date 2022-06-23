// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

interface IBribesProcessor {
    function BALANCE_ERC20() external view returns (bytes32);

    function KIND_SELL() external view returns (bytes32);

    function SETTLEMENT() external view returns (address);

    function sellBribeForWeth(
        CowSwapSeller.Data memory orderData,
        bytes memory orderUid
    ) external;

    function swapWethForBadger(
        CowSwapSeller.Data memory orderData,
        bytes memory orderUid
    ) external;

    function swapWethForCVX(
        CowSwapSeller.Data memory orderData,
        bytes memory orderUid
    ) external;
}

interface CowSwapSeller {
    struct Data {
        address sellToken;
        address buyToken;
        address receiver;
        uint256 sellAmount;
        uint256 buyAmount;
        uint32 validTo;
        bytes32 appData;
        uint256 feeAmount;
        bytes32 kind;
        bool partiallyFillable;
        bytes32 sellTokenBalance;
        bytes32 buyTokenBalance;
    }
}
