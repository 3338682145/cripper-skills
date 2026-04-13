# Cliper 中文说明

Cliper 是 Hermes 的摄取层仓库。它把外部来源声明成可运行的 source，把抓取结果落成可追溯的 Markdown 资产，并为后续 `llm-wiki`、topic dossier、output 层提供稳定的文件化 handoff。

如果你只想先看 30 秒版本，可以记住三句话：

- 这是什么：Hermes 的 `source intake + normalized asset` 层。
- 怎么用：注册一个 source，运行 `cliper ingest run`，检查 raw asset、HTML snapshot 和 run manifest。
- 为什么可信：Markdown-first、frontmatter contract、完整 provenance、去重、validation gates、file-only state。

## 项目简介

Cliper 解决的问题不是“直接写内容”，而是“把外部来源变成下游可以信任和复用的 source 资产”。

它适合这些场景：

- 你要把网页文档、后续的视频转写等来源接入 Hermes
- 你需要保留 provenance，而不是只留下一个摘要
- 你希望下游系统能追溯每条内容来自哪个 source、哪次抓取、哪个提取器版本
- 你要让多个 agent 在同一套 ingestion contract 上协作，而不是各自临时抓网页

和“直接让 agent 读 URL 然后写 wiki/写文案”的做法相比，Cliper 的特点是：

- 先固化 source，再进入知识编译或输出
- registry、raw asset、run manifest 都是 Markdown/JSON 文件，便于审计
- 所有输出都能回溯到 raw source，而不是只保留自由文本结果
- ingestion 和 knowledge linking / publishing 严格分层

## 功能特性

### 当前已实现

- Markdown source registry
- Markdown job registry
- `web_url` 输入
- URL 规范化与 canonical URL 去重
- HTML 抓取与正文抽取
- normalized Markdown raw asset 持久化
- source HTML snapshot 持久化
- run manifest 持久化
- raw asset 索引文件
- CLI 校验与统一 validation gates

### 已定义但未实现

- `topic-dossier` schema
  - `planned contract`
  - 当前只定义 contract，不提供 builder

### 当前明确未实现

- video/transcript adapter
- browser-driven ingestion
- `llm-wiki` runtime integration
- topic ledger writer
- brief / draft / 公众号文案生成
- publishing flow
- 数据库存储

## 快速开始

### 环境要求

- Python `>= 3.12`
- 推荐使用 `uv`

### 安装依赖

在仓库根目录执行：

```bash
uv sync
```

如果你只想直接跑命令，也可以用 `uv run ...`，不需要手动激活环境。

### 最小可运行示例

仓库里已经带了一个真实示例 source：Hermes Profiles 文档页。

直接运行：

```bash
uv run cliper registry validate --root .
uv run cliper ingest run --source hermes-docs-profiles --job hermes-docs-profiles-default --root .
uv run cliper validate all --root .
```

运行成功后，重点查看：

- `content/raw/.../*.md`
- `content/raw/.../*.source.html`
- `state/runs/run-*.json`
- `state/indexes/raw-assets.json`

## 使用说明

### 1. 手动运行一个已注册 source

```bash
uv run cliper registry validate --root .
uv run cliper ingest run --source <source_id> --job <job_id> --root .
uv run cliper validate all --root .
```

当前 CLI 入口有 3 个：

- `cliper registry validate`
- `cliper ingest run --source <source_id> [--job <job_id>]`
- `cliper validate all`

### 2. 新增一个 source

在 `content/registry/sources/` 新建一个 Markdown 文件，frontmatter 最少需要：

```md
---
schema: ingestion-source
schema_version: 1.0.0
source_id: my-doc-page
display_name: My Doc Page
status: active
source_kind: web_url
adapter: web_url
seed_urls:
  - https://example.com/docs/page
allowed_domains:
  - example.com
discovery_mode: seed_urls
default_topics:
  - my-topic
schedule:
  cadence: manual
  timezone: UTC
owner: hermes-core
validation_profile: strict
---

Why this source exists, trust caveats, and operating guidance.
```

### 3. 新增一个 job

在 `content/registry/jobs/` 新建一个 Markdown 文件：

```md
---
schema: ingestion-job
schema_version: 1.0.0
job_id: my-doc-page-default
source_id: my-doc-page
trigger: manual
cadence: on-demand
max_items: 1
fetch_budget: 1
retry_policy:
  max_attempts: 2
  backoff_seconds: 1
write_targets:
  - raw-assets
  - run-manifest
dossier_policy: contract-only
---

Default manual ingest job for this source.
```

### 4. 查看产物

一次成功的 ingest 之后，通常会看到这些文件：

- `content/raw/YYYY/MM/DD/<source-id>/<asset-id>.md`
  - normalized Markdown 正文
