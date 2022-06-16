// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

interface IStrategyCVX {
    function claimBribeFromVotium(
        address votiumTree,
        address token,
        uint256 index,
        address account,
        uint256 amount,
        bytes32[] memory merkleProof
    ) external;

    function claimBribesFromVotium(
        address votiumTree,
        address account,
        address[] memory tokens,
        uint256[] memory indexes,
        uint256[] memory amounts,
        bytes32[][] memory merkleProofs
    ) external;
}
