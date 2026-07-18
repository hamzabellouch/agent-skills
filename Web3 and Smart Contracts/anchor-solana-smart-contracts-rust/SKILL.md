---
name: anchor-solana-smart-contracts-rust
description: Production-grade Solana smart contract (program) development using Rust and the Anchor framework. Covers security vulnerability mitigation, account validation, PDA derivation, CPI safety, and TypeScript testing.
---

# Anchor Solana Smart Contracts & Rust Security Guide

This skill guide provides production-grade architecture, vulnerability defenses, security patterns, anti-patterns, and testing strategies for developing Solana programs using Rust and the **Anchor Framework**.

---

## 1. Core Principles of Solana & Anchor Security

Unlike EVM contracts where code and state reside together in a single contract account, Solana separates **code (Programs)** from **state (Accounts)**.

1. **Explicit Account Validation**: Programs must validate every account passed into an instruction (Owner, Signer, Writable, PDA Seeds/Bump, Expected Key).
2. **PDA (Program Derived Address) Hardening**: Never trust a client-provided bump without validating it against `Pubkey::find_program_address` or storing/canonicalizing the canonical bump.
3. **Strict Type Safety**: Enforce explicit discriminator checks to prevent account type spoofing ("Type Cosplaying").
4. **Checked Arithmetic**: Solana execution halts on panics; always use `checked_add`, `checked_sub`, `checked_mul`, or Anchor's safe math helpers.

---

## 2. Critical Solana Vulnerabilities & Security Defenses

### 2.1 Account Reloading & Owner Validation (Type Cosplaying)

#### Vulnerability
If an account struct does not validate that an account is owned by the expected program or derived with the expected Anchor account discriminator, an attacker can create a fake account with identical memory layout owned by a malicious program.

#### Defense
Anchor handles account discriminators automatically when using `#[account]` and `Account<'info, T>`. Never use `UncheckedAccount` unless strictly necessary and manually validated.

```rust
use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount, Transfer};

declare_id!("8xYg91X29W7dK8J5161GzV41jV7W8yXz111111111111");

#[program]
pub mod secure_vault {
    use super::*;

    pub fn initialize_vault(ctx: Context<InitializeVault>, bump: u8) -> Result<()> {
        let vault = &mut ctx.accounts.vault;
        vault.authority = ctx.accounts.authority.key();
        vault.token_account = ctx.accounts.vault_token_account.key();
        vault.bump = bump;
        Ok(())
    }

    pub fn deposit(ctx: Context<Deposit>, amount: u64) -> Result<()> {
        require!(amount > 0, VaultError::InvalidAmount);

        let cpi_accounts = Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.vault_token_account.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);

        token::transfer(cpi_ctx, amount)?;
        
        let vault = &mut ctx.accounts.vault;
        vault.total_deposited = vault
            .total_deposited
            .checked_add(amount)
            .ok_or(VaultError::MathOverflow)?;

        Ok(())
    }
}

#[derive(Accounts)]
#[instruction(bump: u8)]
pub struct InitializeVault<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + VaultState::INIT_SPACE,
        seeds = [b"vault", authority.key().as_ref()],
        bump
    )]
    pub vault: Account<'info, VaultState>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub mint: Account<'info, Mint>,

    #[account(
        init,
        payer = authority,
        token::mint = mint,
        token::authority = vault,
        seeds = [b"token_vault", vault.key().as_ref()],
        bump
    )]
    pub vault_token_account: Account<'info, TokenAccount>,

    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct Deposit<'info> {
    #[account(
        mut,
        seeds = [b"vault", vault.authority.as_ref()],
        bump = vault.bump,
        has_one = vault_token_account @ VaultError::InvalidTokenAccount
    )]
    pub vault: Account<'info, VaultState>,

    #[account(mut)]
    pub vault_token_account: Account<'info, TokenAccount>,

    #[account(
        mut,
        constraint = user_token_account.owner == user.key() @ VaultError::InvalidOwner,
        constraint = user_token_account.mint == vault_token_account.mint @ VaultError::InvalidMint
    )]
    pub user_token_account: Account<'info, TokenAccount>,

    pub user: Signer<'info>,
    pub token_program: Program<'info, Token>,
}

#[account]
#[derive(InitSpace)]
pub struct VaultState {
    pub authority: Pubkey,
    pub token_account: Pubkey,
    pub total_deposited: u64,
    pub bump: u8,
}

#[error_code]
pub enum VaultError {
    #[msg("Amount must be greater than zero")]
    InvalidAmount,
    #[msg("Math calculation resulted in overflow")]
    MathOverflow,
    #[msg("Token account mismatch")]
    InvalidTokenAccount,
    #[msg("Invalid token account owner")]
    InvalidOwner,
    #[msg("Token mint mismatch")]
    InvalidMint,
}
```

---

### 2.2 Reinitialization & Closed Account Revival

#### Vulnerability
If an account is closed (lamports drained to 0) in Solana, an attacker can re-fund the account in the same transaction or block and reinitialize it if the program doesn't set a closed discriminator or verify state flags.

#### Defense
Anchor handles closing accounts safely via `#[account(close = receiver)]`. This zeroes the account memory and writes a special `CLOSED_ACCOUNT_DISCRIMINATOR` (8 zero bytes) to prevent reuse within the same transaction.

