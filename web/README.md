# Awesome OpenClaw Skills — Web App

Browse, search, chat about, and use OpenClaw skills.

## Setup

1. Build the skills index (from project root):

   ```bash
   skill-sync
   skill-audit examples/skills/ --format json -o skills_index/audit.json
   # Then run the ranking/registry generation (see project README)
   ```

2. Install and run:

   ```bash
   cd web && npm install && npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000)

## Features

- **Browse**: List skills with grade, tier, install command
- **Search**: Filter by name/description
- **Chat**: Ask for skill suggestions (requires `OPENAI_API_KEY` for full chat)
- **Rate**: Star skills (stored in component state for now)
- **Use**: Copy install command

## Environment

- `OPENAI_API_KEY`: Optional. Enables AI chat for skill suggestions.
