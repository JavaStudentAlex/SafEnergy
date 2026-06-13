# M004-njfgw0: Frontend Alignment Foundation

**Vision:** Create the stable solar-operations API foundation the Lovable frontend can depend on after the current forecast-method work: canonical utility-scale PV plant metadata, frontend-ready weather overlays, and documented response contracts with deterministic fixture-backed behavior for demos.

## Success Criteria

- GET /plants and GET /plants/{plant_id} expose stable demo PV plant metadata with plant id, name, location, timezone, capacity, operator-facing status, and any battery or commitment metadata needed by downstream flows.
- GET /weather/live and GET /weather/forecast return frontend-ready weather fields with explicit units, provenance, valid time, and 15/30/45/60-minute horizon support where applicable.
- The OpenAPI surface and tests make plant and weather contracts safe for frontend integration without requiring live external services.
- Missing plant ids, unavailable weather, and fixture fallback behavior are explicit in responses or errors rather than silent mocks.

## Slices

- [x] **S01: Plant Registry Contract** `risk:medium` `depends:[]`
  > After this: After this, the frontend can list demo plants and open a selected plant with stable metadata.

- [x] **S02: Weather Overlay Endpoints** `risk:medium` `depends:[S01]`
  > After this: After this, the frontend can render current weather and short-horizon weather overlays for a selected plant.

- [ ] **S03: Foundation Contract Verification** `risk:low` `depends:[S01,S02]`
  > After this: After this, a documented plant plus weather contract is ready for frontend wiring.

## Boundary Map

| Boundary | In scope | Out of scope |
|---|---|---|
| Plant registry | Demo PV plants, stable ids, location, capacity, timezone, status metadata | Full asset management or mutable admin CRUD |
| Weather | Open-Meteo adapter shape, fixture fallback, units, valid times | Paid weather providers or satellite-derived weather |
| Frontend contract | FastAPI schemas, API tests, docs for plants and weather | Frontend code changes |
