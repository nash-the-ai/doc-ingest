# Web of Trust Core Concepts

## What is Web of Trust?

Web of Trust (WoT) is a decentralized trust model where trust is established through a network of cryptographic signatures and social relationships rather than centralized authorities.

## Key Principles

### 1. Transitive Trust
If Alice trusts Bob, and Bob trusts Carol, Alice can derive some level of trust in Carol. Trust decreases with distance (hops).

### 2. Follow Graphs
In Nostr, the follow graph (kind 3 events) forms the foundation of WoT. Who you follow, and who they follow, defines your trust network.

### 3. Trust Signals
- **Direct follows** - Strongest signal
- **Follows of follows** - Weaker but useful
- **Mutes** - Negative signal
- **Zaps** - Economic signal of value
- **Reactions** - Engagement signal
- **Reposts** - Endorsement signal

### 4. Trust Tiers
Common tiering:
- Tier 0: Self
- Tier 1: Direct follows (1 hop)
- Tier 2: Follows of follows (2 hops)
- Tier 3+: Extended network

## Nostr WoT Implementation Patterns

### Relay-Based Filtering
Relays can use WoT to filter spam. strfry's write policy plugin is an example.

### Client-Based Ranking
Clients can rank/filter content based on trust scores. Coracle does this.

### Hybrid Approaches
Combine relay filtering with client-side scoring for best UX.

## Key NIPs for WoT

- NIP-01: Basic protocol
- NIP-02: Follow lists
- NIP-51: Lists (mutes, pins, etc.)
- NIP-56: Reporting
- NIP-57: Zaps
- NIP-65: Relay lists

## Challenges

1. **Cold start** - New users have no trust graph
2. **Sybil attacks** - Fake identities
3. **Trust decay** - Old follows may be stale
4. **Computational cost** - Large graphs expensive to traverse
5. **Privacy** - Follow graphs are public

## Applications

1. **Spam filtering** - Only show content from trusted sources
2. **Relay policies** - Only accept events from trusted pubkeys
3. **Search ranking** - Weight results by trust
4. **Recommendation** - Suggest follows from trusted network
5. **Moderation** - Community-based content filtering
