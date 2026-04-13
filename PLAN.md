# Hermes Source Intake Skill Plan

## 摘要

目标是设计一个 **Hermes optional skill**，让用户给 Hermes 一个 URL 后，系统可以自动完成：

1. 来源类型识别
2. 抓取 / 抽取 / 归一化
3. LLM 核验与质量分级
4. 双通道路由
   - 高置信度内容进入 `~/wiki/docs/raw/`
   - 低置信度、失败或特殊来源进入 review/staging

这不是 wiki 编译器，也不是 output 生成器。它只负责把外部来源变成 **可复用、可追溯、可核验的 source packet**，并与现有 `cliper -> llm-wiki` 边界保持一致。

### 已锁定决策

- 形态：做成 **Hermes optional skill**，不是 core tool
- 主干：以本地 Cliper intake 逻辑为主
- fallback：
  - 网页困难页 -> Firecrawl
  - PDF/复杂文档 -> MinerU
- 输出 gate：**双通道**
  - `AUTO_PASS` -> `~/wiki/docs/raw/`
  - `REVIEW_REQUIRED` / `LOW_SIGNAL` / `UNSUPPORTED` -> `~/.hermes/intake/review/`
- 自动化：既支持单 URL 交互，也支持 cron 批处理
- GitHub：v1 只留接口，不做完整 ingestion

## 1. 目标与成功标准

### 1.1 用户目标

用户希望持续沉淀高质量资料，而不是一次性总结。对 Hermes 来说，理想体验是：

- 给一个 URL
- Hermes 自动判断来源类型
- 自动选择抓取后端
- 生成规范 Markdown source packet
- 自动判断是否可以进入 `llm-wiki/raw`
- 不合格内容自动拦截到 review 区

### 1.2 成功标准

v1 完成后必须满足：

- 给一个 URL，Hermes 可调用该 skill 并产出 source packet
- 支持常见来源：
  - 博客 / 文章页
  - 文档页
  - 论文落地页 / PDF 链接
- 能在 native / Firecrawl / MinerU 之间自动选路
- 统一输出 Markdown packet
- 有 LLM verifier，输出：
  - `AUTO_PASS`
  - `REVIEW_REQUIRED`
  - `LOW_SIGNAL`
  - `UNSUPPORTED`
- `AUTO_PASS` 自动进入 `~/wiki/docs/raw/`
- 其他结果进入 review 区
- cron 与交互模式共用同一条处理链

## 2. skill 形态与包结构

### 2.1 为什么做 skill，不做 tool

v1 先做 skill，因为这个能力更像“编排 instructions + helper scripts + 外部 backend”，不需要先改 Hermes 核心。后续只有在这些条件成立时再升级为 tool：

- 需要系统级统一 auth
- 需要稳定的长任务管理
- 需要强二进制/上传下载控制
- 需要成为所有 agent 的共享基础设施

### 2.2 为什么放在 `optional-skills/`

因为依赖较重且可选：

- Firecrawl 需要 API key
- MinerU 可能需要本地 CLI / Docker / 服务
- 对所有 Hermes 用户并非默认刚需

默认目录：

```text
optional-skills/research/source-intake/
```

### 2.3 目录布局

```text
optional-skills/
  research/
    source-intake/
      SKILL.md
      scripts/
        intake_url.py
        classify_url.py
        run_native_backend.py
        run_firecrawl_backend.py
        run_mineru_backend.py
        normalize_packet.py
        verify_packet.py
        route_packet.py
        cron_drain_queue.py
      references/
        backend-matrix.md
        verifier-rubric.md
        packet-contract.md
        examples.md
```

### 2.4 各脚本职责

- `intake_url.py`
  - 总入口，负责完整编排
- `classify_url.py`
  - 来源分类
- `run_native_backend.py`
  - 调用本地 Cliper 抽取链路
- `run_firecrawl_backend.py`
  - Firecrawl fallback
