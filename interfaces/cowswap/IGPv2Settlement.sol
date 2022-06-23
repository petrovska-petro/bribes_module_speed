// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

interface IGPv2Settlement {
    function preSignature(bytes calldata orderUid)
        external
        view
        returns (uint256);
}
