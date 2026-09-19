# Integration benchmarks (future)

This directory is intentionally empty of benchmarks.

Connecting production WildfireGuardian repositories is **out of scope for now**
by explicit instruction. What follows is the specification of what should
eventually live here, recorded so that the shape of the integration is decided
before anybody is under pressure to ship it.

## How integration will work

Integration is file-based and one-way. A production repository writes one result
document per benchmark and this suite reads them:

```bash
# in the production repository
your-tool run-benchmarks --suite path/to/wildfireguardian-benchmarks --out results/

# in this repository, importing nothing from the production code
wg-benchmarks validate-results results/
```

A result document is named `WG-BM-0NN.yaml` (or `.yml` / `.json`) and holds
either the result mapping itself or a mapping with a `results` key. Only the
keys a benchmark pins down are compared, so an implementation may emit whatever
additional detail it likes.

## Benchmarks that belong here eventually

These require a production component to exist and therefore cannot be authored
in this repository today. Each is listed with the property it would establish.

| Planned id | Scenario | Property established |
|---|---|---|
| `WG-BM-1xx` | End-to-end: terrain raster in, dispatch schedule out, on a 5-node network with an analytic hazard field | that the *composition* of correct components is still correct — unit conventions survive the interfaces |
| `WG-BM-1xx` | The same scenario run twice from the same inputs | bitwise determinism, or a documented and bounded non-determinism |
| `WG-BM-1xx` | The same scenario with the coordinate reference system changed | no silent projection error; distances and slopes unchanged |
| `WG-BM-1xx` | Observation feed replayed in real time versus loaded from an archive | the deployment path and the evaluation path see the same information at the same times (the deployment-side version of WG-BM-014) |
| `WG-BM-1xx` | A component fed an input outside its declared domain | explicit refusal rather than extrapolation |
| `WG-BM-1xx` | Scale: the WG-BM-026 structure embedded in a 5,000-node network | the non-monotone feasible set is still reported, i.e. the scalar summary was not reintroduced as a performance optimisation |
| `WG-BM-1xx` | Timing: the full pipeline against a declared decision deadline | the system's own latency does not make its output late, which is WG-BM-030 applied to the tool itself |

## Rules these will follow

1. **They are not a substitute for the unit benchmarks.** An integration test
   that passes while a unit benchmark fails means the integration test is not
   exercising the failing path.
2. **Their expected answers are still derived, not recorded.** The scale
   benchmark embeds a structure whose answer is known analytically; it does not
   compare against a previous run.
3. **A recorded-output regression test is a different thing** and belongs in the
   production repository, not here. This repository never records output as
   truth (see `docs/DECISIONS.md`, WG-D-002).
