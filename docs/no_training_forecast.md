# No-Training Forecast Method Stack

## Rationale

In the SafEnergy system, a deterministic **No-Training Forecast Method Stack** is used when reliable, pre-trained AI/ML models are either unavailable, untrustworthy, or missing required live data.

The rationale for using these deterministic baselines instead of defaulting to a newly trained (but poorly generalized) ML model is rooted in the project's commitment to:

1. **Honesty and Trust:** We avoid making false claims about AI or ML performance. Instead of quietly falling back to a fixed constant or a poor prediction from an unoptimized ML model, we explicitly declare the fallback method used.
2. **Explainability:** Deterministic methods like "Smart/Normalized Persistence", "pvlib Physical Solar", and "Wind Power-Curve Approximation" provide highly explainable and physically grounded signals.
3. **Reliability in Degraded Environments:** Live external API data (weather, irradiance, asset metadata) can be missing or stale. Deterministic fallbacks can gracefully degrade, adjusting their confidence and uncertainty metadata when fewer inputs are available.
4. **Safe Trading Behavior:** When the forecast confidence is low due to poor input data (e.g. falling back to the Regional Capacity Fallback), the generated trading signals adjust to become more conservative or return "no-action".

## Method Selection Fallback Hierarchy

The system attempts to pick the most accurate and descriptive deterministic method based on the available inputs:

1. **Smart/Normalized Persistence:** Requires recent generation plus irradiance or weather availability.
2. **pvlib Physical Solar:** Requires solar asset metadata (location, capacity, time) plus weather or irradiance.
3. **Wind Power-Curve Approximation:** Requires wind asset metadata plus wind forecast.
4. **Regional Capacity Fallback:** Requires installed capacity and regional weather only (lower confidence).
5. **Diagnostic Fallback:** Occurs when inputs are completely insufficient. Returns a labeled diagnostic fallback rather than an uninterpretable value.

By reading this documentation and reviewing the tests, contributors can understand how the pipeline preserves predictability, provenance, and safe behavior without relying on trained artifacts.