- `content/raw/YYYY/MM/DD/<source-id>/<asset-id>.source.html`
  - 原始 HTML snapshot
- `state/runs/run-<timestamp>.json`
  - 本次执行 manifest
- `state/indexes/raw-assets.json`
  - 派生索引

### 5. dedupe 与重跑

当前 dedupe 是基于 `canonical_url`。

这意味着：

- 同一 canonical URL 再跑一次，不会再写第二份 raw asset
- 系统会把它记入 `deduped_assets`
- 当前没有 `--refresh` / `--force-reingest` 语义

这属于当前实现限制，不建议靠手工绕过 dedupe 来构造“重抓覆盖”流程。

## 项目结构

```text
.planning/                  GSD 项目上下文、路线图、需求、状态
contracts/schemas/          frontmatter 和下游 handoff 的 canonical contracts
content/registry/sources/   source registry
content/registry/jobs/      ingest job registry
content/raw/                raw asset 与 source snapshot
docs/                       架构、校验、迁移文档
src/cliper/                 CLI、service、models、adapters
state/runs/                 ingest run manifests
state/indexes/              派生索引
llm-wiki/                   下游 knowledge linking 参考与 sibling skill
tests/                      contract tests 与 integration tests
```

### 各目录职责

- `.planning/`
  - 项目边界、phase、requirement、handoff 路线图
- `contracts/schemas/`
  - source/job/raw asset/topic dossier 的 contract 定义
- `content/registry/`
  - 人类可审计的 source 与 job 声明
- `content/raw/`
  - durable raw assets
- `state/`
  - file-only state model 的派生状态
- `llm-wiki/`
  - 下游如何把 raw source 编译成结构化 wiki 的参考实现

## 技术方案 / 原理说明

### 端到端数据流

当前的主流程是：

`source discovery -> registry validate -> fetch -> normalize -> raw asset -> run manifest -> validate -> human review -> downstream handoff`

### 当前实现原理

1. source 和 job 先通过 Markdown registry 声明
2. CLI 加载 registry，并校验 schema 与引用关系
3. `web_url` adapter 抓取页面
4. 抽取正文，生成 normalized Markdown
5. 计算 `canonical_url`、`content_hash`、`dedupe_key`
6. 写 raw asset Markdown
7. 写 HTML snapshot
8. 写 run manifest
9. 更新 raw asset index
10. 运行 validation gates

### file-only state model

当前仓库不使用数据库。

状态全部通过文件表达：

- source declaration：`content/registry/sources/*.md`
- job declaration：`content/registry/jobs/*.md`
- normalized source content：`content/raw/.../*.md`
- source snapshot：`content/raw/.../*.source.html`
- ingest execution state：`state/runs/run-*.json`
- 派生索引：`state/indexes/raw-assets.json`

这样做的好处是：

- 易于 diff、审计、备份
- agent 与人类都能直接检查 handoff
- schema 与文件结构天然绑定

### 为什么 source snapshot / provenance / dedupe 很重要

- `source snapshot`
  - 抽取结果有问题时，可以直接对照原 HTML 排查
- `provenance`
  - 下游知道是怎么抓的、抓的是哪个 URL、用的是哪个 extractor 版本
- `dedupe`
  - 避免同一 canonical URL 被重复写入，降低下游重复编译风险

## 配置与 frontmatter

### source frontmatter

source 至少需要这些字段：

- `source_id`
- `display_name`
- `source_kind`
- `adapter`
- `seed_urls`
- `allowed_domains`
- `discovery_mode`
- `default_topics`
- `schedule`
- `owner`
- `validation_profile`

其中：

- `default_topics`
  - routing hint，不应被误当成最终 topic ledger 写入
- `allowed_domains`
  - 强约束，`seed_urls` 必须在允许域名内

### job frontmatter

job 至少需要这些字段：

- `job_id`
- `source_id`
- `trigger`
- `cadence`
- `max_items`
- `fetch_budget`
- `retry_policy`
- `write_targets`
- `dossier_policy`

### raw asset frontmatter

当前 raw asset 是已经落地的核心输出 contract。

最小必需字段：

- `asset_id`
- `source_id`
- `run_id`
- `source_kind`
- `adapter`
- `canonical_url`
- `retrieved_at`
- `language`
- `content_hash`
- `dedupe_key`
- `status`
- `provenance`
- `refs`

正文 body 约束：

- 只允许 cleaned source Markdown
- 不允许混入 wiki linking、summary、publishing annotations

### 关于 source packet

`source packet` 是 **current assumption**，不是当前仓库已独立实现的 schema。

当前可以把下面这一组文件视为 source packet 等价物：

- `raw-asset.md`
- `.source.html`
- `run manifest ref`

### 关于 topic dossier

`topic dossier` 是 **planned contract**：

