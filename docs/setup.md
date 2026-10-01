# Setup guide (do this once, step by step)

You are using Claude Code **in the cloud** (claude.ai/code), so steps are for the browser.
Never paste a key or token into the chat. You enter keys only in the places named below.

Status found on 1 Oct 2026: the environment already has a `RUNPOD_API_KEY` variable, but the
network policy blocks `api.runpod.io`, `huggingface.co` and other needed domains. Step 4 fixes that.

## Step 1 – Hugging Face read token

1. Open https://huggingface.co/settings/tokens (log in or create a free account).
2. Click **Create new token**. Token type: **Read**. Name: `wenart-runpod`. Click **Create token**.
3. Copy the token (starts with `hf_`). Keep it for Step 2.3. You will not see it again later.

Check: the token appears in the list with type "Read".
Note: none of the models in the plan are gated, so you do not need to accept any model licence on the website.

## Step 2 – RunPod account

2.1 Balance: open https://www.console.runpod.io/user/billing → **Add credits** → add a small amount
(for example $25) by card. Make sure **automatic top-up / auto-pay is OFF** while we test.
Check: the balance shows on the billing page.

2.2 API key: open https://www.console.runpod.io/user/settings → **API Keys** → **Create API Key**.
Name: `wenart-cloud`. Permission: **Restricted**, then give **Read/Write** to Pods, Storage/Network Volumes
and Templates, **Read Only** to everything else, and **None** to Serverless. Click **Create** and copy the key.
(If you already created the key that is in the environment, open it and check it has these permissions.)
Check: the key is in the list.

2.3 Secret: open https://www.console.runpod.io/user/secrets → **Create Secret**.
Name: `hf_token` (exactly), value: the Hugging Face token from Step 1. Save.
Check: `hf_token` is listed. Pods will receive it as `HF_TOKEN={{ RUNPOD_SECRET_hf_token }}`.

## Step 3 – (Mac only, skipped) 
Not needed now, because the sessions run in the cloud. When you later run sessions on your Mac,
ask Claude for this step (Homebrew, git, Python, SSH key, Keychain).

## Step 4 – Claude Code cloud environment settings

Open https://claude.ai/code. At the top of the prompt box there is the **environment selector**
(cloud icon). Hover over your environment and click the **settings (gear) icon** → the
"Update cloud environment" dialog opens.

4.1 **Network access**: select **Custom**. Tick **"Also include default list of common package managers"**.
In **Allowed domains** paste these lines (one per line):

```
api.runpod.io
rest.runpod.io
*.proxy.runpod.net
s3api-eu-ro-1.runpod.io
docs.runpod.io
huggingface.co
cdn-lfs.huggingface.co
download.blender.org
docs.blender.org
download.pytorch.org
api.polyhaven.com
polyhaven.com
dl.polyhaven.org
ambientcg.com
```

4.2 **RunPod key** – choose one:
- **Preferred (Pro/Max plans):** under **API credentials** click **Add**. Allowed websites: `api.runpod.io`
  and on a second line `rest.runpod.io`. Header: `Authorization`, prefix `Bearer`, value = your RunPod key.
  Click **Connect**. Then delete the `RUNPOD_API_KEY` line from **Environment variables**
  (the proxy adds the key for us; the variable is not needed and is visible to anyone using the environment).
- **Otherwise (Team/Enterprise, no API credentials):** keep `RUNPOD_API_KEY=<your key>` in **Environment variables**.

4.3 **Setup script** (optional, makes CPU tools available in every session; finishes in under 5 minutes):
paste the contents of `scripts/cloud-setup.sh` from this repo.

4.4 Click **Save changes**. Then **start a new session** (new settings apply only to new sessions) and tell
Claude: "Setup done, run the checks."

## Step 5 – What Claude will check in the new session (read-only)

- `GET https://api.runpod.io/v2/pods` → list of pods (expected: empty)
- `GET https://api.runpod.io/v2/network-volumes` → (expected: empty until Milestone 1)
- `GET https://api.runpod.io/v2/catalog/gpus?include=AVAILABILITY&product=POD&cloud=SECURE` → live prices
- `GET https://api.runpod.io/v2/account/secrets?name=hf_token` → the secret exists (value is never shown)
- `https://huggingface.co/api/models/Qwen/Qwen3-VL-8B-Instruct` → reachable

Checklist (Claude fills this in):

| Item | Ready? (checked 1 Oct 2026) |
|---|---|
| Hugging Face token created | yes (stored as RunPod secret `hf_token`; value never read) |
| RunPod balance added, auto-top-up off | not checkable by API; please confirm on the billing page |
| RunPod restricted API key | yes, key works for pods, volumes, secrets, catalog (read). Write scope is tested in Milestone 1 |
| RunPod secret `hf_token` | yes, exists (created 1 Oct 2026) |
| Cloud environment: Custom network list | yes, all domains reachable except `cdn-lfs.huggingface.co` (proxy answers 502; not needed, models download on the pod) |
| Cloud environment: RunPod key as API credential or variable | yes, as environment variable `RUNPOD_API_KEY` |
| Read-only API checks pass | yes, all 5 checks returned HTTP 200 |
