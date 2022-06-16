// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

import "interfaces/gnosis/IGnosisSafe.sol";

/*
 * @title   SpeedScopedModule
 * @author  Petrovska @ BadgerDAO
 * @dev  Allows whitelisted executors to trigger specific methods in targetted contracts
 * in our case to enable bribes processing quicker
 * Inspired from: https://github.com/gnosis/zodiac-guard-scope
 */
contract SpeedScopedModule {
    using EnumerableSet for EnumerableSet.AddressSet;

    /* ========== STRUCT ========== */
    struct Target {
        bool allowed;
        bool scoped;
        mapping(bytes4 => bool) allowedFunctions;
    }

    /* ========== STATE VARIABLES ========== */
    address public governance;
    address public safe;

    EnumerableSet.AddressSet internal _executors;

    mapping(address => Target) public allowedTargets;

    /* ========== EVENT ========== */
    event SetTargetAllowed(address target, bool allowed);
    event SetTargetScoped(address target, bool scoped);
    event SetFunctionAllowedOnTarget(
        address target,
        bytes4 functionSig,
        bool allowed
    );

    constructor(address _governance, address _safe) {
        governance = _governance;
        safe = _safe;
    }

    /***************************************
                    MODIFIERS
    ****************************************/
    modifier onlyGovernance() {
        require(msg.sender == governance, "not-governance!");
        _;
    }

    modifier onlyExecutors() {
        require(_executors.contains(msg.sender), "not-executor!");
        _;
    }

    /***************************************
               ADMIN - GOVERNANCE
    ****************************************/

    function setTargetAllowed(address target, bool allow)
        external
        onlyGovernance
    {
        allowedTargets[target].allowed = allow;
        emit SetTargetAllowed(target, allowedTargets[target].allowed);
    }

    function setScoped(address target, bool scoped) public onlyGovernance {
        allowedTargets[target].scoped = scoped;
        emit SetTargetScoped(target, allowedTargets[target].scoped);
    }

    function setAllowedFunction(
        address target,
        bytes4 functionSig,
        bool allow
    ) public onlyGovernance {
        allowedTargets[target].allowedFunctions[functionSig] = allow;
        emit SetFunctionAllowedOnTarget(
            target,
            functionSig,
            allowedTargets[target].allowedFunctions[functionSig]
        );
    }

    function addExecutor(address _executor) external onlyGovernance {
        require(_executor != address(0), "zero-address!");
        _executors.add(_executor);
    }

    function removeExecutor(address _executor) external onlyGovernance {
        require(_executor != address(0), "zero-address!");
        _executors.remove(_executor);
    }

    /***************************************
               ADMIN - EXECUTORS
    ****************************************/

    function checkTransactionAndExecute(address to, bytes calldata data)
        external
        onlyExecutors
    {
        require(allowedTargets[to].allowed, "not-allowed!");

        if (data.length >= 4) {
            require(
                !allowedTargets[to].scoped ||
                    allowedTargets[to].allowedFunctions[bytes4(data)],
                "function-not-allowed!"
            );

            require(
                IGnosisSafe(safe).execTransactionFromModule(
                    to,
                    0,
                    data,
                    IGnosisSafe.Operation.Call
                ),
                "exec-error!"
            );
        }
    }

    /***************************************
               PUBLIC FUNCTION
    ****************************************/

    function getExecutors() public view returns (address[] memory) {
        return _executors.values();
    }

    function isAllowedFunction(address target, bytes4 functionSig)
        public
        view
        returns (bool)
    {
        return (allowedTargets[target].allowedFunctions[functionSig]);
    }
}