- `run_mineru_backend.py`
  - MinerU fallback
- `normalize_packet.py`
  - 统一 source packet 格式
- `verify_packet.py`
  - LLM 质量核验
- `route_packet.py`
  - 写入 raw 或 review
- `cron_drain_queue.py`
  - cron 模式批处理队列

## 3. SKILL.md 规范设计

### 3.1 frontmatter

`SKILL.md` 应符合 Hermes creating-skills 规范，至少包含：

- `name`
- `description`
- `version`
- `author`
- `license`
- `metadata.hermes.tags`
- `metadata.hermes.config`
- `required_environment_variables`

### 3.2 建议配置项

```yaml
metadata:
  hermes:
    tags: [Research, Ingestion, Web, PDF, Wiki]
    related_skills: [wiki]
    config:
      - key: wiki.path
        description: llm-wiki 根目录
        default: "~/wiki"
      - key: source_intake.review_dir
        description: review/staging 目录
        default: "~/.hermes/intake/review"
      - key: source_intake.archive_dir
        description: 原始工件归档目录
        default: "~/.hermes/intake/archive"
      - key: source_intake.default_backend
        description: 默认 backend
        default: "native"
      - key: source_intake.github_mode
        description: GitHub URL 处理策略
        default: "placeholder"
```

### 3.3 环境变量

```yaml
required_environment_variables:
  - name: FIRECRAWL_API_KEY
    prompt: Firecrawl API key
    required_for: Firecrawl fallback backend
```

MinerU 默认不做强制 env，优先走本地 CLI 路径或本地服务配置。

## 4. 输入分类与 backend 选择

### 4.1 来源分类

v1 至少支持：

- `blog_article`
- `docs_page`
- `paper_page`
- `pdf_url`
- `github_repo`
- `unknown`

### 4.2 默认 backend 策略

- `blog_article` -> native
- `docs_page` -> native
- `paper_page` -> native 先抓 landing page
- `pdf_url` -> Firecrawl PDF 或 MinerU
- `github_repo` -> placeholder only

### 4.3 fallback 规则

1. 默认先试 native
2. 出现下列情况切 Firecrawl：
   - 主内容太短
   - heading 结构明显不完整
   - 噪声比例高
   - 页面显著依赖 JS
   - native 直接失败
3. 出现下列情况切 MinerU：
   - URL 指向 PDF
   - Firecrawl PDF 质量不足
   - 扫描件 / 复杂表格 / 多栏 / 公式-heavy
4. GitHub URL：
   - 只识别
   - 生成 placeholder packet
   - verdict 固定为 `UNSUPPORTED`

### 4.4 为什么不是“只用 Obsidian Clipper”

本方案吸收 Obsidian Clipper 的格式和人工 clipping 思路，但不把它当自动化主系统。v1 主系统仍是：

- 本地 Cliper intake 骨架
- Firecrawl / MinerU fallback
- LLM verifier
- review gate

后续如需人工 fallback，可单独补一个 “manual clip / obsidian-compatible review” 子流程。

## 5. source packet contract

### 5.1 contract 定位

当前 `cliper` 仓库已有 `raw-asset` 概念，但本 skill 的目标落点是 `llm-wiki/docs/raw/`。因此这里定义一个 **skill-level source packet contract**，同时尽量继承现有 raw-asset 的稳定字段。

### 5.2 packet 文件形态

写入 raw 或 review 的主文件名：

```text
<packet_id>--<slug>.md
```

frontmatter 建议：

