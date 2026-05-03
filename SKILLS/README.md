# App-Local Timechain Skill Notes

This folder contains documentation that the CypherTempre chat PoC is allowed to read for source-grounded Guide explanations.

The app intentionally reads only files inside `cyphertempre-chat-poc` so public demos do not accidentally expose parent-repo or machine-local files.

## Timechain

Timechain is a local, append-only memory chain for an AI agent. It stores accepted interactions as hash-linked rings so the chain can be verified later.

## Proof of Qualia

Proof of Qualia is the quality gate used before a response becomes memory. It scores a response against the user query, recalled context, existing chain, and covenant. A response that fails the gate is shown but not sealed into memory.

## Recall

Recall searches previously accepted rings and returns the most relevant local memories. Guide and chat explanations should treat recalled rings as local memory, not as live external facts.

## Self Model

The self model summarizes the local chain: ring count, temporal mass, top domains, gaps, and current verification state. It is a diagnostic view of local memory state.

## Chain Verification

Verification replays the hash chain to confirm that each ring still points to the previous ring and that no sealed memory was changed outside the normal append path.

## Source Rule

Guide explanations may use this folder, `README.md`, `.env.example`, and the Guide topic text. They should say when a requested detail is not covered by those sources.