- schema 已定义
- builder 尚未实现
- output 层最终应消费 dossier，而不是 raw asset

### 关于 topic ledger

`topic ledger` 是 **planned downstream concept**：

- 当前仓库没有单独 schema
- 当前也没有 single-topic 强约束
- `default_topics` 只是 routing hint

## 配置与环境变量

### 当前基础运行所需配置

对于当前 `web_url` ingest 闭环，基本不需要 `.env`。

你至少需要：

- Python 3.12+
- `uv`
- 可访问目标 URL 的网络环境

### 当前必须填写的“配置”主要在 registry frontmatter，而不是环境变量

重点是：

- `seed_urls`
- `allowed_domains`
- `retry_policy`
- `schedule`
- `validation_profile`

### 安全注意事项

- 不要把未来 adapter 需要的 secrets 直接写进 registry Markdown
- 如果后续引入 video/transcript/provider tokens，应通过环境变量或外部 secret 管理
- raw asset 应保存 provenance，但不应泄露敏感 token

## How Output Aligns With Hermes / llm-wiki

### 这层在 Hermes 工作流里的位置

推荐放在整个工作流的最前面：

`source discovery -> cliper intake/fetch/normalize -> human review -> dossier / llm-wiki / output`

### 上下游边界

Cliper 只做：

- source intake
- fetch persistence
- normalized source markdown
- file-only traceability

Cliper 不做：

- wiki 编译
- brief / draft 生成
- topic dossier builder
- publishing

### 与 llm-wiki 的对齐方式

`llm-wiki` 的职责是把 raw sources 编译成结构化 topic wiki，并维护 cross-links、index、log。

因此 Cliper 的输出应该对齐成“结构化 source asset”，而不是直接生成散乱 wiki。

对 `llm-wiki` 来说，最关键的字段是：

- `canonical_url`
- `content_hash`
- `dedupe_key`
- `title`
- `published_at`
- `default_topics`
- `provenance.*`
- `refs.registry_source`
- `refs.run_manifest`
- `refs.source_snapshot`
- raw asset Markdown body

### 与 source packet / topic ledger / dossier 的关系

- `source packet`
  - `current assumption`
  - 当前等价于 `raw asset + snapshot + manifest`
- `topic ledger`
  - `planned downstream concept`
  - 当前不由 ingestion 写入
- `topic dossier`
  - `planned contract`
  - 未来应成为 output 层唯一批准的 publishing input

## 为什么可信

### 1. Markdown-first registry 与 asset

source、job、raw asset 都以文件形式落地，可审计、可 diff、可 review。

### 2. provenance + refs 完整链路

每个 raw asset 都应能回溯到：

- 谁声明了 source
- 哪个 job 跑的
- 哪次 run 产生的
- 原始 snapshot 是什么
- 使用了什么 extractor

### 3. run manifest + raw index 的 file-only state

你不需要猜系统内部状态。

当前状态都能直接在文件里看到：

- `state/runs/run-*.json`
- `state/indexes/raw-assets.json`

### 4. validation gates + migration governance

系统会拒绝：

- 缺 frontmatter 的 registry/raw asset
- 引用了不存在 source 的 job
- 缺少关键 provenance/ref 的 raw asset
- broken refs

contract 变更还需要 migration note，而不是偷偷改 schema。

## 常见问题 / 排错

### 1. registry validate 不通过

优先检查：

- frontmatter 是否完整
- `source_id` / `job_id` 是否重复
- job 是否引用了不存在的 `source_id`
- `seed_urls` 是否落在 `allowed_domains` 内

### 2. ingest run 成功了，但没有写新文件

先看 run manifest：

- 如果 `deduped_assets` 有记录，说明命中了 canonical URL 去重
- 当前这不是 bug，而是预期行为

### 3. 抽取结果噪声很多

优先对照：

- raw asset Markdown
- 同路径下的 `.source.html`

判断问题来自：

- 主内容区域选择不稳
- 页面结构变化
- Markdown 转换不够干净

### 4. validate all 失败

重点看：

- `refs.registry_source`
- `refs.run_manifest`
- `refs.source_snapshot`

这些引用只要有一个断掉，就会失败。

### 5. 我想重新抓同一个 URL，但现在不重写

这是 dedupe 的当前语义。

当前没有 `refresh` contract，如果确实要重新抓，应先明确为什么需要覆盖旧资产，再决定后续实现方式。

### 6. 视频/transcript 为什么不能直接加

因为当前 schema 只支持 `web_url`。

video/transcript 在产品方向上是合理的，但在当前仓库里仍属于 `planned contract`，不能伪装成已落地功能。

## 开发说明

### 本地开发

建议流程：