```yaml
---
schema: source-packet
schema_version: 0.1.0
packet_id: <stable id>
source_type: <blog_article|docs_page|paper_page|pdf_url|github_repo|unknown>
input_url: <original input url>
canonical_url: <normalized canonical url>
title: <resolved title>
retrieved_at: <ISO8601 UTC>
published_at: <optional>
language: <optional>
backend_used: <native|firecrawl|mineru|github_placeholder>
backend_version: <string>
content_hash: <sha256 of normalized body>
dedupe_key: <sha256 of canonical_url>
signal_level: <high|medium|low>
verdict: <AUTO_PASS|REVIEW_REQUIRED|LOW_SIGNAL|UNSUPPORTED>
confidence: <0.00-1.00>
reason_codes:
  - <list of verifier reasons>
routing:
  suggested_topic: <string or null>
  suggested_kind: <docs|blog|paper|reference>
refs:
  artifact_dir: <archive dir>
  raw_html: <optional path>
  raw_pdf: <optional path>
  extracted_json: <optional path>
  verifier_report: <path>
  source_snapshot: <path>
---
<normalized markdown body only>
```

### 5.3 工件归档策略

为避免污染 `llm-wiki` 仓库，中间工件放到：

```text
~/.hermes/intake/archive/<packet_id>/
```

归档内容包括：

- 原始 HTML
- 原始 PDF
- Firecrawl JSON
- MinerU JSON / Markdown
- verifier report
- backend run log

`~/wiki/docs/raw/` 中只保留：

- Markdown 正文
- frontmatter
- refs

## 6. verifier 与双通道路由

### 6.1 verifier 目标

verifier 只做质量门禁，不做内容总结。它要判断：

- 抽取是否完整
- 噪声是否可接受
- 结构是否稳定
- 是否值得进入 `llm-wiki/raw`
- 是否应转 review

### 6.2 verifier 输出

```json
{
  "verdict": "AUTO_PASS|REVIEW_REQUIRED|LOW_SIGNAL|UNSUPPORTED",
  "confidence": 0.0,
  "signal_level": "high|medium|low",
  "reason_codes": ["..."],
  "summary": "short reviewer summary",
  "suggested_topic": "..."
}
```

### 6.3 判定规则

- `AUTO_PASS`
  - 正文完整
  - 噪声低
  - 结构清晰
  - 不是 placeholder
  - 具备 durable knowledge 价值
- `REVIEW_REQUIRED`
  - 内容基本可用，但抽取质量、结构、topic 判断不稳
- `LOW_SIGNAL`
  - 信息薄、模板噪声多、缺 durable value
- `UNSUPPORTED`
  - GitHub placeholder
  - 登录态 / 高交互 / backend 无法合理提取

### 6.4 路由规则

- `AUTO_PASS` -> `{{wiki.path}}/docs/raw/`
- `REVIEW_REQUIRED` -> `{{source_intake.review_dir}}/`
- `LOW_SIGNAL` -> `{{source_intake.review_dir}}/`
- `UNSUPPORTED` -> `{{source_intake.review_dir}}/`

### 6.5 dedupe 规则

基于 `canonical_url` 去重。

- raw 区已有相同 `canonical_url` 时不重复写入
- review 区也要 dedupe
- cron 队列在处理前先去重

## 7. 与 llm-wiki 的集成方式

### 7.1 上下游边界

该 skill 只负责把 source 送进 `llm-wiki` 的 raw inbox，不负责：

- 编译 topic article
- 更新 topic 索引
- cross-link
- build wiki
- 生成 brief / draft / output

这些继续留给 `llm-wiki` 或更下游的 dossier/output 流程。

### 7.2 llm-wiki 最小兼容要求

写入 `docs/raw/` 的 packet note 必须满足：

- Markdown 正文可直接读取
- frontmatter 提供 provenance
- 不依赖数据库才能理解
- 有稳定 dedupe / hash / refs 字段

### 7.3 topic 处理原则

v1 不做真正的 topic ledger。

只保留：

- `suggested_topic`
- `suggested_kind`

作为 routing hint。最终 topic 归属由 `llm-wiki` 或人工 review 决定。

## 8. cron 自动化设计

### 8.1 设计原则

cron 负责机械处理，LLM 负责核验与总结。不要让 cron 直接做自由发挥式内容生成。

### 8.2 队列文件

默认：

