# WoT Implementations in the Wild

## Coracle (Client)
GitHub: https://github.com/coracle-social/coracle
- Full-featured Nostr client with WoT integration
- Trust scores based on follow graph
- Content filtering by trust level
- Shows WoT distance on profiles

## strfry (Relay)
GitHub: https://github.com/hoytech/strfry
- High-performance C++ relay
- Write policy plugins for custom filtering
- Can use WoT via external plugin scripts
- Example: only accept events from N-hop network

## Haven (Personal Relay)
GitHub: https://github.com/bitvora/haven
- Personal relay server
- Built-in WoT-based filtering
- Imports trust from your follow list
- Blocks spam at relay level

## nostr-tools (Library)
GitHub: https://github.com/nbd-wtf/nostr-tools
- JavaScript/TypeScript Nostr library
- Functions for fetching follow graphs
- Building blocks for WoT implementations

## Notable WoT Algorithms

### Simple Hop Count
Trust = 1 / (hops + 1)
- Direct follow = 1.0
- 2 hops = 0.5
- 3 hops = 0.33

### PageRank Style
Weight follows by how many followers the person has
- More popular = stronger signal
- Prevents single-path manipulation

### Zap Weighted
Include economic signals in trust calculation
- Zaps received = endorsement
- Zap amount = strength of signal

### Negative Signals
- Mutes reduce trust
- Reports reduce trust
- Blocks propagate through network
