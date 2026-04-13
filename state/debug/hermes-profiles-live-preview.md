Run multiple independent Hermes agents on the same machine — each with its own config, API keys, memory, sessions, skills, and gateway.

## What are profiles?[​](#what-are-profiles "Direct link to What are profiles?")

A profile is a fully isolated Hermes environment. Each profile gets its own directory containing its own `config.yaml`, `.env`, `SOUL.md`, memories, sessions, skills, cron jobs, and state database. Profiles let you run separate agents for different purposes — a coding assistant, a personal bot, a research agent — without any cross-contamination.

When you create a profile, it automatically becomes its own command. Create a profile called `coder` and you immediately have `coder chat`, `coder setup`, `coder gateway start`, etc.

## Quick start[​](#quick-start "Direct link to Quick start")

```
hermes profile create coder       # creates profile + "coder" command aliascoder setup                       # configure API keys and modelcoder chat                        # start chatting
```

That's it. `coder` is now a fully independent agent. It has its own config, its own memory, its own everything.

## Creating a profile[​](#creating-a-profile "Direct link to Creating a profile")

### Blank profile[​](#blank-profile "Direct link to Blank profile")

```
hermes profile create mybot
```

Creates a fresh profile with bundled skills seeded. Run `mybot setup` to configure API keys, model, and gateway tokens.

### Clone config only (`--clone`)[​](#clone-config-only---clone "Direct link to clone-config-only---clone")

```
hermes profile create work --clone
```

Copies your current profile's `config.yaml`, `.env`, and `SOUL.md` into the new profile. Same API keys and model, but fresh sessions and memory. Edit `~/.hermes/profiles/work/.env` for different API keys, or `~/.hermes/profiles/work/SOUL.md` for a different personality.

### Clone everything (`--clone-all`)[​](#clone-everything---clone-all "Direct link to clone-everything---clone-all")

```
hermes profile create backup --clone-all
```

Copies **everything** — config, API keys, personality, all memories, full session history, skills, cron jobs, plugins. A complete snapshot. Useful for backups or forking an agent that already has context.

### Clone from a specific profile[​](#clone-from-a-specific-profile "Direct link to Clone from a specific profile")

```
hermes profile create work --clone --clone-from coder
```

Honcho memory + profiles

When Honcho is enabled, `--clone` automatically creates a dedicated AI peer for the new profile while sharing the same user workspace. Each profile builds its own observations and identity. See [Honcho -- Multi-agent / Profiles](/docs/user-guide/features/memory-providers#honcho) for details.

## Using profiles[​](#using-profiles "Direct link to Using profiles")

### Command aliases[​](#command-aliases "Direct link to Command aliases")

Every profile automatically gets a command alias at `~/.local/bin/<name>`:

```
coder chat                    # chat with the coder agentcoder setup                   # configure coder's settingscoder gateway start           # start coder's gatewaycoder doctor                  # check coder's healthcoder skills list             # list coder's skillscoder config set model.model anthropic/claude-sonnet-4
```

The alias works with every hermes subcommand — it's just `hermes -p <name>` under the hood.

### The `-p` flag[​](#the--p-flag "Direct link to the--p-flag")

You can also target a profile explicitly with any command:

```
hermes -p coder chathermes --profile=coder doctorhermes chat -p coder -q "hello"    # works in any position
```

### Sticky default (`hermes profile use`)[​](#sticky-default-hermes-profile-use "Direct link to sticky-default-hermes-profile-use")

```
hermes profile use coderhermes chat                   # now targets coderhermes tools                  # configures coder's toolshermes profile use default    # switch back
```

Sets a default so plain `hermes` commands target that profile. Like `kubectl config use-context`.

### Knowing where you are[​](#knowing-where-you-are "Direct link to Knowing where you are")

The CLI always shows which profile is active:

- **Prompt**: `coder ❯` instead of `❯`
- **Banner**: Shows `Profile: coder` on startup
- **`hermes profile`**: Shows current profile name, path, model, gateway status

## Running gateways[​](#running-gateways "Direct link to Running gateways")

Each profile runs its own gateway as a separate process with its own bot token:

```
coder gateway start           # starts coder's gatewayassistant gateway start       # starts assistant's gateway (separate process)
```

### Different bot tokens[​](#different-bot-tokens "Direct link to Different bot tokens")

Each profile has its own `.env` file. Configure a different Telegram/Discord/Slack bot token in each:

```
# Edit coder's tokensnano ~/.hermes/profiles/coder/.env# Edit assistant's tokensnano ~/.hermes/profiles/assistant/.env
```

### Safety: token locks[​](#safety-token-locks "Direct link to Safety: token locks")

If two profiles accidentally use the same bot token, the second gateway will be blocked with a clear error naming the conflicting profile. Supported for Telegram, Discord, Slack, WhatsApp, and Signal.

### Persistent services[​](#persistent-services "Direct link to Persistent services")

```
coder gateway install         # creates hermes-gateway-coder systemd/launchd serviceassistant gateway install     # creates hermes-gateway-assistant service
```

Each profile gets its own service name. They run independently.

## Configuring profiles[​](#configuring-profiles "Direct link to Configuring profiles")

Each profile has its own:

- **`config.yaml`** — model, provider, toolsets, all settings
- **`.env`** — API keys, bot tokens
- **`SOUL.md`** — personality and instructions

```
coder config set model.model anthropic/claude-sonnet-4echo "You are a focused coding assistant." > ~/.hermes/profiles/coder/SOUL.md
```

## Updating[​](#updating "Direct link to Updating")

`hermes update` pulls code once (shared) and syncs new bundled skills to **all** profiles automatically:

```
hermes update# → Code updated (12 commits)# → Skills synced: default (up to date), coder (+2 new), assistant (+2 new)
```

User-modified skills are never overwritten.

## Managing profiles[​](#managing-profiles "Direct link to Managing profiles")

```
hermes profile list           # show all profiles with statushermes profile show coder     # detailed info for one profilehermes profile rename coder dev-bot   # rename (updates alias + service)hermes profile export coder   # export to coder.tar.gzhermes profile import coder.tar.gz   # import from archive
```

## Deleting a profile[​](#deleting-a-profile "Direct link to Deleting a profile")

```
hermes profile delete coder
```

This stops the gateway, removes the systemd/launchd service, removes the command alias, and deletes all profile data. You'll be asked to type the profile name to confirm.

Use `--yes` to skip confirmation: `hermes profile delete coder --yes`

note

You cannot delete the default profile (`~/.hermes`). To remove everything, use `hermes uninstall`.

## Tab completion[​](#tab-completion "Direct link to Tab completion")

```
# Basheval "$(hermes completion bash)"# Zsheval "$(hermes completion zsh)"
```

Add the line to your `~/.bashrc` or `~/.zshrc` for persistent completion. Completes profile names after `-p`, profile subcommands, and top-level commands.

## How it works[​](#how-it-works "Direct link to How it works")

Profiles use the `HERMES_HOME` environment variable. When you run `coder chat`, the wrapper script sets `HERMES_HOME=~/.hermes/profiles/coder` before launching hermes. Since 119+ files in the codebase resolve paths via `get_hermes_home()`, everything automatically scopes to the profile's directory — config, sessions, memory, skills, state database, gateway PID, logs, and cron jobs.

The default profile is simply `~/.hermes` itself. No migration needed — existing installs work identically.