```text
~/.hermes/intake/queue.jsonl
```

每行示例：

```json
{"url":"https://example.com/post","source":"manual","added_at":"2026-04-13T00:00:00Z"}
```

### 8.3 cron 行为

`cron_drain_queue.py` 每次运行：

1. 读取队列
2. 跳过已处理或重复 URL
3. 对每条 URL 调用 `intake_url.py`
4. 输出结果摘要：
   - 进入 raw 的数量
   - 进入 review 的数量
   - 失败数量
   - 每条 URL 的 verdict

### 8.4 Hermes cron prompt 要求

cron prompt 必须自包含：

- 队列位置
- raw / review 路径
- verdict 定义
- `[SILENT]` 规则
- 只总结，不重写底层抓取逻辑

默认输出规则：

- 有新结果才汇报
- 无新结果输出 `[SILENT]`

## 9. 分阶段实施计划

### Phase 1: skill skeleton

交付：

- `optional-skills/research/source-intake/SKILL.md`
- `references/`
- scripts 占位入口
- config/env 定义

目标：

- Hermes 能识别该 skill
- 文档与配置完整

### Phase 2: native backend orchestration

交付：

- 单 URL intake 编排
- native backend 接入
- packet 输出
- raw/review 路由

目标：

- 博客 / 文档 URL 跑通闭环

### Phase 3: Firecrawl fallback

交付：

- Firecrawl fallback
- API key 接入
- backend 选择矩阵

目标：

- JS-heavy 页面和部分 PDF URL 有稳定 fallback

### Phase 4: MinerU PDF fallback

交付：

- MinerU 接入
- PDF artifact 管理
- 论文 / 复杂 PDF 路径打通

目标：

- 复杂 PDF、扫描件、表格-heavy 文档可进入 packet flow

### Phase 5: verifier + cron

交付：

- LLM verifier
- queue + cron drain
- 双通道自动路由

目标：

- 持续 intake 成为长期资料沉淀链路

### Phase 6: GitHub placeholder adapter

交付：

- GitHub URL 分类
- placeholder packet
- unsupported 路由

目标：

- 先留接口，不阻塞主链路

## 10. 测试计划

### 核心 happy path

- 博客 URL -> native -> `AUTO_PASS` -> 写入 `docs/raw/`
- 文档 URL -> native -> `AUTO_PASS` -> 写入 `docs/raw/`
- PDF URL -> MinerU -> `AUTO_PASS` 或 `REVIEW_REQUIRED`

### fallback

- native 提取过短 -> Firecrawl fallback
- Firecrawl PDF 质量不足 -> MinerU fallback

### verifier

- 噪声高 -> `REVIEW_REQUIRED`
- 内容极薄 -> `LOW_SIGNAL`
- GitHub URL -> `UNSUPPORTED`

### routing

- `AUTO_PASS` 只写 raw
- 其余 verdict 只写 review

### dedupe

- 相同 canonical URL 不重复写
- queue 中重复 URL 自动跳过

### cron

- queue 空时输出 `[SILENT]`
- queue 有混合结果时摘要正确

## 11. 风险与失败模式

### 抽取质量风险

- 主内容区域不稳定
- JS-heavy 页面正文不完整
- 代码块 / 表格 / 公式失真

应对：

- backend fallback
- verifier gate
- review 目录

### 外部依赖风险

- Firecrawl API 不可用
- MinerU 未安装
- 网络受限

应对：

- graceful degradation
- 明确 reason code
- 不允许 silent fail

### llm-wiki 污染风险

- 低质量内容直接进入 raw

应对：

- 双通道 gate
- verifier 必须给 verdict

### scope 漂移风险

- ingestion 变成 wiki compiler
- ingestion 开始写 brief / draft

应对：

- 在 `SKILL.md` 明确 Non-goals
- route 阶段禁止越层写入

## 12. Non-goals

v1 明确不做：