```bash
uv sync
uv run cliper registry validate --root .
uv run cliper ingest run --source hermes-docs-profiles --job hermes-docs-profiles-default --root .
uv run cliper validate all --root .
```

### 测试命令

```bash
uv run --with pytest python -m pytest tests
```

### 契约治理

当前 contract 主要在：

- `contracts/schemas/ingestion-source.schema.yaml`
- `contracts/schemas/ingestion-job.schema.yaml`
- `contracts/schemas/raw-asset.schema.yaml`
- `contracts/schemas/topic-dossier.schema.yaml`

### migration note 规则

只要 schema version 或 required field 语义发生变化，就必须补 migration note。

建议放在：

- `docs/migrations/`

### 开发时的分层纪律

改 ingestion 层时，避免把这些职责塞进来：

- wiki entity linking
- topic writing
- output drafting
- publishing

## 示例

### 示例 1：Hermes 文档 URL

source：

```md
---
schema: ingestion-source
schema_version: 1.0.0
source_id: hermes-docs-profiles
display_name: Hermes Docs Profiles Page
status: active
source_kind: web_url
adapter: web_url
seed_urls:
  - https://hermes-agent.nousresearch.com/docs/user-guide/profiles
allowed_domains:
  - hermes-agent.nousresearch.com
discovery_mode: seed_urls
default_topics:
  - hermes
  - user-guide
schedule:
  cadence: manual
  timezone: UTC
owner: hermes-core
validation_profile: strict
---
```

job：

```md
---
schema: ingestion-job
schema_version: 1.0.0
job_id: hermes-docs-profiles-default
source_id: hermes-docs-profiles
trigger: manual
cadence: on-demand
max_items: 1
fetch_budget: 1
retry_policy:
  max_attempts: 2
  backoff_seconds: 1
write_targets:
  - raw-assets
  - run-manifest
dossier_policy: contract-only
---
```

运行：

```bash
uv run cliper registry validate --root .
uv run cliper ingest run --source hermes-docs-profiles --job hermes-docs-profiles-default --root .
uv run cliper validate all --root .
```

### 示例 2：视频来源

下面这个例子是 **planned contract**，不是当前仓库可直接运行的配置：

```yaml
schema: ingestion-source
schema_version: 1.0.0
source_id: hermes-talk-video
display_name: Hermes Talk Video
status: active
source_kind: video_url
adapter: video_transcript
seed_urls:
  - https://www.youtube.com/watch?v=...
allowed_domains:
  - youtube.com
discovery_mode: seed_urls
default_topics:
  - hermes
schedule:
  cadence: manual
  timezone: UTC
owner: hermes-core
validation_profile: strict
```

如果未来支持视频，至少还需要明确：

- transcript 来源
- transcript 获取方式
- transcript 完整度
- transcript 的 provenance
- 是否需要 speaker / timestamp segmentation

## Non-goals / 当前 v1 不做什么

- 不做 topic dossier builder
- 不做 llm-wiki runtime integration
- 不做 publishing
- 不做 topic ledger writer
- 不做数据库化状态管理
- 不做 video/transcript implementation
- 不做自动公众号发布
- 不直接从 ingestion 层产出 brief / draft / final content

## Open Questions / 尚未钉死的问题

- 是否要单独引入 `source-packet.schema.yaml`
- `default_topics` 最终是 hint 还是更强的 routing contract
- single-topic ledger 应在哪一层强制
- human review 是否需要 machine-readable state
- `LOW_SIGNAL` 是否需要正式 status model
- refresh / reingest 语义如何定义
- video/transcript contract 具体如何建模
- output 层是否始终只消费 dossier，还是过渡期允许 source packet review

## 最小上手指南

### 我现在想抓一个 Hermes 文档 URL，应该怎么走

1. 在 `content/registry/sources/` 写一个 source 文件
2. 在 `content/registry/jobs/` 写一个 job 文件
3. 跑：
   - `uv run cliper registry validate --root .`
   - `uv run cliper ingest run --source <source_id> --job <job_id> --root .`
   - `uv run cliper validate all --root .`
4. 打开 raw asset、snapshot、run manifest 做人工检查

### 我想把这层接进 Hermes agent，应该放在哪

放在最前面的 source normalization 阶段：

`source discovery -> cliper intake/fetch/normalize -> human review -> llm-wiki / dossier / output`

### 我想让输出对齐 llm-wiki，最关键的字段和约束是什么

最关键的是：

- `canonical_url`
- `content_hash`
- `dedupe_key`
- `title`
- `published_at`
- `provenance.*`
- `refs.registry_source`
- `refs.run_manifest`
- `refs.source_snapshot`
- Markdown body only

最关键的约束是：

- body 只能是 normalized source content
- ingestion 不直接写 wiki
- 下游必须能回溯到 raw source
- output 不应直接绕过 dossier / downstream contract
