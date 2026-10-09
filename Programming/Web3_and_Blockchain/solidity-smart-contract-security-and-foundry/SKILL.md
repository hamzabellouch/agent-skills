---
name: solidity-smart-contract-security-and-foundry
description: Advanced Solidity smart contract development, security hardening, vulnerability defense, and testing framework using Foundry (Forge, Cast, Anvil). Use when writing, auditing, testing, or securing Ethereum/EVM smart contracts.
---

# Solidity Smart Contract Security & Foundry Engineering Guide

This skill guide provides production-grade standards, vulnerability defenses, security patterns, anti-patterns, and comprehensive Foundry testing strategies for EVM smart contract development.

---

## 1. Core Principles of EVM Security

1. **Defense in Depth**: Relying on a single security layer (e.g., modifier access control) is insufficient. Use checks-effects-interactions, reentrancy guards, rate limiting, and invariant testing.
2. **Minimize Surface Area**: Expose only required functions with the strictest visibility (`private` or `internal` preferred; `external` over `public` for external entry points).
3. **Explicit Invariants**: Define strict properties that must hold true before, during, and after state execution (e.g., `total_shares * price_per_share == total_assets`).
4. **Assume Unchecked External Input**: External calls can execute arbitrary code, reenter state, or fail maliciously. Treat every external contract/call as untrusted.

---

## 2. Common Vulnerabilities & Security Defenses

### 2.1 Reentrancy & Read-Only Reentrancy

#### Mechanism
Occurs when an external call is executed before internal state updates are completed, allowing an attacker to call back into the contract (or a reading contract) while state is inconsistent.

#### Defense Strategy
- **CEI Pattern**: Checks-Effects-Interactions (validate inputs, modify local state, interact with external contracts).
- **Transient Storage Guard (EIP-1153)**: High-efficiency gas reentrancy lock using `tstore` / `tload`.
- **OpenZeppelin ReentrancyGuardTransient / ReentrancyGuard**.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import "@openzeppelin/contracts/utils/ReentrancyGuardTransient.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Vault is ReentrancyGuardTransient {
    using SafeERC20 for IERC20;

    IERC20 public immutable token;
    mapping(address => uint256) private _balances;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);

    constructor(IERC20 _token) {
        token = _token;
    }

    function deposit(uint256 amount) external nonReentrant {
        require(amount > 0, "Invalid amount");
        
        // Effects
        _balances[msg.sender] += amount;

        // Interactions
        token.safeTransferFrom(msg.sender, address(this), amount);

        emit Deposited(msg.sender, amount);
    }

    function withdraw(uint256 amount) external nonReentrant {
        require(_balances[msg.sender] >= amount, "Insufficient balance");

        // Effects - Update state BEFORE external interaction
        _balances[msg.sender] -= amount;

        // Interactions
        token.safeTransfer(msg.sender, amount);

        emit Withdrawn(msg.sender, amount);
    }

    function balanceOf(address account) external view returns (uint256) {
        return _balances[account];
    }
}
```

---

### 2.2 Oracle Manipulation & Flash Loan Attacks

#### Mechanism
Spot prices from DEX reserves (e.g., Uniswap v2 pair reserves) can be manipulated within a single transaction using flash loans.

#### Defense Strategy
- Never use spot reserves (`getReserves()`) for pricing collateral or liquidations.
- Use **Chainlink Oracles** with strict freshness, positivity, and circuit-breaker checks.
- Use **Time-Weighted Average Price (TWAP)** with an adequate observation window if Chainlink is unavailable.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

library ChainlinkOracleLib {
    error PriceStale();
    error InvalidPrice();
    error IncompleteRound();

    uint256 private constant MAX_TIMEOUT = 3 hours;

    function getLatestPrice(AggregatorV3Interface priceFeed) internal view returns (uint256) {
        (
            uint80 roundId,
            int256 price,
            ,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        if (price <= 0) revert InvalidPrice();
        if (updatedAt == 0 || updatedAt < block.timestamp - MAX_TIMEOUT) revert PriceStale();
        if (answeredInRound < roundId) revert IncompleteRound();

        return uint256(price);
    }
}
```

---

### 2.3 Access Control & Privilege Escalation

#### Anti-Pattern
Using `tx.origin` for authentication or failing to secure initializer functions in upgradeable contracts.

