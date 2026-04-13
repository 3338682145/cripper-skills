# Hermes 使用手册解读（中文）

本文基于当前仓库中的 Hermes 官方文档整理，目标不是逐字翻译，而是回答 7 个更偏“怎么落地”的问题，并把“官方直接支持”和“工程化组合实践”分开讲清楚。

## 阅读范围

我重点阅读了这些文档类别：

- Getting Started：`installation.md`、`quickstart.md`
- User Guide：`configuration.md`、`features/tools.md`、`features/skills.md`、`features/delegation.md`、`features/cron.md`、`features/memory.md`、`features/memory-providers.md`、`features/mcp.md`、`features/browser.md`、`features/provider-routing.md`、`features/fallback-providers.md`、`features/code-execution.md`
- Guides：`delegation-patterns.md`、`automate-with-cron.md`、`work-with-skills.md`、`use-mcp-with-hermes.md`、`python-library.md`、`tips.md`
- Reference / Developer Guide：`toolsets-reference.md`、`tools-reference.md`、`cli-commands.md`、`creating-skills.md`、`adding-tools.md`

---

## 1. 安装好 Hermes 后，第一步应该怎么配置，才能让它开始稳定工作？

最短答案：先把 Hermes 从“能跑起来”变成“有稳定默认配置”。

### 推荐顺序

1. 先确认运行环境。
   - 如果你在 Windows 上，官方明确建议用 **WSL2**，不是原生 Windows。
   - 如果后面要用 `execute_code`，也优先放在 Linux / macOS / WSL2，因为该能力依赖 Unix domain socket。

2. 先跑一遍：

```bash
hermes setup
```

如果你不想全量向导，至少要跑：

```bash
hermes model
hermes tools
```

3. 把配置职责分清：
   - `~/.hermes/config.yaml`：模型、toolsets、terminal backend、compression、memory、delegation 等非敏感配置
   - `~/.hermes/.env`：API key、token、密码等敏感信息

4. 至少确定 4 件事：
   - 默认 `provider + model`
   - `terminal.backend`
   - 你要开放哪些 `toolsets`
   - `fallback_model` 是否配置

5. 最后做体检：

```bash
hermes doctor
hermes status
hermes config check
```

### 我建议的“稳定起步”基线

- 主模型先固定，不要一上来频繁切换，避免把会话和调试体验搞乱。
- `terminal.backend` 刚开始可以先用 `local` 验证，再切到 `docker` 或 `ssh`。
- 开启默认压缩，不要关掉 `compression`。
- 保留审批机制，`approvals.mode` 不建议一开始设成 `off`。
- 尽早放一个项目级 `AGENTS.md`，这样 Hermes 每次进项目都能拿到稳定上下文。

### 一句话建议

如果你只想尽快稳定开工，最实用的顺序是：

`hermes setup -> hermes model -> hermes tools -> hermes doctor -> 开始用`

---

## 2. Hermes 怎样配置 provider、toolsets、terminal backend，才能更适合长时间执行任务？

核心思路是三层分离：

- 主模型负责高质量推理
- 子 agent / 辅助任务走更便宜更快的模型
- 执行环境放到更稳定、更隔离的 backend

### 2.1 Provider 怎么配

#### 推荐结构

- 主 provider：选你最稳定、最熟悉的主力模型
- `fallback_model`：配一个不同故障域的备份 provider:model
- `delegation`：给子 agent 单独配一个更便宜/更快的模型
- `auxiliary.*` / `compression.*`：让视觉、网页提取、压缩这些边任务独立解析

#### 实战建议

- 如果你追求“通用稳定 + 路由灵活”，**OpenRouter** 很适合作主入口，因为有 provider routing。
- 如果你追求“直接接大模型原厂”，可以用 Anthropic、Copilot、Codex、Gemini、Kimi、GLM、MiniMax 等一方 provider。
- 如果你是自托管模型，务必显式确认 `context_length`，这在 Hermes 里非常关键。

#### 长任务的配置重点

- 配 `fallback_model`
- 保留 `compression.enabled: true`
- 如果你走 OpenRouter，可加 `provider_routing`
- 给 `delegation.model` 单独设快模型，降低大任务成本

### 2.2 Toolsets 怎么配

不要默认“全开就是最好”。长时间任务更适合“按任务最小授权”。

#### 常见组合

- 研发 / 调试：`terminal,file,web`
- 自动化采集：`web,file,terminal,code_execution,cronjob`
- 深度研究：`web,skills,delegation`
- 低风险只读：`safe` 或 `web,file`

#### 什么时候不要开太多

- 如果任务只是采集和整理，不一定要开 `browser`
- 如果任务不需要跨平台发消息，不一定要开 `send_message`
- 如果任务不需要并行推理，不一定要开 `delegation`

