# superclaw-ctl User Guide

`superclaw-ctl` is a CLI tool for managing the SuperClaw vLLM model-serving stack. It handles first-time setup, Docker Compose lifecycle (start/stop/restart), health monitoring, model management, and API key rotation.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Linux x86_64 | Must run on the server host |
| Docker Engine (with Compose plugin) | `docker compose` (v2) must work |
| Intel GPU (Arc) | Tested on Intel® Arc B70 Pro |
| Internet access (first run only) | To pull the vLLM Docker image and download models from Hugging Face |

> <h3>⚠️ Important!</h3>
> 
>For initial setup, proxy environment variables, including no_proxy must be set (if applicable). See more details in the [Proxy Configuration section](#proxy-configuration)
>
> If a proxy is required, Docker proxy settings must also be set: See instructions [here](https://docs.docker.com/engine/daemon/proxy/)

---

## Installation

Download the `superclaw-ctl` binary, and extract to your local bin

```bash
tar -xzf superclaw-ctl.tar.gz
chmod +x superclaw-ctl
sudo mv superclaw-ctl /usr/local/bin/
```

Verify it works:

```bash
superclaw-ctl --help
superclaw-ctl version
```

---

## Quick Start

```
superclaw-ctl init      # one-time setup
superclaw-ctl up        # start the vLLM stack
superclaw-ctl status    # confirm everything is healthy
superclaw-ctl down      # stop the stack
```

---

## Commands

### `init` — First-time setup

Checks prerequisites, detects GPUs, pulls the vLLM Docker image, downloads default models, generates API keys, and writes config files.

```bash
superclaw-ctl init
```

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--models-dir PATH` | `~/.models` | Directory where models are stored |
| `--skip-models` | off | Skip model download (offline / pre-downloaded) |
| `-v` / `--verbose` | off | Enable debug output |

Config and secrets are written to `~/.config/superclaw-ctl/`.  
Compose templates are extracted to `~/.config/superclaw-ctl/compose/`.

> **Run `init` once.** Re-running it is safe but will regenerate API keys.

---

### `up` — Start the stack

Starts the vLLM container (chat + embedding backends + router) and waits until all services are healthy.

```bash
superclaw-ctl up
superclaw-ctl up --router-port 9090 --timeout 1800
```

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--router-port PORT` | `8080` | Port the vLLM router listens on |
| `--timeout SECONDS` | `1200` | How long to wait for backends to become healthy |
| `-v` / `--verbose` | off | Print retry attempts while waiting |

After startup succeeds, the tool prints connection info:

```
vLLM Model Router  →  http://<host-ip>:8080
vLLM Chat          →  http://127.0.0.1:18103
vLLM Embed         →  http://127.0.0.1:18104
API key            →  <redacted>
```

---

### `down` — Stop the stack

Stops and removes containers (models and config are untouched).

```bash
superclaw-ctl down
```

---

### `status` — Check container and health state

Shows container state, GPU utilisation (via `xpu-smi`), and live health probes for the chat backend, embed backend, and router.

```bash
superclaw-ctl status
superclaw-ctl status --router-port 9090   # if started on a non-default port
```

---

### `logs` — View container logs

```bash
superclaw-ctl logs              # last 200 lines
superclaw-ctl logs -f           # follow (live tail)
superclaw-ctl logs --tail 500   # last 500 lines
superclaw-ctl logs vllm -f      # explicit service + follow
```

---

### `doctor` — Run diagnostics

Checks Docker, Compose, the vLLM image, GPU access, the models directory, and secret quality — without changing anything.

```bash
superclaw-ctl doctor
```

---

## API Key Management

### Show keys (redacted)

```bash
superclaw-ctl keys show
superclaw-ctl keys show --reveal    # print full key values
```

### Rotate keys

Generates new keys, saves them, and reminds you to restart containers to apply them.

```bash
superclaw-ctl keys rotate
superclaw-ctl down && superclaw-ctl up   # apply the new key
```

---

## Configuration

Config is stored in `~/.config/superclaw-ctl/config.toml`.

### Show effective config

```bash
superclaw-ctl config show
```

### Update a config value

Use dot notation to address any key shown by `config show`.

```bash
superclaw-ctl config set paths.models_dir /data/models
superclaw-ctl config set images.vllm intel/llm-scaler-vllm:0.15.0
```

### Environment variable overrides

These env vars override the corresponding config values without modifying `config.toml`:

| Variable | Overrides |
|----------|-----------|
| `SUPERCLAW_MODELS_DIR` | `paths.models_dir` |
| `SUPERCLAW_VLLM_API_KEY` | `secrets.vllm_api_key` |

---

## Cleanup

```bash
# Preview what would be removed without touching anything
superclaw-ctl clean containers --dry-run
superclaw-ctl clean images --dry-run
superclaw-ctl clean config --dry-run
superclaw-ctl clean all --dry-run

# Run cleanup (prompts for confirmation unless --force is passed)
superclaw-ctl clean containers
superclaw-ctl clean images
superclaw-ctl clean config          # removes ~/.config/superclaw-ctl/
superclaw-ctl clean all             # containers + images + config
superclaw-ctl clean all --force     # no prompts
```

> **Note:** The models directory (`~/.models` by default) is **never** deleted by any clean command.

---

## Proxy Configuration

If your server is behind an HTTP proxy, set `HTTP_PROXY` / `HTTPS_PROXY` before running any command. The tool automatically passes these to Docker Compose.

Ensure `localhost` and `127.0.0.1` are in `NO_PROXY` so internal health probes are not routed through the proxy:

```bash
export NO_PROXY="$NO_PROXY,localhost,127.0.0.1"
```

`superclaw-ctl` will warn you if a proxy is active but the local bypass is missing.

### Docker

For Docker image pulls, if your server is being a proxy, these proxy settings must also be configured for Docker.

See [official Docker docs](https://docs.docker.com/engine/daemon/proxy/) for more information.

---

## Troubleshooting

| Symptom | Action |
|---------|--------|
| `Config file not found` | Run `superclaw-ctl init` first |
| Backends not healthy after `up` | Increase timeout: `superclaw-ctl up --timeout 1800` |
| Health probes failing with proxy | Add `localhost,127.0.0.1` to `NO_PROXY` |

Run `superclaw-ctl doctor` at any time to get a consolidated diagnostic report.
