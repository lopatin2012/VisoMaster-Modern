# VisoMaster-Modern

[English](README.md) | [Русский](README.ru.md) | **中文**

> **VisoMaster-Modern** 是 [VisoMaster](https://github.com/visomaster/VisoMaster) 的社区分支，
> 针对现代 NVIDIA 显卡（CUDA 12.9/cu129、Blackwell `sm_120`）和较新的运行时
> （torch 2.8、onnxruntime-gpu 1.23、TensorRT 10.13、PySide6 6.10 + qfluentwidgets）进行了现代化改造。
> 许可证：**GPL-3.0**（见 [LICENSE](LICENSE)）；原始版权归 VisoMaster 作者所有。
> 上游项目：https://github.com/visomaster/VisoMaster

---

### VisoMaster 是一款强大且易用的 AI 人脸替换与编辑工具，适用于图片和视频。它利用 AI 以极少的操作获得自然的效果，适合普通用户和专业人士。

---
<img src=".github/screenshot.png" height="auto"/>

## 功能

### 🔄 **换脸**
- 支持多种换脸模型
- 兼容 DeepFaceLab 训练的模型（DFM）
- 多人脸换脸，支持按面部部件遮罩
- 遮挡遮罩（DFL XSeg Masking）
- 支持常见的人脸检测器与关键点检测器
- 表情恢复：将原始表情迁移到换脸结果
- 人脸修复：支持常见的放大与增强模型

### 🎭 **人脸编辑器（LivePortrait 模型）**
- 手动调整各面部部件的表情与姿势
- 通过 RGB 微调面部、头发、眉毛和嘴唇的颜色

### 🚀 **其他功能**
- **实时预览**：保存前即可查看处理效果
- **人脸特征（Embeddings）**：使用多张源人脸提升精度与相似度
- **摄像头实时换脸**：输出到虚拟摄像头，用于 Twitch、YouTube、Zoom 等
- **友好的界面**，支持中文
- **视频标记**：为特定帧单独设置参数
- **TensorRT 支持**
- **以及更多功能** 🎉

## 要求

- Windows 10/11（Linux 也可），较新的 NVIDIA 驱动。
- **Python 3.11** —— 请勿使用 3.14（固定版本的依赖没有对应的 wheel）。
- 面向现代 GPU（RTX 40/50 系列，`sm_90`/`sm_120`）。不提供旧的 CUDA 11.8/12.4 版本。
- 约 15 GB 磁盘空间用于模型和缓存。

## 安装（Windows，venv）

```sh
git clone https://github.com/lopatin2012/VisoMaster-Modern.git
cd VisoMaster-Modern
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements_cu129.txt
```

或运行**自动安装程序**（检查/安装 Python 3.11，创建 `.venv`，安装依赖，下载模型和 ffmpeg）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```
也可以直接双击 **install.bat**。

## 模型与 ffmpeg

1. 下载所需模型：
   ```sh
   .venv\Scripts\python.exe download_models.py
   ```
2. 从 [visomaster-assets 发布页](https://github.com/visomaster/visomaster-assets/releases/tag/v0.1.0_dp)
   下载二进制文件并复制到 `dependencies/` 目录（**不要**下载 “Source code” 压缩包）。
   内置的 `dependencies\ffmpeg.exe` 会被自动识别，无需单独安装 ffmpeg。

## 运行

```sh
.venv\Scripts\python.exe main.py
```

或双击 **Start.bat**（存在 `.venv` 时优先使用）。诊断：

```sh
.venv\Scripts\python.exe main.py --profile   # 在控制台输出各阶段耗时
```

## 界面语言

在 **设置 → 语言** 中切换（`English` / `Русский` / `中文`）。切换立即生效，无需重启，并会保存。

## 可选：TensorRT

TensorRT 已安装，但默认使用 **CUDA** 执行提供程序。可在 **设置 → 执行提供程序优先级** 中选择 *TensorRT*；
首次运行会在 `tensorrt-engines/` 中构建引擎（较慢，之后使用缓存）。在随附模型上 CUDA 速度相当，因此 TensorRT 为可选项。

## 更新

```sh
scripts\update_cu129.bat
```
会拉取最新的 `main`（hard reset）并重新安装依赖。

## 疑难解答

- CUDA 相关问题：请更新 NVIDIA 驱动。
- 缺少模型：确认文件已放入 `model_assets/` 下正确的子目录。
- 录制/导出需要 ffmpeg —— 内置的 `dependencies\ffmpeg.exe` 会自动找到。

## [加入上游 Discord](https://discord.gg/5rx4SQuDbp)

## 支持上游项目
VisoMaster 由 **[@argenspin](https://github.com/argenspin)** 和 **[@Alucard24](https://github.com/alucard24)** 以及 Discord 社区众多成员共同完成。如果你想支持*上游*项目，可以向他们中的任意一位（或两位 :smiley: ）捐赠。

### **argenspin**
- [BuyMeACoffee](https://buymeacoffee.com/argenspin)
- BTC: bc1qe8y7z0lkjsw6ssnlyzsncw0f4swjgh58j9vrqm84gw2nscgvvs5s4fts8g
- ETH: 0x967a442FBd13617DE8d5fDC75234b2052122156B
### **Alucard24**
- [BuyMeACoffee](https://buymeacoffee.com/alucard_24)
- [PayPal](https://www.paypal.com/donate/?business=XJX2E5ZTMZUSQ&no_recurring=0&item_name=Support+us+with+a+donation!&currency_code=EUR)
- BTC: 15ny8vV3ChYsEuDta6VG3aKdT6Ra7duRAc


## 免责声明
**VisoMaster** 是一个业余项目，我们将其提供给社区，以感谢所有先行贡献者。
本免责声明借用自 [Swap-Mukham](https://github.com/harisreedhar/Swap-Mukham)，因为其内容完善且完全适用于本仓库。

我们强调，本换脸软件仅供负责任且合乎道德的使用。用户须对自己的行为承担全部责任。

用途：本软件用于创作逼真且具有娱乐性的内容，例如电影、视觉特效、虚拟现实等创意应用。我们鼓励在合法、合乎道德并尊重他人隐私的范围内使用。

道德准则：不得创建或传播可能伤害、诽谤或骚扰他人的内容；使用他人肖像前须获得同意与授权；不得将本技术用于欺骗、虚假信息或恶意目的；遵守适用的法律、法规和版权限制。

隐私与同意：用户须确保已获得所使用肖像者的必要许可与同意。我们坚决反对在未经明确同意的情况下创建内容，尤其是非自愿或私密内容。请尊重所有相关人员的隐私与尊严。

法律注意事项：用户须了解并遵守所有相关的本地、区域和国际法律，包括隐私、诽谤、知识产权等相关法律。如有疑问，请咨询法律专业人士。

责任：作为 deepfake 软件的创作者与提供者，我们不对使用本软件所产生的行为与后果负责。用户对使用及其可能的滥用承担全部责任。

使用本软件即表示你已阅读、理解并同意上述准则与免责声明。我们强烈建议谨慎、诚信并尊重他人权利地使用本技术。

请记住：技术应当用于赋能与启发，而非伤害与欺骗。让我们以合乎道德且负责任的方式使用 deepfake 技术。