### 2.3 Terminal backend 怎么配

#### `local`

- 适合：刚开始、本机可信任务、快速调试
- 不适合：长期自动化、风险隔离要求高的场景

#### `docker`

- 适合：最常见的长任务方案
- 优点：隔离好、可复现、容易限制 CPU / 内存 / 磁盘、可持久化
- 建议：长任务优先选它

#### `ssh`

- 适合：远程专用执行机、把 Hermes 和工作机分离
- 优点：网络边界天然隔离，`persistent_shell` 默认就很适合长任务

#### `modal` / `daytona`

- 适合：云端执行、弹性资源、远程持续运行
- `daytona` 更像持久云工作区
- `modal` 更像云沙箱

#### `singularity`

- 适合：HPC / 共享服务器环境

### 2.4 一个适合长任务的配置模板

下面是“思路模板”，不是唯一答案：

```yaml
model:
  provider: openrouter
  default: anthropic/claude-sonnet-4.6

fallback_model:
  provider: anthropic
  model: claude-sonnet-4-6

delegation:
  provider: openrouter
  model: google/gemini-3-flash-preview

terminal:
  backend: docker
  timeout: 300
  container_persistent: true
  container_cpu: 1
  container_memory: 5120
  container_disk: 51200

compression:
  enabled: true
  threshold: 0.50

toolsets:
  - hermes-cli

approvals:
  mode: manual
```

### 简化判断

- 要稳定隔离：`docker`
- 要远程常驻：`ssh` 或 `daytona`
- 要省钱：主模型强，`delegation` 便宜
- 要减少误操作：toolsets 最小化，不要无脑 all

---

## 3. Skills 到底是什么？怎么安装官方 Skills？怎么自己写一个 Skill？

### 3.1 Skills 是什么

官方定义里，Skills 是 **按需加载的知识文档**，本质上是“程序性知识”。

它不是一个 Python 扩展模块，也不是一个 MCP server。它更像：

- 一份带 frontmatter 的 `SKILL.md`
- 外加可选的 `references/`、`scripts/`、`templates/`、`assets/`
- Hermes 在需要时才加载，遵循 progressive disclosure

你可以把它理解成：

- Memory 记“事实”
- Skill 记“做法”

### 3.2 官方 Skills 怎么安装

官方 optional skills 不是默认全部启用，而是显式安装。

常见命令：

```bash
hermes skills browse --source official
hermes skills install official/<category>/<skill>
hermes skills list
```

例如：

```bash
hermes skills install official/security/1password
hermes skills install official/productivity/siyuan
```

除了 official 源，Hermes 还支持：

- `skills-sh`
- `well-known`
- `github`
- `clawhub`
- `lobehub`

但如果你问“官方 Skills”，最稳妥就是 `official/...`

### 3.3 自己写一个 Skill

最小步骤：

1. 建目录

```bash
mkdir -p ~/.hermes/skills/my-category/my-skill
```

2. 写 `SKILL.md`

```markdown
---
name: my-skill
description: 这个 skill 是干什么的
version: 1.0.0
metadata:
  hermes:
    tags: [automation]
    category: my-category
---

# My Skill

## When to Use
什么时候该用

## Procedure
1. 第一步
2. 第二步

## Pitfalls
- 可能失败的地方

## Verification
怎么验证结果
```

3. 如果流程复杂，再补：
   - `scripts/`
   - `references/`
   - `templates/`

4. 新开会话测试：

```bash
hermes chat -q "/my-skill 帮我处理这个任务"
```

### 写 Skill 时最重要的观念

- 先把高频流程写前面
- 复杂解析逻辑尽量放到 `scripts/`
- API key 用 `required_environment_variables`
- 非敏感路径 / 偏好用 `metadata.hermes.config`

---

## 4. 什么情况下该写 Skill，什么情况下该写 Tool？

这是官方文档里讲得最明确的一组边界。

### 优先写 Skill 的情况

- 这个能力可以被表达成“说明文 + shell 命令 + 现有工具”
- 它本质是一个工作流、套路、SOP
- 它依赖外部 CLI 或 HTTP API，但不需要 Hermes 内核级集成
- 你希望它易改、易分享、低门槛

典型例子：

- Git 工作流
- Docker 管理
- arXiv 检索
- PDF 处理
- 你的知识库写入规范

### 应该写 Tool 的情况

- 需要内建认证流 / API key 处理
- 需要稳定、精确、每次都一样的底层处理逻辑
- 处理二进制、流式输出、实时事件
- 你要把它接入 Hermes 的 tool registry / toolset / check_fn / schema

典型例子：

- 浏览器自动化
- TTS
- Vision
- 一个带专用协议、专用鉴权、专用状态管理的系统级集成

