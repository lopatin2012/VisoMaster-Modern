
# VisoMaster-Modern

> **VisoMaster-Modern** is a community fork of [VisoMaster](https://github.com/visomaster/VisoMaster),
> modernized for recent NVIDIA GPUs (CUDA 12.9/cu129, Blackwell `sm_120`) and up-to-date runtimes
> (torch 2.8, onnxruntime-gpu 1.23, TensorRT 10.13, PySide6 6.10 + qfluentwidgets).
> Licensed under **GPL-3.0** (see [LICENSE](LICENSE)); all original copyright belongs to the VisoMaster authors.
> Upstream project: https://github.com/visomaster/VisoMaster

---

### VisoMaster is a powerful yet easy-to-use tool for face swapping and editing in images and videos. It utilizes AI to produce natural-looking results with minimal effort, making it ideal for both casual users and professionals.  

---
<img src=".github/screenshot.png" height="auto"/>

## Features  

### 🔄 **Face Swap**  
- Supports multiple face swapper models  
- Compatible with DeepFaceLab trained models (DFM)  
- Advanced multi-face swapping with masking options for each facial part  
- Occlusion masking support (DFL XSeg Masking)  
- Works with all popular face detectors & landmark detectors  
- Expression Restorer: Transfers original expressions to the swapped face  
- Face Restoration: Supports all popular upscaling & enhancement models  

### 🎭 **Face Editor (LivePortrait Models)**  
- Manually adjust expressions and poses for different face parts  
- Fine-tune colors for Face, Hair, Eyebrows, and Lips using RGB adjustments  

### 🚀 **Other Powerful Features**  
- **Live Playback**: See processed video in real-time before saving  
- **Face Embeddings**: Use multiple source faces for better accuracy & similarity  
- **Live Swapping via Webcam**: Stream to virtual camera for Twitch, YouTube, Zoom, etc.  
- **User-Friendly Interface**: Intuitive and easy to use  
- **Video Markers**: Adjust settings per frame for precise results  
- **TensorRT Support**: Leverages supported GPUs for ultra-fast processing  
- **Many More Advanced Features** 🎉  

## Requirements

- Windows 10/11 (Linux also works), recent NVIDIA driver.
- **Python 3.11** — do *not* use 3.14 (no wheels for the pinned stack).
- This build targets modern GPUs (RTX 40/50 series, `sm_90`/`sm_120`). It does **not** ship the legacy
  CUDA 11.8/12.4 stacks.
- ~15 GB free disk for models and caches.

## Install (Windows, venv)

```sh
git clone https://github.com/lopatin2012/VisoMaster-Modern.git
cd VisoMaster-Modern
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements_cu129.txt
```

## Models and ffmpeg

1. Download the required models:
   ```sh
   .venv\Scripts\python.exe download_models.py
   ```
2. Download the binaries from the
   [visomaster-assets release](https://github.com/visomaster/visomaster-assets/releases/tag/v0.1.0_dp)
   and copy them into the `dependencies/` folder (do **not** download the “Source code” archives).
   A bundled `dependencies\ffmpeg.exe` is auto-detected, so no system-wide ffmpeg is required.

## Run

```sh
.venv\Scripts\python.exe main.py
```

or double-click **Start.bat** (it uses `.venv` when present). Optional diagnostics:

```sh
.venv\Scripts\python.exe main.py --profile   # prints per-stage timings to the console
```

## Optional: TensorRT

TensorRT is installed but the default provider is **CUDA**. In **Settings → Providers Priority** you can
select *TensorRT*; the first run builds engines into `tensorrt-engines/` (slow once, cached afterwards).
On the bundled models CUDA was just as fast in testing, so TensorRT is opt-in.

## Updating

```sh
scripts\update_cu129.bat
```
pulls the latest `main` (hard reset) and reinstalls the pinned dependencies.

## Troubleshooting

- CUDA-related issues: make sure the NVIDIA driver is up to date.
- Missing models: verify the files were placed in the correct `model_assets/` subfolders.
- Recording/export needs ffmpeg — the bundled `dependencies\ffmpeg.exe` is found automatically.

## [Join the upstream Discord](https://discord.gg/5rx4SQuDbp)

## Support the upstream project ##
VisoMaster was made possible by **[@argenspin](https://github.com/argenspin)** and **[@Alucard24](https://github.com/alucard24)** with the support of countless other members of the Discord community. If you wish to support the *upstream* project, you can donate to either of them (or both if you're double Awesome :smiley: )

### **argenspin** ###
- [BuyMeACoffee](https://buymeacoffee.com/argenspin)
- BTC: bc1qe8y7z0lkjsw6ssnlyzsncw0f4swjgh58j9vrqm84gw2nscgvvs5s4fts8g
- ETH: 0x967a442FBd13617DE8d5fDC75234b2052122156B
### **Alucard24** ###
- [BuyMeACoffee](https://buymeacoffee.com/alucard_24)
- [PayPal](https://www.paypal.com/donate/?business=XJX2E5ZTMZUSQ&no_recurring=0&item_name=Support+us+with+a+donation!&currency_code=EUR)
- BTC: 15ny8vV3ChYsEuDta6VG3aKdT6Ra7duRAc


## Disclaimer: ##
**VisoMaster** is a hobby project that we are making available to the community as a thank you to all of the contributors ahead of us.
We've copied the disclaimer from [Swap-Mukham](https://github.com/harisreedhar/Swap-Mukham) here since it is well-written and applies 100% to this repo.
 
We would like to emphasize that our swapping software is intended for responsible and ethical use only. We must stress that users are solely responsible for their actions when using our software.

Intended Usage: This software is designed to assist users in creating realistic and entertaining content, such as movies, visual effects, virtual reality experiences, and other creative applications. We encourage users to explore these possibilities within the boundaries of legality, ethical considerations, and respect for others' privacy.

Ethical Guidelines: Users are expected to adhere to a set of ethical guidelines when using our software. These guidelines include, but are not limited to:

Not creating or sharing content that could harm, defame, or harass individuals. Obtaining proper consent and permissions from individuals featured in the content before using their likeness. Avoiding the use of this technology for deceptive purposes, including misinformation or malicious intent. Respecting and abiding by applicable laws, regulations, and copyright restrictions.

Privacy and Consent: Users are responsible for ensuring that they have the necessary permissions and consents from individuals whose likeness they intend to use in their creations. We strongly discourage the creation of content without explicit consent, particularly if it involves non-consensual or private content. It is essential to respect the privacy and dignity of all individuals involved.

Legal Considerations: Users must understand and comply with all relevant local, regional, and international laws pertaining to this technology. This includes laws related to privacy, defamation, intellectual property rights, and other relevant legislation. Users should consult legal professionals if they have any doubts regarding the legal implications of their creations.

Liability and Responsibility: We, as the creators and providers of the deep fake software, cannot be held responsible for the actions or consequences resulting from the usage of our software. Users assume full liability and responsibility for any misuse, unintended effects, or abusive behavior associated with the content they create.

By using this software, users acknowledge that they have read, understood, and agreed to abide by the above guidelines and disclaimers. We strongly encourage users to approach this technology with caution, integrity, and respect for the well-being and rights of others.

Remember, technology should be used to empower and inspire, not to harm or deceive. Let's strive to be ethical and responsible use of deep fake technology for the betterment of society.
