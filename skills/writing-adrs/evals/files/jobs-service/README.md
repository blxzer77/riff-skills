# jobs-service

Small TypeScript service that runs background jobs (image thumbnails, email sends)
for the photo-sharing app. Single instance on a 2 vCPU VM, Postgres 16 already used
for app data.

    npm run dev    # start
    npm test       # vitest