### 一句话判断

如果你问的是“教 Hermes 怎么做”，多半是 Skill。  
如果你问的是“给 Hermes 新增一个系统级能力”，多半是 Tool。

---

## 5. Hermes 的子 agent / delegation 应该怎么理解？什么时候适合委派？

### 5.1 正确认知

Hermes 的 delegation 不是“复制一个带完整上下文的自己”，而是：

- 启动一个 **全新子 agent**
- 子 agent 有独立上下文、独立 terminal session、独立 toolset
- 父 agent 只收到它的最终摘要

最关键一句：**子 agent 对父会话一无所知。**

所以你必须把它需要的上下文写进：

- `goal`
- `context`

### 5.2 什么时候适合委派

适合：

- 并行研究多个主题
- 把会淹没主上下文的大任务拆出去
- 需要“新鲜视角”的审查 / 调研
- 推理密集型子任务

不适合：

- 单次工具调用
- 很机械的批处理
- 需要频繁向用户追问
- 很小的文件修改

### 5.3 Delegation 和 execute_code 的区别

- `delegate_task`：适合“需要判断、需要推理”的子任务
- `execute_code`：适合“多步机械流程 + 程序逻辑”的子任务

一个很好记的原则：

- 要脑力拆分，用 delegation
- 要流水线处理，用 execute_code

### 5.4 Hermes delegation 的限制

- 最多 3 个并行子任务
- 默认深度上只允许父到子，不允许子再继续委派
- 子 agent 不能再用 `delegate_task`、`clarify`、`memory`、`send_message`、`execute_code`

### 5.5 最佳实践

如果要委派，请把这些都写清楚：

- 项目根目录
- 相关文件路径
- 已知报错 / 目标
- 测试命令
- 约束条件

否则子 agent 会因为缺上下文而空转。

---

## 6. 如果我要让 Hermes 自动化抓取 URL、清洗文章、写入自己的知识库，再基于知识库生成口播文案，该怎么设计？

这个需求 Hermes 能做，但它不是“一个开关就全自动”的单功能。更准确地说，Hermes 提供的是一组可以拼成流水线的原件。

我建议按 4 层来设计。

### 6.1 第一层：调度层

用 `cronjob` 负责定时。

适合做的事：

- 每小时 / 每天抓一批 URL
- 定时跑一个来源清单
- 定时生成日报、周报、口播草稿

如果你需要抓取前先做一些机械预处理，可以用 cron 的 `script` 参数，让脚本先跑，stdout 再交给 agent 分析。

### 6.2 第二层：采集与清洗层

#### 采集

优先级建议：

1. 静态网页 / 普通文章：`web_search` + `web_extract`
2. 动态站点 / 需要交互：`browser_*`
3. 已有企业系统：MCP server

#### 清洗

如果是批量 URL，最合适的是 `execute_code`：

- 循环抓取
- 去重
- 抽取正文
- 裁剪广告 / 导航 / 噪声
- 统一成 JSON / Markdown

这样中间结果不会把主对话上下文塞爆。

### 6.3 第三层：知识库存储层

这里有 4 条路线，按复杂度从低到高：

#### 路线 A：本地文件知识库

最简单，直接让 Hermes 把清洗结果写到：

- Markdown 目录
- JSONL
- 按日期 / 来源分层的文件夹

优点：

- 最好控
- 最容易调试
- 不依赖额外系统

缺点：

- 检索能力要你自己再补

#### 路线 B：用官方 memory provider 做“长期知识”

如果你想要官方支持的长期记忆 / 语义检索体系，可以选：

- OpenViking：最像知识库，支持 `viking_add_resource`
- Supermemory：偏语义长期记忆
- Hindsight：偏知识图谱 / 反思
- ByteRover：偏本地知识树

其中，**OpenViking** 最接近“URL / 文档入库”的知识库模型。

#### 路线 C：接你自己的知识库系统

如果你已经有：

- 内部 CMS
- 向量库
- 笔记系统
- 企业知识平台

最干净的接法通常不是改 Hermes core，而是：

- **MCP server**
- 或一个专用 Skill
- 或一个专用 Tool / 插件

#### 路线 D：用官方 optional skill 接现成知识库

如果你的知识库本身就在官方 optional skill 覆盖范围内，也可以直接利用，比如：

- `official/productivity/siyuan`
- `official/research/qmd`

这类属于“官方提供的可选工作流”，不是 Hermes core 内建。

### 6.4 第四层：基于知识库生成口播文案

这一层建议不要直接“抓完就写”，而是分两步：

1. 检索与选题
   - 先从知识库里选出最近值得播报的条目
   - 去重、聚类、判断重要性

