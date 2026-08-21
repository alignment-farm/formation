# Accumulated-table container diagnostic

## Main result

Changing list order changed which retained family worked better, but not by
enough in both directions to meet the frozen order-effect rule. A container
keyed by controller family also failed to make both lessons reliable. The
frozen verdict is null.

The external family gate remained strong, making 63 of 64 actions. A-then-B
list order made 56, with a 32-to-24 family split. B-then-A order made 52, with a
20-to-32 split. The favored family therefore moved with table order, but the
A-then-B gap was 8 rather than the required 12.

The keyed object made 44 of 64 actions: 24 for family A and 20 for family B. It
did not approach the required 58 or the gated control.

## What was held fixed

This contact authored no new lesson. It loaded the eight exact model-written
tables from the preceding accumulation packet and verified the source packet
and specimen hashes before model contact.

Each retained lineage received fresh A and B devices above and below the current
position. The exact same table strings appeared in five conditions: empty,
A-then-B list, B-then-A list, object keyed by controller-family ID, and external
family gate. Every case received four identical calls.

## Results

| Container | All actions | Family A | Family B |
| --- | ---: | ---: | ---: |
| Empty | 32/64 | 16/32 | 16/32 |
| A then B list | 56/64 | 32/32 | 24/32 |
| B then A list | 52/64 | 20/32 | 32/32 |
| Keyed by controller family | 44/64 | 24/32 | 20/32 |
| External family gate | 63/64 | 32/32 | 31/32 |

Every four-call cell contained at least three valid action objects.

## What this supports

The result supports a narrow interface diagnosis. Ordered joint delivery is
order-sensitive, but the effect is not a simple deterministic first-entry rule.
The tested keyed object does not make the cold model perform the lookup
reliably. External exact-family selection remains much more dependable.

This creates a research boundary. Two lessons can coexist behind an external
gate, but that mechanism resembles key-based retrieval. The current evidence
does not show that the model can govern applicability among several retained
changes on its own. Running a larger validation of the same external lookup
would strengthen a substrate fact without resolving that distinction.

The next mechanism question should therefore concern applicability: what
information can let a retained change transfer beyond exact identity without
letting the harness silently choose the answer or causing the negative transfer
already observed under ungated delivery?

## Audit details

- Model: `ai/qwen3:14B-Q6_K`
- Model digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 320
- Physical attempts: 320
- Retries: 0
- Frozen specification SHA-256: `5420b143319389e057d96c044f97fe85092dbacf0fbd842b96e217428aedb02d`
- Specimen SHA-256: `f5fd8264604d47a8547adfa82df4e9f061f0e6fcaeee9f8da9869beba5400754`
- Packet SHA-256: `f06d55c7ddef488cf90bbfc10a5d81ba7439ec4f64c95fec9a5c3f17748a8b32`
- Frozen container verdict: `null`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The fresh devices and source
hashes are in [specimen.json](specimen.json). The exact provider identity is in
[provider.json](provider.json). Every raw request and response is under
`attempts/`.
