# heybox-auto-sign

小黑盒自动化脚本集合，基于 Node.js 实现，支持小黑盒每日任务、普通领券、定时抢券、0 元抽奖盒券等功能。

> [!WARNING]
> **免责声明**：本人不懂编程。本仓库基于上游原仓库 [yowiv08/heybox](https://github.com/yowiv08/heybox) 及 AI（WorkBuddy）辅助修改而成，**不保证稳定可用，也不保证长期有效**。
>
> 后续的任何修改，都可能使原本可用的功能变得不可用；脚本也可能因小黑盒接口变动、签名服务失效、Cookie 过期等原因随时中断或失效。**请自行评估并承担使用风险。**

> 仅供学习交流使用。请自行承担使用风险，并遵守小黑盒平台规则。Cookie 属于敏感信息，请勿泄露给他人或提交到公开仓库。

## 来源与文件说明

> 本仓库派生自上游原仓库 [yowiv08/heybox](https://github.com/yowiv08/heybox)，并由 **WorkBuddy** 进行整理与修改。

### 源文件（继承自上游原仓库）

以下文件从原仓库 [yowiv08/heybox](https://github.com/yowiv08/heybox) 继承，内容与其保持一致（文件哈希一致，未做改动）。如上游更新，请以原仓库为准：

| 源文件 / 目录      | 说明                              |
| --------------- | ------------------------------- |
| `README.md`     | 项目说明文档（本文）                     |
| `heybox_sign.js`  | 每日签到与每日分享任务                     |
| `heybox_claim.js` | 普通领券                            |
| `heybox_rush.js`  | 定时抢券                            |
| `heybox_roll.js`  | 0 元抽奖盒券                         |
| `package.json`    | npm 脚本与依赖声明                     |
| `package-lock.json` | 依赖锁文件                         |
| `src/`          | 通用运行框架、接口、签名、上报等封装              |

原仓库地址：<https://github.com/yowiv08/heybox>

### 本仓库新增 / 修改的文件

以下文件由本仓库（`MarchAlva/heybox-auto-sign`）新增，使用 **WorkBuddy** 辅助整理与编写：

| 文件 / 目录           | 说明                          |
| ------------------ | --------------------------- |
| `.github/`         | GitHub Actions 工作流（`sign.yml` 每日签到、`roll.yml` 0 元抽奖盒券、`claim.yml` 普通领券、`rush.yml` 定时抢券、`keepalive.yml` 保活；`claim.yml` / `rush.yml` 默认停用） |
| `GITHUB_ACTIONS.md` | GitHub Actions 使用说明            |
| `dump_token.py`     | 导出 / 转储小黑盒 token 工具          |
| `scan_token.py`     | 扫描小黑盒 token 工具               |
| `run_sign.bat`      | Windows 一键运行签到脚本             |
| `.gitignore`        | Git 忽略规则                    |

## 功能概览

| 脚本                | 功能                                | npm script             |
| ----------------- | --------------------------------- | ---------------------- |
| `heybox_sign.js`  | 每日签到、每日分享任务、H 币信息输出               | `npm run heybox_sign`  |
| `heybox_claim.js` | 普通游戏优惠券自动领取                       | `npm run heybox_claim` |
| `heybox_rush.js`  | 限时券/抢券任务，支持自动发现目标、定时窗口、多轮并发请求     | `npm run heybox_rush`  |
| `heybox_roll.js`  | 0 元抽奖盒券任务，支持活动发现、前置任务处理、参与抽奖、分享任务 | `npm run heybox_roll`  |

## 已支持任务

### 每日任务：`heybox_sign.js`

支持自动完成：

| 任务          | 处理方式                 |
| ----------- | -------------------- |
| 签到          | 请求签到接口，并回查签到状态与奖励    |
| 分享任意帖子到社交平台 | 拉取帖子流，模拟浏览时长，上报分享事件  |
| 分享游戏详情到社交平台 | 拉取推荐游戏，发送游戏详情分享事件    |
| 分享游戏评价到社交平台 | 拉取推荐游戏和评论，发送游戏评价分享事件 |

其他能力：

* 自动读取单账号或多账号 Cookie
* 从 `pkey` 中解析 `heybox_id`
* 根据 `pkey` 生成请求所需 `imei`
* 通过 hkey 服务生成小黑盒 App 接口签名参数
* 自动跳过已完成任务
* 对未支持任务输出提示
* 输出当前账号 H 币数量
* 根据任务完成情况返回退出码

### 普通领券：`heybox_claim.js`

支持自动完成：

* 拉取普通游戏券列表
* 筛选可领取、未领取、未受限的券
* 自动刷新领取所需 session
* 逐个领取可领取优惠券
* 登录态失效时停止当前账号任务

### 定时抢券：`heybox_rush.js`

支持自动完成：

* 自动发现当前限时/特殊优惠券目标
* 支持配置指定抢券目标
* 从券标签中解析开抢时间
* 支持统一指定抢券时间
* 开抢前预热 session
* 在开抢窗口内多轮请求
* 支持多账号并发、单账号内多目标并发
* 自动跳过已抢光、已结束、已领取、库存不足等终态目标

默认抢券参数：

| 参数               | 默认值    | 说明                  |
| ---------------- | ------ | ------------------- |
| `prewarmMs`      | `1500` | 开抢前 1.5 秒刷新 session |
| `windowBeforeMs` | `300`  | 开抢前 0.3 秒进入请求窗口     |
| `windowAfterMs`  | `5000` | 开抢后持续请求 5 秒         |
| `intervalMs`     | `250`  | 请求轮次间隔              |
| `maxRounds`      | `20`   | 最大请求轮数              |
| `parallel`       | `6`    | 单轮最大并发数             |

### 0 元抽奖盒券：`heybox_roll.js`

支持自动完成：

* 自动发现 0 元抽奖活动
* 拉取活动详情和盒券列表
* 自动处理部分前置任务
* 自动参与抽奖
* 自动完成分享活动任务
* 输出活动任务状态和盒券状态

当前前置任务支持情况：

| 任务类型                  | 支持情况       |
| --------------------- | ---------- |
| `inject_js_for_count` | 支持，模拟停留后回查 |
| `focus_on_homeowner`  | 支持，直接上报    |
| `share_act`           | 支持，参与后执行分享 |
| `add_to_wish_list`    | 暂不支持，自动跳过  |
| `follow_game`         | 暂不支持，自动跳过  |
| 其他未知任务                | 输出提示，不自动处理 |

## 运行环境

* Node.js
* npm
* 依赖包：`got`

安装依赖：

```bash
npm install
```

单独安装依赖：

```bash
npm install got@^11.8.6
```

## 环境变量

所有脚本共用一个环境变量：

```bash
heybox_ck
```

值需要包含：

```bash
pkey=xxx;x_xhh_tokenid=xxx;
```

### 单账号示例

```bash
export heybox_ck='pkey=xxx;x_xhh_tokenid=xxx;'
```

### 多账号示例

支持换行分隔：

```bash
pkey=账号1;x_xhh_tokenid=账号1;
pkey=账号2;x_xhh_tokenid=账号2;
```

也支持使用 `&` 分隔：

```bash
pkey=账号1;x_xhh_tokenid=账号1;&pkey=账号2;x_xhh_tokenid=账号2;
```

## 本地运行

每日任务：

```bash
node heybox_sign.js
```

普通领券：

```bash
node heybox_claim.js
```

定时抢券：

```bash
node heybox_rush.js
```

0 元抽奖盒券：

```bash
node heybox_roll.js
```

也可以使用 npm scripts：

```bash
npm run heybox_sign
npm run heybox_claim
npm run heybox_rush
npm run heybox_roll
```

## 青龙面板使用

拉取仓库后，在青龙环境变量中添加：

| 名称          | 值                             |
| ----------- | ----------------------------- |
| `heybox_ck` | `pkey=xxx;x_xhh_tokenid=xxx;` |

建议定时任务：

```bash
task heybox_sign.js
task heybox_claim.js
task heybox_roll.js
```

`heybox_rush.js` 属于定时抢券脚本，建议根据券的开抢时间单独配置定时任务，不建议只按固定每日任务运行。

## GitHub Actions 使用

本项目自带五个 GitHub Actions 工作流（详见 `.github/workflows/`），可在 GitHub 云端自动运行，电脑无需开机：

- `.github/workflows/sign.yml`：**每日定时自动签到**，执行 `heybox_sign.js`（每日签到与每日分享任务）；
- `.github/workflows/roll.yml`：**每日定时 0 元抽奖盒券**，执行 `heybox_roll.js`（0 元抽奖盒券任务）；
- `.github/workflows/claim.yml`：**每日定时普通领券**，执行 `heybox_claim.js`（普通游戏优惠券自动领取）；**默认停用**，需手动启用；
- `.github/workflows/rush.yml`：**定时抢券**，执行 `heybox_rush.js`（限时券 / 抢券任务）；**默认停用**，需手动启用；
- `.github/workflows/keepalive.yml`：**每周保活**，向 `.keepalive` 写入时间戳并自动 push，用于刷新 GitHub 的「连续 60 天无活动」计时器，防止定时任务被自动停用。

> 签到、抽奖盒券、普通领券、抢券各自为**独立工作流**：各有独立运行记录、可单独启用 / 停用，互不影响。`sign.yml` 与 `roll.yml` 默认开启；`claim.yml` 与 `rush.yml` 默认停用（详见下方「停用 / 只保留某个工作流」）。

完整图文教程见 [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)。

### 配置方法

1. 在仓库 **Settings → Secrets and variables → Actions → New repository secret** 添加一个密钥：
   - Name：`HEYBOX_CK`
   - Secret：小黑盒 App 的 cookie 一行，形如 `pkey=xxxx;x_xhh_tokenid=yyyy;`（即 `heybox_ck` 环境变量所需内容，单行、无换行）
2. `sign.yml` 与 `roll.yml` 默认已开启，无需额外操作；`claim.yml` 与 `rush.yml` 默认停用，需先在 Actions 页 **Enable workflow** 才会运行。触发方式有两种：
   - **自动**：每天 UTC 01:30（北京时间 09:30）由 `schedule` 定时触发（已启用者同时触发，各跑各的）；
   - **手动**：仓库 **Actions** 标签页 → 对应工作流（如 `小黑盒每日签到`、`小黑盒0元抽奖盒券`）→ **Run workflow**。
3. 四个任务工作流均读取 `HEYBOX_CK` 密钥，`permissions` 仅申请 `contents: read`（最小权限）：`sign.yml` 运行 `node heybox_sign.js`、`roll.yml` 运行 `node heybox_roll.js`、`claim.yml` 运行 `node heybox_claim.js`、`rush.yml` 运行 `node heybox_rush.js`。各工作流独立执行、独立记录，可单独启用 / 停用其中一个而不影响其他。

### 停用 / 只保留某个工作流

**默认情况**：`sign.yml`（每日签到）与 `roll.yml`（0 元抽奖盒券）在推送后**默认开启**，每天 UTC 01:30（北京时间 09:30）由 GitHub 同时触发，二者各跑各的、互不影响；`claim.yml`（普通领券）与 `rush.yml`（定时抢券）**默认停用**，不会自动运行。

如果想**只签到、不抽奖**（或反过来只抽奖、不签到），只需停用其中一个工作流即可：

1. 进入仓库 **Actions** 标签页；
2. 在左侧工作流列表中点击要停用的那一个（例如 `小黑盒0元抽奖盒券`）；
3. 点击右上角的 **···（更多）** 菜单 → 选择 **Disable workflow（停用工作流）**；
4. 确认后，该工作流不再自动定时运行、也不会出现在手动触发列表；另一个工作流（如 `小黑盒每日签到`）照常每天 09:30 运行。

需要恢复时，在同一位置点击 **Enable workflow（启用工作流）** 即可。

> ⚠️ **请勿停用 `keepalive.yml`**：它是每周保活工作流。停用后仓库连续 60 天无提交，GitHub 会自动停用全部定时任务（含签到 / 抽奖）。只停用 `sign.yml` 或 `roll.yml` 不影响保活。

> 💡 `claim.yml` / `rush.yml` **默认停用**：如需启用，在 Actions 页对应工作流点 **··· → Enable workflow** 即可；`rush.yml` 为定时抢券，建议先按券的开抢时间修改其 `schedule` 后再启用（详见 `heybox_rush.js` 说明）。

### 验证与排查

- **Actions** 标签页查看运行结果：绿色 ✓ 表示成功（日志含 `签到: 已完成`、`完成: 1/1`）；红色 ✗ 表示失败。
- 常见失败原因：Secret 填写错误、cookie 已过期、外部签名服务 `hkey` 不可用。

### 风险提示

> ⚠️ 自动化脚本存在账号与合规风险，请仅用于学习交流，并自行承担一切后果。

- **Cookie 会过期**：App cookie 失效后工作流会报 `relogin` 并失败（红 ✗），需重新抓取手机 cookie 并更新 `HEYBOX_CK` Secret。
- **定时可能被停用（已自动规避）**：GitHub 对**连续 60 天无任何活动**的仓库会自动停用定时任务。本仓库已通过 `keepalive.yml` 工作流每周自动 push 一次来刷新计时器，可长期保活；若你 Fork 后删除了该工作流，则需手动 push 一次或重新 Enable 恢复。
- **定时不精准**：GitHub cron 可能延迟数分钟，请勿依赖其精确到秒。
- **仓库隐私**：强烈建议将仓库设为 **Private**，降低 cookie 逻辑与账号信息暴露风险（即便 cookie 存于加密 Secret，公开仓库风险仍更高）。
- **免费额度**：公开仓库 Actions 免费；私有仓库有每月额度，单脚本每日运行完全足够。
- **依赖外部服务**：签到依赖外部签名服务 `hkey.qcciii.com`，其不可用时签到会失败。
- **平台合规**：小黑盒平台可能将自动化行为视为违规，存在账号被风控 / 封禁的可能，请谨慎使用。

## 输出说明

每日任务输出示例：

```text
当前版本: 1.3.xxx build=xxxx

========== 账号1 ==========
账号=昵称 黑盒ID=123456 IMEI=xxxxxxxxxxxxxxxx
签到: 已完成 (+20经验 +20H币 +1盒电)
分享任意帖子到社交平台: 已完成
当前总H币: 123

完成: 1/1
```

普通领券输出示例：

```text
开始领券 heybox_id=123456
Claim targets: 10001, 10002
item_id=10001 游戏名: OK success
```

抢券输出示例：

```text
抢券计划:
 时间: 2026-01-01 12:00:00.0 (1张券)
 - ￥10 优惠券 pool=xxx act=xxx
 刷新session: 2026-01-01 11:59:58.5
 请求窗口: 2026-01-01 11:59:59.7 -> 2026-01-01 12:00:05.0
 间隔: 250ms, 轮数: 20, 并发: 1
```

抽奖盒券输出示例：

```text
抽奖活动 award_id=xxx 活动名
参与抽奖: {"status":"ok",...}
分享活动: 已完成
未自动处理任务: add_to_wish_list
```

## 退出码

`heybox_sign.js` 会根据每日任务完成情况设置退出码：

| 退出码 | 说明                   |
| --- | -------------------- |
| `0` | 所有账号核心任务均完成          |
| `1` | 存在账号任务未完成、初始化失败或脚本异常 |

其他脚本在异常时可能设置非 0 退出码，具体以运行日志为准。

## 常见问题

### 初始化失败：缺少环境变量 heybox_ck

没有配置 `heybox_ck`，或当前运行环境没有读取到该变量。请检查变量名是否为小写：

```bash
heybox_ck
```

### 无法从 pkey 解析 heybox_id

通常是 `pkey` 不完整、已过期或格式不正确。请重新抓取小黑盒 Cookie。

### hkey 接口失败

可能是外部 hkey 服务不可用、网络异常，或接口返回参数异常。可以稍后重试，或检查当前运行环境网络。

### 任务执行后仍显示未完成

可能原因：

* 小黑盒接口延迟结算
* Cookie 已失效
* 小黑盒任务规则发生变化
* 当前任务不在脚本支持范围内
* 某些任务需要 App 原生行为，脚本无法完全模拟

### 抽奖盒券提示心愿单任务不支持

`add_to_wish_list`、`follow_game` 等心愿单相关任务目前不会自动完成，脚本会跳过并输出提示。

### 抢券没有找到目标

可能原因：

* 当前没有可抢的限时券
* 券已结束、已抢光或已领取
* 接口返回结构发生变化
* 需要手动配置 `targets`

## 安全提示

* 不要把真实 Cookie 写进 README、Issue、日志截图或公开仓库
* 不要把 `heybox_ck` 提交到 Git
* Cookie 失效后请重新抓取
* 多账号运行时请确认每个账号格式完整

## 项目结构

```text
.
├── heybox_sign.js    # 每日签到与每日分享任务
├── heybox_claim.js   # 普通领券
├── heybox_rush.js    # 定时抢券
├── heybox_roll.js    # 0 元抽奖盒券
├── package.json
├── package-lock.json
├── src/              # 通用运行框架、接口、签名、上报等封装（继承自上游）
│   ├── core/         # 通用运行框架、HTTP、工具函数
│   └── heybox/       # 小黑盒账号、接口、签名、上报等封装
├── .github/
│   └── workflows/
│       ├── sign.yml        # 每日定时自动签到（heybox_sign.js，默认开启）
│       ├── roll.yml        # 每日定时 0 元抽奖盒券（heybox_roll.js，默认开启）
│       ├── claim.yml       # 每日定时普通领券（heybox_claim.js，默认停用）
│       ├── rush.yml        # 定时抢券（heybox_rush.js，默认停用）
│       └── keepalive.yml    # 每周保活，防止定时任务被停用
├── GITHUB_ACTIONS.md # GitHub Actions 使用图文说明
├── dump_token.py     # 导出 / 转储小黑盒 token 工具
├── scan_token.py     # 扫描小黑盒 token 工具
├── run_sign.bat      # Windows 一键运行签到脚本
└── .gitignore        # Git 忽略规则
```
