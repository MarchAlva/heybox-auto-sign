# 部署到 GitHub Actions（云端每日自动签到）

本说明教你把小黑盒自动签到放到 GitHub 上，每天在云端自动运行，**电脑不用开机**。

> 核心思路：代码（含脚本）推到 GitHub，账号 cookie 以**加密 Secret** 形式存储，工作流运行时读取后执行 `heybox_sign.js`。cookie 永不进入代码仓库。

---

## 一、前置条件

- 本地已有可运行的 `heybox-auto-sign/` 项目（本目录）。
- 已有一个 GitHub 账号。
- 本地 `cookie.txt` 里是正确的 App cookie（`pkey=...;x_xhh_tokenid=...;`，从手机抓的）。

---

## 二、在 GitHub 上准备仓库（二选一）

### 方案 A：Fork 原项目（推荐，最干净）

1. 打开 https://github.com/yowiv08/heybox ，点右上角 **Fork** → 创建 `你的用户名/heybox`。
2. Fork 已经包含原项目全部代码，我们只需把本目录新增的几个文件推上去。

### 方案 B：新建空白仓库

1. GitHub 右上角 **+ → New repository**，建议 **Private（私有）**，仓库名随意（如 `heybox-auto-sign`）。
2. **不要**勾选 Initialize with README（保持空仓库）。
3. 由于本地是浅克隆，推送前建议补全历史：
   ```bash
   git fetch --unshallow
   ```

---

## 三、添加 Cookie 密钥（关键，必须做）

1. 进入你的仓库 → **Settings → Secrets and variables → Actions → New repository secret**。
2. Name 填：`HEYBOX_CK`
3. Secret 内容填：**`cookie.txt` 里的那一行**（形如 `pkey=xxxx;x_xhh_tokenid=yyyy;`）。
   - 不要带换行，就是单行。
   - 本地可在项目目录执行 `type cookie.txt`（Windows）/`cat cookie.txt`（mac/Linux）复制。
4. 保存。

> ⚠️ cookie 会过期。过期后脚本会报 `relogin` 并让工作流失败（红色 ✗），此时重新抓手机 cookie 并更新这个 Secret 即可。

---

## 四、推送代码

在项目目录执行（把 `你的用户名` 换成实际用户名，方案 B 用你新建的仓库地址）：

```bash
# 方案 A（fork）添加远程
git remote add mine https://github.com/你的用户名/heybox.git

# 方案 B（空白仓库）添加远程
git remote add mine https://github.com/你的用户名/heybox-auto-sign.git

# 暂存并推送我们自己新增的文件（cookie.txt / sign_log.txt 已被 .gitignore 排除，不会上传）
git add .github/workflows/sign.yml .github/workflows/roll.yml GITHUB_ACTIONS.md .gitignore dump_token.py run_sign.bat scan_token.py
git commit -m "feat: add GitHub Actions auto-sign + token tools"
git push mine main
```

---

## 五、开启并验证

1. 仓库 → **Settings → Actions → General → Workflow permissions** 确认允许运行（默认即可）。
2. 仓库 → **Actions** 标签页，应能看到 `小黑盒每日签到` 和 `小黑盒0元抽奖盒券` 两个工作流。
3. 点 **Run workflow** 手动跑一次验证：
   - 绿色 ✓ = 成功，日志里能看到 `签到: 已完成` 和 `完成: 1/1`。
   - 红色 ✗ = 检查 Secret 是否正确、cookie 是否过期。
4. 之后每天 UTC 01:30（北京 09:30）自动跑。

---

## 六、注意事项

- **定时精度**：GitHub cron 可能延迟几分钟；若仓库 **60 天无任何提交/活动**，定时任务会被自动停用——届时手动 push 一次或重新 enable 即可。
- **私有仓库**：强烈建议 Private，避免 cookie 逻辑和账号暴露（即使 cookie 在 Secret 里，仓库公开也会增加风险）。
- **免费额度**：公开仓库 Actions 免费；私有仓库有每月额度，单脚本每日跑一次完全够用。
- **扩展**：想顺便自动领券，可参照 `sign.yml` 新建 `claim.yml` 工作流执行 `node heybox_claim.js`（同样依赖 `HEYBOX_CK`），与签到 / 抽奖盒券一样独立运行。
- **依赖外部签名服务** `hkey.qcciii.com`，若其不可用，签到会失败。
