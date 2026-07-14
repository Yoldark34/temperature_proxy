# HACS Default Repository Submission Checklist

Tracking status against the [HACS "Include" requirements](https://www.hacs.xyz/docs/publish/include/)
and [Integration-specific requirements](https://www.hacs.xyz/docs/publish/integration/)
for submitting this repo to `hacs/default`.

## General requirements

- [x] Repository is public and hosted on GitHub
- [x] Repository is installable as a HACS custom repository already
- [x] Repository is not archived
- [x] `hacs.json` exists with at least a `name` field
- [x] At least one GitHub **Release** exists (not just a tag) — `v1.0.0`
- [ ] `HACS Action` (`.github/workflows/hacs.yml`) passes with zero errors/ignores — added, needs a green run on GitHub before submitting
- [ ] `Hassfest` (`.github/workflows/hassfest.yml`) passes — added, needs a green run on GitHub before submitting
- [ ] PR to `hacs/default` opened from a personal (non-org) account, on a branch off `master`, with the entry inserted alphabetically

## Integration-specific requirements

- [x] Exactly one integration directory: `custom_components/temperature_proxy/`
- [x] All required files live inside that directory
- [x] `manifest.json` defines `domain`, `documentation`, `issue_tracker`, `codeowners`, `name`, `version`
- [ ] Brand assets: a `brand/` directory in the repo root with at least an `icon.png` (also can be submitted to [home-assistant/brands](https://github.com/home-assistant/brands)) — **not yet added, needs real artwork**

## Manual steps still needed (not automatable from here)

1. Supply an `icon.png` (and ideally `logo.png`) brand image and commit it under `brand/`.
2. Push to `main`, confirm both workflows (`HACS Validation`, `Hassfest Validation`) show green on GitHub.
3. Fork [`hacs/default`](https://github.com/hacs/default), add `Yoldark34/temperature_proxy` to the `integration` list in alphabetical order, and open a PR from your fork (not an org account).
