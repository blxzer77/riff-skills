# api-server

Express API for the recipes app. Sessions are stored in memory (express-session's
default MemoryStore); we run two instances behind a load balancer.

    npm run dev
