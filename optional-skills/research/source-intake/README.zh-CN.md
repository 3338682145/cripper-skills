# Source Intake Skill 使用说明

`source-intake` 现在同时有两种形态：

- Hermes 可选技能，由 [`SKILL.md`](./SKILL.md) 描述
- 可打包的 Python 命令入口，安装后可以直接调用

运行链路保持不变：

`classify -> native/Firecrawl/MinerU -> normalize -> verify -> route`

## 打包后会得到什么

构建整个仓库包之后，可以直接使用这些命令：

- `source-intake`
- `source-intake-cron`
- `source-intake-wizard`
- `cliper source-intake run`
- `cliper source-intake cron`
- `cliper source-intake wizard`

Hermes 技能说明和参考文档仍然放在当前目录：

- [`SKILL.md`](./SKILL.md)
- [`references/backend-matrix.md`](./references/backend-matrix.md)
- [`references/packet-contract.md`](./references/packet-contract.md)
- [`references/verifier-rubric.md`](./references/verifier-rubric.md)
- [`references/examples.md`](./references/examples.md)

## 快速开始

在仓库根目录执行：

```bash
uv sync
uv run source-intake "https://example.com/post" \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive
```

队列批处理模式：

```bash
uv run source-intake-cron \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive
```

交互式填参向导：

```bash
uv run source-intake-wizard
uv run cliper source-intake wizard
```

通过主 CLI 的等价调用方式：

```bash
uv run cliper source-intake run "https://example.com/post" \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive

uv run cliper source-intake cron \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive
```

## 如何打包

在仓库根目录执行：

```bash
uv build
```

构建完成后，`dist/` 目录里会生成 `cliper` 的 wheel 和 sdist。安装 wheel 后，就可以在不依赖仓库命令路径的情况下直接调用：

```bash
pip install dist/cliper-*.whl
source-intake "https://example.com/post" \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive
```

## 直接调用时必须提供的参数

主入口至少需要这三个目录参数：

- `--raw-dir`
- `--review-dir`
- `--archive-dir`

可选参数包括：

- `--verdict`
- `--confidence`
- `--signal-level`
- `--reason-code`
- `--suggested-topic`
- `--suggested-kind`
- `--queue-path`，用于 cron 模式

向导会强制填写这些必填项：

- `run` 模式下的 `URL`
- `--raw-dir`
- `--review-dir`
- `--archive-dir`

其余选填项都可以直接回车留空，向导会自动忽略这些参数。

## 如何加载成 Codex skill

把整个技能目录复制到 Codex 本地 skills 目录：

```powershell
Copy-Item -Recurse -Force .\optional-skills\research\source-intake "$env:USERPROFILE\.codex\skills\source-intake"
```

复制后保持这个结构：

- `%USERPROFILE%\.codex\skills\source-intake\SKILL.md`
- `%USERPROFILE%\.codex\skills\source-intake\references\...`

这样 Codex 就可以把它识别成本地 skill。skill 负责说明和调用约定，打包出来的 CLI 负责真正执行命令，两者可以一起用。

## 外部依赖

以下依赖都是可选增强，不配置也能运行：

- `FIRECRAWL_API_KEY`，用于 Firecrawl fallback
- `MINERU_ENDPOINT`，用于 MinerU HTTP 或 CLI 模式
- `MINERU_BACKEND`，用于给 MinerU CLI 传递 backend 选择

如果 Firecrawl 或 MinerU 没有配置，系统会降级到 review-safe 路径，不会静默放行。

## README 中英文版应该怎么维护

建议把这套技能文档拆成两份并保持同步：

- 英文版：[`README.md`](./README.md)
- 中文版：[`README.zh-CN.md`](./README.zh-CN.md)

推荐规则：

- 两个版本的命令示例保持完全一致
- `source-packet`、`AUTO_PASS`、`UNSUPPORTED` 这类协议词不要翻译
- 只要 CLI 参数、打包方式、目录结构变了，中英文 README 一起改

## 边界说明

- `cliper` 仍然只负责 ingestion
- 这个技能可以把 packet 路由到 raw 或 review，但不会直接编译 wiki 页面
- GitHub URL 在 v1 仍然只是 placeholder
- 任何 contract 语义变更都要先补 migration notes
