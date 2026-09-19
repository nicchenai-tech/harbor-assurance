# Public deployment

## Safety boundary

Deploy only the repository's owned `demo-data`. The public image intentionally excludes organizer/customer data, ground truth, generator code and existing runtime databases. Public mode disables document uploads, rate-limits writes, resets on each process start and offers a manual sandbox reset. It is not a production authentication model.

## Portable container check

```sh
docker compose -f compose.demo.yml up --build
curl http://127.0.0.1:8080/api/health
```

Expected health fields: `status=ok`, seven emails, `mode=public synthetic sandbox`, `ocr_backend=tesseract`, and `uploads_enabled=false`.

## Render Blueprint

1. Publish this repository to GitHub/GitLab.
2. In Render, create a Blueprint from the repository's `render.yaml`.
3. Confirm region Singapore, Docker runtime and `/api/health` health check.
4. Open the generated HTTPS URL in an incognito window.
5. Test all four guided cases, a v1→v2 review, reset, mobile width and health endpoint.

The committed Blueprint selects a free preview instance to avoid an automatic purchase. Free services can sleep and lose ephemeral changes; that is acceptable because the sandbox reseeds itself, but the first judging request can be slow. Use a continuously running plan during judging only after the account owner approves any cost.

## Cloud Run alternative

The same Dockerfile can be built and deployed as a public Cloud Run service. Allow unauthenticated access, expose the platform `PORT`, set the four `HARBOR_*` environment variables from `render.yaml`, and use `/api/health` for startup/health checks. The filesystem is intentionally ephemeral.

## Judge-period check

- Public HTTPS URL opens without login.
- Seven synthetic emails load; no organizer identifiers appear.
- The scanned case reports the cloud OCR backend and remains human-gated.
- Upload is absent and the upload API returns 403.
- Reset restores report v1.
- Repository, slides, video and demo links work in a signed-out browser.
- Keep the service available through September26.
