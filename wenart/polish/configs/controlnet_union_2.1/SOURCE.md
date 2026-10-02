# ControlNet Union 2.1 config (vendored)

`config.json` in this folder is a byte-identical copy of the diffusers config of the Z-Image-Turbo Fun
ControlNet Union 2.1 (docs/milestone5.md §1.6).

| Field | Value |
|---|---|
| Source repo | `hlky/Z-Image-Turbo-Fun-Controlnet-Union-2.1` |
| Revision | `5d85f6a430fd40300f931bd1291e0c4982094859` |
| URL | https://huggingface.co/hlky/Z-Image-Turbo-Fun-Controlnet-Union-2.1/raw/5d85f6a430fd40300f931bd1291e0c4982094859/config.json |
| Size | 591 bytes |
| sha256 | `f7225591bd7534c4ef9b9844c93a4d843813d55cd1f542b571af835cc70acba9` |
| git blob id (HF API) | `391e3f0ea3fa4ac55d0472997d247a93e5567740` |
| Fetched | 2 Oct 2026 |

Why vendored:
- The weights come from `alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1` (Apache-2.0), file
  `Z-Image-Turbo-Fun-Controlnet-Union-2.1-2602-8steps.safetensors`, in VideoX-Fun single-file format.
  diffusers 0.40.0 (`ZImageControlNetModel.from_single_file`) builds the model config either by guessing
  it from the weight keys and downloading the config from the hlky repo, or from a local `config=` folder.
- The hlky repo is a personal repo without a licence. The file holds only architecture metadata (layer
  counts and places, sizes), so it is copied here and passed as a local `config=` instead of downloading
  from that repo at run time (pinned, offline with `HF_HUB_OFFLINE=1`, nothing guessed).
- The loader passes `config=` = this folder (`polish.yaml: models.controlnet.config_dir`, relative to
  `wenart/polish`). `tests/test_m5_config.py` checks the sha256 above.
