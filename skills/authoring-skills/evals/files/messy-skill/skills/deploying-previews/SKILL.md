---
name: deploy-preview
description: helps with deployments
allowed-tools: Bash(vercel:*) Bash(gh:*)
disable-model-invocation: true
when_to_use: when the user says "deploy preview" or "preview deploy" or "make a preview" or "staging link"
---

# Deploy Preview Skill

## What is a preview deployment?

A preview deployment is a temporary deployment of your application that lets you
see changes before they go to production. Preview deployments are very useful
because they allow reviewers to see changes in a real environment. Many platforms
like Vercel, Netlify, and Render support preview deployments. They are typically
created for each pull request.

## Instructions

You MUST ALWAYS run the tests first. NEVER skip the tests!!!

Use the Bash tool to run `npm test`. Then use the Bash tool to run `vercel deploy`.
Then use the AskUserQuestion tool to ask if they want to post the URL to the PR.
If yes, use `gh pr comment` to post it. You can use ${CLAUDE_PLUGIN_ROOT}/scripts/post.sh
for that too.

Options for deployment: you can use vercel, or netlify, or render, or fly.io, or
railway, or cloudflare pages. Pick whichever.

## Environment variables

Preview deployments need environment variables. Environment variables are
key-value pairs used to configure applications. Make sure the preview has the
right environment variables. Never use production secrets in previews.

## Troubleshooting

If the deploy fails, check the logs. If the build fails, check the build logs.
