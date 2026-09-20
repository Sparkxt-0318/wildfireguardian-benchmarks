# WG-BM-050 (K7) — Information with no decision value

## Scenario

The WG-BM-049 decision (`p* = 0.2`) with a lower prior and a weaker observation.

```
prior: P(H_reaches) = 0.05
P(haze | reaches) = 0.6      P(haze | misses) = 0.3
```

Valley haze is **twice as likely** if the fire is going to reach the settlement.
It is a real signal.

## Derivation

```
prior action: E[stay] = 0.05 * 20 = 1.0  vs  E[evacuate] = 0.95 * 5 = 4.75   ->  stay

P(haze)    = 0.03 + 0.285 = 0.315     P(reaches | haze)    = 0.03/0.315 = 0.0952380952
P(no haze) = 0.02 + 0.665 = 0.685     P(reaches | no haze) = 0.02/0.685 = 0.0291970803
```

Both posteriors are **below `p* = 0.2`**, so the action is `stay` on both
branches:

```
expected loss after observing = 0.315 * 1.90476 + 0.685 * 0.58394 = 0.6 + 0.4 = 1.0
EVSI = 1.0 - 1.0 = 0        exactly
```

Meanwhile:

```
mutual information I(H;Z) = 0.0130871531 bits   >  0
EVPI                      = 1.0                    >  0
```

## Why this benchmark matters more than its size suggests

Three quantities are positive, zero and positive respectively, and they are
routinely treated as the same quantity:

| Quantity | Value | Means |
|---|---|---|
| mutual information | **0.0131 bits** | the observation tells you something |
| EVSI | **0** | it cannot change what you do |
| EVPI | **1.0** | knowing the truth *could* change what you do |

The governance consequence is direct. "We are uncertain, therefore we should
gather more information" is not valid. The correct question is whether the
information could move the belief **across a decision boundary**, and here it
provably cannot: the observation's strongest possible branch leaves the belief
at 0.095, less than half of `p*`.

Note the third row. The zero is a property of *this observation*, not of the
decision — perfect information would be worth 1.0. So the right conclusion is
not "stop looking" but "this particular sensor cannot settle it, and tasking it
is spending a pass for nothing".

The `choose_by_information_gain` mutation recommends acquisition on positive
entropy reduction; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| posterior after haze / no haze | 0.0952 / 0.0292 |
| action on both branches | `stay` |
| EVSI | **0** |
| mutual information | 0.013087 bits |
| EVPI | 1.0 |
