# Understanding the Nostr Social Graph

## Event Types That Define Relationships

### Kind 3: Follow List
The core social graph primitive. Contains all pubkeys a user follows.

```json
{
  "kind": 3,
  "tags": [
    ["p", "pubkey1", "relay-url", "petname"],
    ["p", "pubkey2", "relay-url", "petname"]
  ]
}
```

### Kind 10000: Mute List
Negative signal - users/content to hide.

### Kind 10001: Pin List
Positive signal - favorited content.

### Kind 30000: Profile Badges
Credentials and achievements.

### Kind 1984: Reports
Moderation signal for problematic content.

## Graph Traversal Strategies

### Breadth-First (Hop-Based)
1. Start with user's follows
2. Expand to follows-of-follows
3. Continue to desired depth

Best for: Quick trust assessment, spam filtering

### Weighted Traversal
Weight edges by:
- Recency of follow
- Mutual follows (bidirectional)
- Interaction frequency (zaps, replies)

Best for: Recommendation, relevance ranking

### Reverse Traversal
Find who follows a target pubkey.
Useful for: Influence measurement, sybil detection

## Practical Considerations

### Caching
- Follow lists change infrequently
- Cache aggressively (hours to days)
- Subscribe to kind 3 for real-time updates

### Partial Graphs
- Full graph is too large to fetch
- Use sampling or probabilistic structures
- Focus on relevant subgraph

### Relay Selection
- Different relays have different coverage
- Use NIP-65 relay lists
- Query multiple relays for completeness

## Trust Score Algorithms

### Simple Distance
```
score = 1 / (hops + 1)
```

### Mutual Connection Boost
```
if target follows user:
    score *= 1.5
```

### Activity Decay
```
lastActive = days since last event
score *= exp(-0.01 * lastActive)
```

### Zap Integration
```
zapScore = log(1 + totalZapsReceived)
finalScore = hopScore * 0.6 + zapScore * 0.4
```