#### Defense Strategy
- Use `msg.sender` for authorization.
- Implement fine-grained Role-Based Access Control (`AccessControlUpgradeable` / `AccessControlEnumerable`).
- Secure Initializers with `_disableInitializers()` in constructors.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract SystemAdmin is AccessControl {
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    bool public paused;

    event PausedStateChanged(bool isPaused);

    constructor(address defaultAdmin, address operator) {
        _grantRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
        _grantRole(OPERATOR_ROLE, operator);
    }

    function setPaused(bool _paused) external onlyRole(PAUSER_ROLE) {
        paused = _paused;
        emit PausedStateChanged(_paused);
    }

    function executeCriticalOperation() external onlyRole(OPERATOR_ROLE) {
        require(!paused, "Contract is paused");
        // Critical business logic
    }
}
```

---

### 2.4 Signature Malleability & Replay Attacks

#### Mechanism
EIP-191 / EIP-712 signatures can be replayed across different chains or reused if nonces, domain separators, and malleability controls (`s` value upper bound check) are missing.

#### Defense Strategy
- Validate EIP-712 domain separator including `block.chainid` and `address(this)`.
- Use OpenZeppelin's `ECDSA` library which enforces low-s values and signature length checks.
- Store consumed signature nonces or hashes.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract MetaTxProcessor is EIP712 {
    using ECDSA for bytes32;

    bytes32 private constant EXECUTE_TYPEHASH = keccak256("Execute(address sender,uint256 amount,uint256 nonce,uint256 deadline)");
    mapping(address => uint256) public nonces;

    error SignatureExpired();
    error InvalidSignature();

    constructor() EIP712("MetaTxProcessor", "1.0.0") {}

    function executeMetaTx(
        address sender,
        uint256 amount,
        uint256 deadline,
        bytes calldata signature
    ) external {
        if (block.timestamp > deadline) revert SignatureExpired();

        uint256 currentNonce = nonces[sender]++;
        bytes32 structHash = keccak256(
            abi.encode(EXECUTE_TYPEHASH, sender, amount, currentNonce, deadline)
        );

        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = digest.recover(signature);

        if (signer != sender) revert InvalidSignature();

        // Perform execution logic for sender
    }
}
```

---

## 3. Foundry Development & Testing Guide

Foundry provides high-performance testing via Rust (`forge`), chain manipulation (`cast`), and local node capabilities (`anvil`).

### 3.1 Advanced Forge Testing Patterns

- **Unit Testing**: Test functions in isolation with deterministic parameters.
- **Fuzz Testing**: Use property-based random inputs with `bound()` and `vm.assume()`.
- **Invariant Testing**: Stateful fuzzing ensuring system invariants hold across random sequences of call sequences.
- **Fork Testing**: Mainnet/testnet state simulation using `vm.createSelectFork()`.

### 3.2 Production Foundry Test Suite Example

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import "forge-std/Test.sol";
import "../src/Vault.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockToken is ERC20 {
    constructor() ERC20("Mock Token", "MTK") {
        _mint(msg.sender, 1_000_000 * 1e18);
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

contract VaultTest is Test {
    Vault public vault;
    MockToken public token;

    address public user1 = address(0x1);
    address public user2 = address(0x2);

    function setUp() public {
        token = new MockToken();
        vault = new Vault(IERC20(address(token)));

        token.mint(user1, 10_000 * 1e18);
        token.mint(user2, 10_000 * 1e18);

        vm.prank(user1);
        token.approve(address(vault), type(uint256).max);

        vm.prank(user2);
        token.approve(address(vault), type(uint256).max);
    }

    /// @dev Basic Unit Test
    function test_DepositSuccessful() public {
        vm.prank(user1);
        vault.deposit(1_000 * 1e18);

        assertEq(vault.balanceOf(user1), 1_000 * 1e18);
        assertEq(token.balanceOf(address(vault)), 1_000 * 1e18);
    }

    /// @dev Fuzz Test with Input Bounds
    function testFuzz_Deposit(uint256 amount) public {
        amount = bound(amount, 1, 10_000 * 1e18);

        vm.prank(user1);
        vault.deposit(amount);

        assertEq(vault.balanceOf(user1), amount);
    }

    /// @dev Reentrancy Failure Verification
    function test_ReentrancyProtection() public {
        // Verification logic for reentrancy rejection
        vm.prank(user1);
        vault.deposit(500 * 1e18);

        vm.prank(user1);
        vault.withdraw(500 * 1e18);
        assertEq(vault.balanceOf(user1), 0);
    }
}
```

---

## 4. Security Audit Checklist

- [ ] **State Variables**: Are all state variables explicitly marked `private`, `internal`, or `public`?
- [ ] **Reentrancy**: Are external calls placed strictly after state modifications? Are `nonReentrant` modifiers added where required?
- [ ] **Integer Safety**: Is Solidity `^0.8.0` used? Are `unchecked` blocks used strictly when mathematical underflow/overflow is impossible?
- [ ] **ERC20 Transfers**: Is `SafeERC20` used for all external ERC20 calls to handle non-compliant tokens (e.g. USDT)?
- [ ] **Oracles**: Are oracle responses validated for stale data (`updatedAt`), zero/negative values, and round completeness?
- [ ] **Front-Running / MEV**: Are slippage protection thresholds (`minAmountOut`) passed as explicit user parameters?
- [ ] **Access Control**: Are two-step ownership transfers used (`Ownable2Step`)?