```rust
#[derive(Accounts)]
pub struct CloseVault<'info> {
    #[account(
        mut,
        close = authority,
        has_one = authority @ VaultError::Unauthorized,
        constraint = vault.total_deposited == 0 @ VaultError::VaultNotEmpty
    )]
    pub vault: Account<'info, VaultState>,

    #[account(mut)]
    pub authority: Signer<'info>,
}
```

---

### 2.3 PDA Seed Collision & Canonical Bump Defense

#### Vulnerability
Using non-unique seeds (e.g., overlapping strings or uncontrolled user inputs) can allow two distinct logic paths to resolve to the exact same Program Derived Address (PDA).

#### Defense Strategy
- Prefix seeds with constant byte literals (`b"user_profile"`).
- Include all necessary domain identifiers (e.g., `user.key()`, `mint.key()`).
- Always validate and store the canonical bump returned by Anchor's `find_program_address`.

```rust
#[account(
    init,
    payer = payer,
    space = 8 + UserProfile::INIT_SPACE,
    seeds = [b"user_profile", user.key().as_ref()],
    bump
)]
pub profile: Account<'info, UserProfile>,
```

---

### 2.4 Arbitrary CPI & Program ID Checks

#### Vulnerability
Passing an unvalidated `AccountInfo` as a program ID when making a Cross-Program Invocation (CPI) allows an attacker to pass a malicious program that mimics standard interfaces (e.g., fake Token Program).

#### Defense
Use Anchor's strongly typed `Program<'info, System>` or `Program<'info, Token>` instead of raw `AccountInfo`.

```rust
// SECURE: Strongly typed Program check validates program ID automatically
pub token_program: Program<'info, Token>,
```

---

## 3. Production Anchor Testing with TypeScript / Mocha

Testing Anchor programs involves using `@coral-xyz/anchor` and `@solana/web3.js` with local validator test runners (`anchor test`).

```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { SecureVault } from "../target/types/secure_vault";
import {
  TOKEN_PROGRAM_ID,
  createMint,
  createAccount,
  mintTo,
  getAccount,
} from "@solana/spl-token";
import { assert } from "chai";

describe("secure_vault", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.SecureVault as Program<SecureVault>;
  const authority = provider.wallet;

  let mint: anchor.web3.PublicKey;
  let userTokenAccount: anchor.web3.PublicKey;
  let vaultPda: anchor.web3.PublicKey;
  let vaultBump: number;
  let vaultTokenPda: anchor.web3.PublicKey;

  before(async () => {
    // Create SPL Mint
    mint = await createMint(
      provider.connection,
      (authority as any).payer,
      authority.publicKey,
      null,
      6
    );

    // Deriving PDAs
    [vaultPda, vaultBump] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("vault"), authority.publicKey.toBuffer()],
      program.programId
    );

    [vaultTokenPda] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("token_vault"), vaultPda.toBuffer()],
      program.programId
    );

    // Create and mint to user token account
    userTokenAccount = await createAccount(
      provider.connection,
      (authority as any).payer,
      mint,
      authority.publicKey
    );

    await mintTo(
      provider.connection,
      (authority as any).payer,
      mint,
      userTokenAccount,
      authority.publicKey,
      1_000_000
    );
  });

  it("Initializes the vault securely", async () => {
    await program.methods
      .initializeVault(vaultBump)
      .accounts({
        vault: vaultPda,
        authority: authority.publicKey,
        mint: mint,
        vaultTokenAccount: vaultTokenPda,
        systemProgram: anchor.web3.SystemProgram.programId,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .rpc();

    const vaultAccount = await program.account.vaultState.fetch(vaultPda);
    assert.equal(vaultAccount.authority.toBase58(), authority.publicKey.toBase58());
  });

  it("Executes deposit safely", async () => {
    const depositAmount = new anchor.BN(500_000);

    await program.methods
      .deposit(depositAmount)
      .accounts({
        vault: vaultPda,
        vaultTokenAccount: vaultTokenPda,
        userTokenAccount: userTokenAccount,
        user: authority.publicKey,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .rpc();

    const vaultAccount = await program.account.vaultState.fetch(vaultPda);
    assert.equal(vaultAccount.totalDeposited.toString(), depositAmount.toString());
  });
});
```

---

## 4. Solana Security Checklist

- [ ] **Signer Check**: Are all accounts modifying state or transferring funds marked with `Signer<'info>`?
- [ ] **Owner Check**: Are all custom accounts defined using `Account<'info, T>` to enforce Anchor discriminator and program ownership checks?
- [ ] **Bump Seed Validation**: Is canonical bump passed/validated during PDA account resolution?
- [ ] **CPI Verification**: Are external program calls strictly typed using `Program<'info, TargetProgram>`?
- [ ] **Arithmetic Checks**: Are all numerical operations guarded by `checked_add`, `checked_sub`, `checked_mul`, etc.?
- [ ] **Rent Exemption**: Are newly initialized accounts guaranteed to be rent-exempt?
- [ ] **Account Closing**: Is `close = destination` used to drain lamports and clear discriminators safely when closing accounts?
