# Configuration

SafEnergy reads local service access from a `.env` file during development.
Use [.env.example](../.env.example) as the committed template and copy it to
`.env` for local runs. The real `.env` file is ignored by Git.

Do not commit real credentials, service-account JSON files, access tokens, raw
satellite scenes, local caches, generated model binaries, database files, or
large market/generation extracts.

## Credential Tiers

The project should not require credentials for every task. Keep provider access
split into mandatory, recommended, and optional groups so deterministic tests,
fixtures, and local development still work when live services are unavailable.

| Tier | Provider | `.env` settings | Notes |
| --- | --- | --- | --- |
| Mandatory for live satellite MVP | One Sentinel access path | `EE_PROJECT` or Copernicus credentials or Sentinel Hub credentials | Use exactly one primary satellite path for the first MVP. |
| Recommended for MVP | Google Earth Engine | `EE_PROJECT`; optionally `GOOGLE_APPLICATION_CREDENTIALS` | Earth Engine auth is initialized with the Python client and a Google Cloud project. |
| Alternative satellite path | Copernicus Data Space direct download | `COPERNICUS_USERNAME`, `COPERNICUS_PASSWORD` | Generate/cache short-lived access tokens at runtime. Do not hardcode username/password or store bearer tokens permanently. |
| Alternative satellite path | Sentinel Hub Process API | `SENTINELHUB_CLIENT_ID`, `SENTINELHUB_CLIENT_SECRET` | Required only if the ingestion adapter uses Sentinel Hub APIs. |
| Optional satellite/weather path | EUMETSAT | `EUMETSAT_CONSUMER_KEY`, `EUMETSAT_CONSUMER_SECRET` | Reserved for a future EUMDAC-based adapter. |
| Recommended weather source | Open-Meteo | none | No `OPEN_METEO_API_KEY` is needed for the MVP usage. |
| Recommended solar modeling | pvlib | none | pvlib is a local Python library, not a credentialed service. |
| Optional market/generation data | ENTSO-E | `ENTSOE_API_TOKEN` | Only needed if an ENTSO-E adapter is implemented. |
| Optional market/generation data | EIA | `EIA_API_KEY` | Only needed if an EIA adapter is implemented. |
| Optional public data | SMARD, Energy-Charts, Ember, GDELT | none by default | Prefer cached downloads or fixture-backed adapters for demos. |

## Minimum MVP Setup

For the first satellite-driven forecast-to-trade slice, configure one of these
satellite paths:

1. Earth Engine, preferred:

   ```env
   EE_PROJECT=your-google-cloud-project
   ```

   For local user auth, run the Earth Engine Python authentication flow outside
   the repository, then initialize with the project name in code. For
   service-account/server usage, set:

   ```env
   GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
   ```

   The referenced JSON file must stay outside Git.

2. Copernicus Data Space direct download:

   ```env
   COPERNICUS_USERNAME=
   COPERNICUS_PASSWORD=
   ```

   Use these only to request a runtime access token. Cache token metadata under
   `SAFENERGY_CACHE_DIR` and avoid writing bearer tokens to committed files.

3. Sentinel Hub:

   ```env
   SENTINELHUB_CLIENT_ID=
   SENTINELHUB_CLIENT_SECRET=
   ```

   Use this path only if the ingestion adapter is based on Sentinel Hub rather
   than Earth Engine or direct Copernicus downloads.

Open-Meteo does not require a key, so do not add `OPEN_METEO_API_KEY` unless
the provider's terms or a future paid plan explicitly requires it.

## Cache and Fixture Paths

The hackathon demo should be able to run with pre-downloaded or fixture-backed
data because live APIs can rate-limit, fail, or require credentials at demo
time.

```env
SAFENERGY_DATA_DIR=data
SAFENERGY_CACHE_DIR=data/cache
SAFENERGY_FIXTURE_DATA_DIR=data/fixtures
```

Keep these directories ignored unless a small deterministic fixture is
explicitly added for tests.

## Provider Reference Links

- Google Earth Engine authentication:
  <https://developers.google.com/earth-engine/guides/auth>
- Copernicus Data Space OData product download authentication:
  <https://documentation.dataspace.copernicus.eu/APIs/OData.html>
- Sentinel Hub authentication:
  <https://docs.sentinel-hub.com/api/latest/api/overview/authentication/>
- Open-Meteo weather API:
  <https://open-meteo.com/en/docs>
- NASA POWER API:
  <https://power.larc.nasa.gov/docs/services/api/>
- EUMETSAT Data Access Client:
  <https://user.eumetsat.int/resources/user-guides/eumetsat-data-access-client-eumdac-guide>
- EIA API documentation:
  <https://www.eia.gov/opendata/documentation.php>