- 不写 wiki topic article
- 不更新 `docs/topics/*`
- 不跑 `llm-wiki` build
- 不生成 brief / draft / final post
- 不做真正的 GitHub repo 深度 ingestion
- 不做浏览器自动化后端
- 不做数据库状态管理

## 13. 默认假设

若实现时没有额外产品决策，默认采用：

- skill 路径：`optional-skills/research/source-intake/`
- `wiki.path` 默认 `~/wiki`
- `review_dir` 默认 `~/.hermes/intake/review`
- `archive_dir` 默认 `~/.hermes/intake/archive`
- 默认 backend 为 `native`
- Firecrawl 是 fallback，不是主后端
- MinerU 只用于 PDF / 复杂文档
- GitHub v1 仅做 placeholder adapter
- 只有 `AUTO_PASS` 才进入 `docs/raw/`
- cron 仅处理队列，不做全网发现

## 14. 交付物

实现阶段至少要产出：

- 一个符合 Hermes 规范的 optional skill 包
- 一套 helper scripts
- 一个稳定的 source packet contract
- 一套 verifier + routing 规则
- 一个 cron-friendly queue workflow

## 15. Autoplan Review Summary

### 15.1 Verdict

审核结论：**批准进入新 milestone 落地，但需要把当前四阶段 roadmap 视为历史基线，而不是继续当作活跃路线图。**

### 15.2 CEO Review

- 当前方案最强的一点，是它把目标锁在“durable source intake”而不是一次性总结，这和 Hermes 的核心方向一致。
- scope 需要继续收紧在 ingestion skill，不要把 `cliper` 本体推成 wiki compiler、topic builder 或 output generator。
- GitHub 维持 placeholder-only 是正确的 v1 边界，不能提前滑进 repo crawling。

### 15.3 Engineering Review

- 现有 `cliper` CLI、registry、dedupe、manifest、HTML snapshot 逻辑应保留，作为 `native backend` 复用，而不是平行重写。
- `source-packet` 应该是 additive contract，不应该直接推翻当前 raw-asset contract。迁移时要补 migration notes。
- Firecrawl 和 MinerU 只做 fallback backend，不做主流程默认值。
- raw/review 外部路径必须通过 skill config 注入，不能硬编码进 `cliper` core。

### 15.4 DX Review

- 脚本命名已经足够清晰，保留 `intake_url.py / classify_url.py / run_*_backend.py / verify_packet.py / cron_drain_queue.py` 这一套显式入口。
- verifier 输出必须稳定且可机读，避免 cron 或 review 结果出现自由发挥文本。
- Firecrawl 和 MinerU 需要在执行阶段显式声明 `user_setup`，否则 Windows 环境下的 phase execution 很容易卡死在外部依赖。

### 15.5 Review Outcome

- 采用 **新 milestone + 重置 phase 编号**。
- 跳过 design review，因为当前没有 UI 交付面。
- 保留 DX review，因为这是一条面向开发者的 CLI/skill 工作流。
- 后续 phase 2-5 在执行前增加外部 review gate。

### 15.6 Decision Audit Trail

| # | Decision | Classification | Rationale |
|---|----------|----------------|-----------|
| 1 | 用新 milestone 承接 source-intake，而不是继续复用旧 roadmap | architecture | 避免两条路线图描述两个不同产品 |
| 2 | 保留 `cliper` 作为 native backend | implementation | 当前 repo 已有可运行 extraction spine，不应重写 |
| 3 | `source-packet` 作为增量 contract | contract | 兼容当前 raw-asset，同时支持 richer routing/verifier metadata |
| 4 | Firecrawl / MinerU 都是 fallback，不是 primary backend | scope | 保持成本和复杂度受控 |
| 5 | 只有 `AUTO_PASS` 可进入 wiki raw | quality gate | 保护下游知识库不被低质量输入污染 |
| 6 | GitHub v1 只做 placeholder packet | scope | 防止 ingestion 范围过早扩大 |
