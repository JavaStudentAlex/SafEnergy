# M007-19pj5r: Portfolio Health Dashboard Closure

**Vision:** Complete the backend/frontend alignment by serving plant health diagnostics, a portfolio dashboard overview, and an honest demo-ready product story while explicitly deferring satellite-derived cloud and irradiance enhancements until the core loop is working.

## Success Criteria

- GET /plant-health, GET /plant-health/{plant_id}, and anomaly-oriented health responses provide rule-based plant diagnostics for weather derating, underperformance, inverter outage, and string degradation scenarios.
- GET /dashboard/overview aggregates plants, weather, forecast, market exposure, commitment metrics, accepted actions, and health status into one frontend-safe portfolio response.
- The minimum credible frontend story is verified: plant map to weather to forecast to commitment gap to recommendation to accepted action to updated portfolio metrics.
- Demo-facing docs and response metadata use honest terms such as physics-informed PV forecast, weather-driven nowcast, fixture-backed market prices, simulated spread, and rule-based recommendation engine.
- Satellite-derived cloud or irradiance features are captured as deferred follow-up work and do not block completion of the core frontend alignment.

## Slices

- [x] **S01: Rule Based Plant Health** `risk:medium` `depends:[]`
  > After this: After this, the frontend Plant Health Monitor can show meaningful demo statuses and anomalies for each plant.

- [x] **S02: Dashboard Overview Aggregation** `risk:high` `depends:[S01]`
  > After this: After this, the frontend can load one portfolio overview endpoint for the dashboard while retaining detailed endpoint drill-downs.

- [x] **S03: Demo Closure and Honesty Guardrails** `risk:medium` `depends:[S01,S02]`
  > After this: After this, the complete frontend product story is verified and described honestly for hackathon demo use.

## Boundary Map

| Boundary | In scope | Out of scope |
|---|---|---|
| Plant health | Rule-based demo health, anomaly categories, clear diagnostics | Production SCADA integration or real inverter telemetry |
| Dashboard | Aggregated portfolio overview for frontend convenience | Replacing detailed endpoints or hiding upstream failures |
| Demo closure | End-to-end smoke, honest docs, deferred satellite scope | Live trading, physical dispatch, trained-model claims, satellite implementation |
