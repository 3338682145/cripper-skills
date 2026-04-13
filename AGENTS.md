\# Hermes Project Rules



\## Goal

Build a durable multi-agent content operating system, not one-off summaries.



\## Core principles

\- Markdown-first

\- Preserve provenance for every asset

\- Prefer composable adapters over monolithic pipelines

\- Every output must be traceable back to raw sources

\- Do not redesign schemas without migration notes



\## Architecture boundaries

\- cliper handles ingestion only

\- llm-wiki handles knowledge linking

\- output layer consumes topic dossiers, not raw sources directly



\## Validation requirements

\- No raw asset without frontmatter

\- No wiki entity without source references

\- No topic dossier without readiness score

\- No publishing output without evidence links