2. 口播生成
   - 让 Hermes 按固定模板输出
   - 例如：开场 1 句、主体 3 段、结尾 1 句
   - 明确要求口语化、短句、适合朗读

如果你有固定风格，最好把“口播写法”做成一个 Skill。

### 6.5 推荐的工程方案

这是我认为最稳的一版：

#### 方案 A：最小可用版

- `cronjob` 负责定时
- `execute_code` 负责批量抓取 + 清洗
- `write_file` 写入本地 Markdown/JSON 知识库
- 一个自定义 Skill 负责“知识库目录结构 + 命名规范 + 口播模板”
- 最后由主 agent 生成口播稿

#### 方案 B：更像产品的版本

- `cronjob`
- `execute_code`
- `OpenViking` 或 `MCP` 接你的知识库
- `delegate_task` 并行分析多个来源
- Skill 负责口播模板
- 如需语音，再接 `text_to_speech`

### 6.6 一个推荐的流水线示意

```text
cronjob
  -> execute_code 批量抓取 URL
  -> execute_code 清洗正文 / 去重 / 结构化
  -> 写入本地知识库 或 MCP/Memory Provider 入库
  -> 检索最近新增内容
  -> 生成口播文案
  -> 可选：TTS 输出音频 / deliver 到 Telegram、Discord 等
```

### 6.7 什么时候用 delegation

只有在“不同来源需要独立判断”时才值得加 delegation。

例如：

- 子 agent A：看 AI 新闻源
- 子 agent B：看行业博客
- 子 agent C：看政策 / 公司公告

最后父 agent 汇总成一篇口播稿。

如果只是 20 个 URL 的机械抓取，别用 delegation，用 `execute_code` 更稳。

---

## 7. 这套方案里，哪些部分是 Hermes 官方直接支持的，哪些是基于官方能力组合出来的工程实践？

这是最重要的边界题。

### 7.1 Hermes 官方直接支持

这些属于官方原生能力：

- 配置系统：`config.yaml`、`.env`、`hermes setup`、`hermes model`
- Provider 管理：多 provider、custom endpoint、provider routing、fallback model
- Toolsets：按平台 / 会话控制工具集
- Terminal backends：local、docker、ssh、modal、daytona、singularity
- Web 与 Browser：`web_search`、`web_extract`、`browser_*`
- `execute_code`
- `delegate_task`
- `cronjob`
- Skills 框架
- MCP 集成
- Memory 与 Memory Providers
- Python library 方式嵌入你自己的脚本系统

### 7.2 Hermes 官方支持，但不是默认核心工作流

这些也是官方支持，只是不是“开箱即用的一键流水线”：

- Official optional skills
- 外部 memory providers（OpenViking、Supermemory、Hindsight 等）
- 通过 MCP 接第三方系统
- 通过 Skill 封装你的私有工作流

### 7.3 基于官方能力组合出来的工程实践

下面这些通常不是 Hermes 给你现成产品功能，而是你基于官方能力自己搭出来的：

- URL 抓取 -> 去重 -> 清洗 -> 分块 -> 写入你的业务知识库
- 文章质量打分 / 来源可信度规则
- 自定义知识库 schema
- 选题规则、栏目规则、口播风格
- 审核流、回滚流、失败重试、幂等设计
- 监控、日志聚合、告警
- 把 Hermes 接到你内部 CMS / 向量库 / 内容平台

### 7.4 最清晰的结论

Hermes 官方给的是一套很强的 **agent runtime + tools + orchestration primitives**。  
你要的“采集、入库、再生成口播”的完整系统，Hermes 能做底座，但完整方案本身仍然是 **工程设计**，不是单个官方开关。

---

## 最后给你的落地建议

如果你现在就要开工，我建议分三步：

### 第一步：先搭最小闭环

- `cronjob`
- `web_extract`
- `execute_code`
- 本地 Markdown 知识库
- 一个“口播模板” Skill

先证明“能持续产出”。

### 第二步：再升级知识库

- 如果只是个人资料库：本地文件就够
- 如果要语义检索：OpenViking / Supermemory / ByteRover
- 如果是企业内部系统：MCP

### 第三步：最后再做并行与交付

- 多来源并行时再加 `delegate_task`
- 真要出音频时再接 `text_to_speech`
- 真要做多渠道推送时再加 `send_message` / gateway

---

## 一句话总结

Hermes 最适合做的是：  
**用配置、工具、Skills、cron、delegation、MCP 和 memory provider，把一个“人要反复做的内容工作流”变成可持续运行的 agent 系统。**

如果你愿意，我下一步可以继续把这份说明往下收敛成两种更可执行的产物之一：

1. 一份“适合个人知识库”的最小落地配置清单  
2. 一份“适合团队内容生产”的完整系统设计草案
