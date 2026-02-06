# WoT Design Patterns for Applications

## Pattern 1: Trust-Gated Content
Only show content from trusted sources by default.

```
if user.trustScore(author) >= threshold:
    show(content)
else:
    hide(content) or show(lowPriority)
```

## Pattern 2: Graduated Access
Different trust levels get different capabilities.

| Trust Level | Capabilities |
|-------------|--------------|
| 0 (unknown) | Read only, rate limited |
| 1 (1-hop) | Read, limited write |
| 2 (2-hop) | Read, write, react |
| 3+ (extended) | Full access |

## Pattern 3: Trust Decay
Trust should decay over time if not reinforced.

```
trust = baseTrust * exp(-λ * daysSinceInteraction)
```

## Pattern 4: Negative Signal Propagation
Mutes and blocks should propagate through network.

```
if user.mutes(target):
    for follower in user.followers:
        follower.trustScore(target) -= penalty
```

## Pattern 5: Economic Trust
Weight trust by economic signals (zaps, purchases).

```
economicTrust = sum(zapsReceived) / networkMedian
finalTrust = socialTrust * 0.7 + economicTrust * 0.3
```

## Pattern 6: Relay Reputation
Relays themselves can have trust scores.

- Uptime
- Response time  
- Spam ratio
- Community moderation quality

## Pattern 7: Cold Start Solutions
For new users with no follow graph:

1. Suggest "starter pack" follows
2. Import from other platforms
3. Use content similarity
4. NIP-05 domain trust (if @company.com, trust more)

## Pattern 8: Sybil Resistance
Prevent fake identity attacks:

1. Proof of work on identity creation
2. Vouch system (existing users vouch for new)
3. Unique human verification (optional)
4. Economic cost (zap to join)

## Pattern 9: Privacy-Preserving WoT
Don't leak full social graph:

1. Zero-knowledge proofs of trust
2. Local computation only
3. Bloom filters for membership
4. Trusted relays compute scores

## Pattern 10: Federated Moderation
Communities share moderation signals:

1. Community-specific mute lists
2. Cross-community reputation
3. Moderator trust weighting
4. Appeal mechanisms
