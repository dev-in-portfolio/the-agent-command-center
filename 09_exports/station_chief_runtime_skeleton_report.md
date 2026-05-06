# Station Chief Runtime Skeleton

## Status
Station Chief Runtime upgraded to v4.0.0. Locked 175-family baseline preserved. First tiny real-world supervised execution candidate added.

## Runtime Capabilities
- live external action final preflight gate layer preserved as the prior boundary
- first tiny real-world supervised execution candidate schema
- first tiny real-world supervised execution candidate approval gate
- local proof artifact candidate contract
- explicit output directory boundary contract
- forbidden path contract
- local only execution envelope
- candidate pre-action audit proof
- local proof artifact execution record
- post-action verification record
- cleanup / rollback instruction record
- first tiny candidate ledger
- first tiny candidate readiness summary
- post-action verification and audit review bridge

## Required Validator
python3 scripts/validate_station_chief_runtime_v4_0.py

## Next Recommended Build Step
Next recommended build step: build post-action verification and audit review.

## v4.0 Doctrine
Station Chief Runtime v4.0.0 allows exactly one real-world action when separately approved: writing one local deterministic reversible proof artifact to an explicit operator-approved output directory. It does not authorize APIs, network, sockets, DNS resolution, outbound connections, credential use, secret reads, environment variable reads, deployment, production execution, production activation, live task assignment, live worker routing, live orchestration, worker process starts, or full workforce activation. v4.0 does not approve v4.1.
