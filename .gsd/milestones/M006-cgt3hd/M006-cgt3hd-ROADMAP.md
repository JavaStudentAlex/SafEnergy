# M006-cgt3hd: Commitment Action Loop

**Vision:** Implement the frontend’s central operator loop: compare forecasted generation against commitments, recommend a battery or market action, persist accepted actions, and update metrics in a transparent ledger-backed way.

## Success Criteria

- POST /commitment/recommend returns HOLD, DISCHARGE_BATTERY, DISCHARGE_AND_BUY, or BUY_MARKET recommendations based on forecast MWh, committed MWh, available battery energy, and DE-LU market prices.
- Recommendation responses include commitment gap, battery discharge MWh, market buy MWh, estimated cost, avoided imbalance cost, confidence, and an explanation suitable for frontend display.
- POST /commitment/actions/accept persists accepted actions in a simple local ledger with plant id, action type, timestamps, MWh quantities, and estimated cost.
- GET /commitment/actions and GET /commitment/metrics reflect accepted actions and update shortfall, cost, avoided-cost, and portfolio metrics.
- An end-to-end smoke test proves plants to weather to forecast to market to recommendation to accept action to metrics.

## Slices

- [x] **S01: Recommendation Engine** `risk:high` `depends:[]`
  > After this: After this, the frontend can request a commitment recommendation and display a clear action with explanation and cost impact.

- [x] **S02: Accepted Action Ledger** `risk:medium` `depends:[S01]`
  > After this: After this, the frontend can accept a recommendation and list accepted actions for a plant.

- [ ] **S03: Metrics and Commitment Smoke** `risk:medium` `depends:[S01,S02]`
  > After this: After this, accepting an action updates the metrics the frontend shows to operators.

## Boundary Map

| Boundary | In scope | Out of scope |
|---|---|---|
| Recommendation | Rule-based commitment gap, battery, and market recommendation | Automated live trading or real battery dispatch |
| Ledger | Simple local accepted-action storage for demo and metrics | Durable multi-user audit/compliance platform |
| Metrics | Accepted-action derived shortfall, estimated cost, avoided cost, portfolio totals | Financial settlement-grade accounting |
