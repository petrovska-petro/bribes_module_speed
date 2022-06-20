// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

import "interfaces/gnosis/IGnosisSafe.sol";

/// @title   SpeedScopedModule
/// @author  Petrovska @ BadgerDAO
/// @dev  Allows whitelisted executors to trigger specific methods in targetted contracts
/// in our case to enable bribes processing quicker
/// Inspired from: https://github.com/gnosis/zodiac-guard-scope
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

    /// @dev Set whether or not calls can be made to an address.
    /// @notice Only callable by governance.
    /// @param target Address to be allowed/disallowed.
    /// @param allow Bool to allow (true) or disallow (false) calls to target.
    function setTargetAllowed(address target, bool allow)
        external
        onlyGovernance
    {
        allowedTargets[target].allowed = allow;
        emit SetTargetAllowed(target, allowedTargets[target].allowed);
    }

    /// @dev Sets whether or not calls to an address should be scoped to specific function signatures.
    /// @notice Only callable by governance.
    /// @param target Address to be scoped/unscoped.
    /// @param scoped Bool to scope (true) or unscope (false) function calls on target.
    function setScoped(address target, bool scoped) public onlyGovernance {
        allowedTargets[target].scoped = scoped;
        emit SetTargetScoped(target, allowedTargets[target].scoped);
    }

    /// @dev Sets whether or not a specific function signature should be allowed on a scoped target.
    /// @notice Only callable by governance.
    /// @param target Scoped address on which a function signature should be allowed/disallowed.
    /// @param functionSig Function signature to be allowed/disallowed.
    /// @param allow Bool to allow (true) or disallow (false) calls a function signature on target.
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

    /// @dev Adds an executor to the Set of allowed addresses.
    /// @notice Only callable by governance.
    /// @param _executor Address which will have rights to call `checkTransactionAndExecute`.
    function addExecutor(address _executor) external onlyGovernance {
        require(_executor != address(0), "zero-address!");
        _executors.add(_executor);
    }

    /// @dev Removes an executor to the Set of allowed addresses.
    /// @notice Only callable by governance.
    /// @param _executor Address which will not have rights to call `checkTransactionAndExecute`.
    function removeExecutor(address _executor) external onlyGovernance {
        require(_executor != address(0), "zero-address!");
        _executors.remove(_executor);
    }

    /***************************************
               ADMIN - EXECUTORS
    ****************************************/

    /// @dev Allows executing specific calldata into an address thru a gnosis-safe, which have enable this contract as module.
    /// @notice Only callable by executors.
    /// @param to Contract address where we will execute the calldata.
    /// @param data Calldata to be executed within the boundaries of the `allowedFunctions`.
    function checkTransactionAndExecute(address to, bytes calldata data)
        external
        onlyExecutors
    {
        require(allowedTargets[to].allowed, "address-not-allowed!");

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

    /// @dev Returns all addresses which have executor role
    function getExecutors() public view returns (address[] memory) {
        return _executors.values();
    }

    /// @dev Returns bool to indicate if a function signature is allowed for a target address.
    /// @param target Address to check.
    /// @param functionSig Signature to check.
    function isAllowedFunction(address target, bytes4 functionSig)
        public
        view
        returns (bool)
    {
        return (allowedTargets[target].allowedFunctions[functionSig]);
    }
}
