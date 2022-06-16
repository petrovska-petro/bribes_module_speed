# Speed Scoped Module

This repository contains the smart contract for the Module, which will allow to trigger specific methods thru the multisig in a speedy manner. E.g: will help processing bribes quicker than thru the usual multisig process.

The module is capped on two senses, one on the contracts it can point and second the methods in those contracts that can trigger methods for. This reduces the concern of the priviliages of this module significantly.

# Architecture design

[Miro sketch](https://miro.com/app/board/uXjVOtXEcWc=/)

# Requirements

Your ganache instance needs to be run on block < **14961328** to test round 20 (ALCX, FXS, STG & USDN claims).

Ref of last round 20 claim: [tx](https://etherscan.io/tx/0x688a41dead0a91eeaf03769acd9af82ac6cafb6fc6e5d5314f5c91e52f701610).

In your terminal:

```
git clone https://github.com/oo-00/Votium.git data/Votium

brownie pm clone OpenZeppelin/openzeppelin-contracts@4.5.0
```

# Contribute

Feel free to open issues or PRs for improvements!