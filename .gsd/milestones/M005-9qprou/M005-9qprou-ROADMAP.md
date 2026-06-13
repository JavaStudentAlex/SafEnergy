# M005-9qprou: Forecast and Market Credibility Layer

**Vision:** Replace frontend-visible mocked forecast and ERCOT-oriented market behavior with an honest physics-informed PV forecast and DE-LU market context that power the commitment workflow expected by the Lovable frontend.

## Success Criteria

- POST /forecast/predict and GET /forecast/{plant_id} return 15/30/45/60-minute PV generation forecasts grounded in plant capacity, weather, irradiance or proxy inputs, temperature, and optional recent generation.
- Forecast responses include expectation baseline, forecast delta, confidence or uncertainty, horizon-specific values, and explanation drivers rather than fixed mock-like outputs.
- GET /market/prices?zone=DE-LU returns EUR/MWh day-ahead, intraday, balancing-short, and balancing-long values with clear fixture or simulated-spread provenance.
- A plant to weather to forecast to market smoke path works deterministically for the frontend demo.

## Slices

- [x] **S01: Physics Informed PV Forecast** `risk:high` `depends:[]`
  > After this: After this, the frontend can request short-horizon PV forecasts that respond to plant capacity and weather instead of fixed mocks.

- [x] **S02: DE LU Market Price Service** `risk:medium` `depends:[]`
  > After this: After this, the frontend can show European market prices in EUR per MWh for commitment exposure decisions.

- [ ] **S03: Forecast Market Contract Smoke** `risk:medium` `depends:[S01,S02]`
  > After this: After this, one demo plant can flow through weather, forecast, and market endpoints with consistent ids and units.

## Boundary Map

| Boundary | In scope | Out of scope |
|---|---|---|
| PV forecast | Physics-informed nowcast, 15/30/45/60-minute horizons, uncertainty, explanations | Training a large ML model or claiming production-grade accuracy |
| Market | DE-LU fixture or live-adapter shape, EUR/MWh prices, simulated intraday and balancing spreads | Live trading execution or exchange integration |
| Existing routes | Preserve current trading routes as secondary compatibility surface | Rewriting the whole trading subsystem |
