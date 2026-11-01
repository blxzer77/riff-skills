#!/usr/bin/env node
const [cmd, ...args] = process.argv.slice(2);
const flags = { "--json": "print JSON", "--api-url": "API base URL (default http://localhost:3000)" };
if (cmd === "export") console.log("exporting", args.join(" "));
else console.log("usage: readwell export <list> [--json] [--api-url URL]", flags);
