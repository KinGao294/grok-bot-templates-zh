# Grok Bot 模板市场 · 中文导航速查（非官方）

一个可静态部署的中文导航站，把 xAI/SpaceXAI 官方 **Bot Marketplace** 的公开模板做成中文货架。
**安装按钮一律跳官方原页，本站不托管模板、不代理安装、不收费。**

- 官方目录：<https://x.ai/bot/marketplace>
- 数据快照日期：**2026-09-05**
- 当前收录：**69 个模板 / 43 位创作者 / 9 个官方分类**（另有 2 个模板官方未打分类，站内归入「其他」）

## 本地预览

纯静态，无构建步骤。任选一种：

```bash
# 方式一：起个本地服务器（推荐）
cd sites
python3 -m http.server 8765
# 打开 http://127.0.0.1:8765/grok-bot-templates-zh/
```

```bash
# 方式二：直接双击 index.html
# 数据是 assets/data.js（挂在 window 上），不走 fetch，所以 file:// 直开也能正常渲染。
```

## 目录结构

```
grok-bot-templates-zh/
├── index.html            页面本体
├── assets/
│   ├── styles.css
│   ├── app.js            搜索 / 分类筛选 / 卡片渲染
│   └── data.js           【自动生成】69 条模板数据
└── tools/
    ├── refresh.py        从官方页抓取 + 合并中文译名 → 生成 data.js
    └── zh.json           中文译名与说明（手工维护的唯一数据源）
```

## 数据是怎么来的

`tools/refresh.py` 抓 `https://x.ai/bot/marketplace`，从页面内嵌的 RSC 负载里取出官方 `templates` 数组，
字段包括 `id`（slug）、`name`、`creatorName`、`handle`、`description`、`categories`、`addHref`。
`addHref` 形如 `grokbot://app/v1/bot-template?id=<token>`，其中的 token 就是官方模板预览页
`https://x.ai/bot/<token>` 的地址。

所以站内每张卡片的两个链接都是官方域名，且都由官方数据直接推导，没有任何人工拼装：

| 按钮 | 目标 | 说明 |
| --- | --- | --- |
| 安装 / 使用（官方页） | `https://x.ai/bot/<token>` | 官方模板预览页，页面上的 **Add to Grok Bot** 是 `grokbot://` 深链，需本机装有 Grok Bot 客户端 |
| 官方详情 | `https://x.ai/bot/marketplace/bots/<slug>` | 官方市场详情页 |

刷新数据：

```bash
cd sites/grok-bot-templates-zh
python3 tools/refresh.py          # 重新抓取并生成 assets/data.js
python3 tools/refresh.py --check  # 只校验站内所有链接是否仍返回 200
```

生成时若发现官方新增了 `zh.json` 里没有的 slug，脚本会打印提示，页面会先回退显示英文原名，
补译只需在 `tools/zh.json` 的 `templates` 下加一条 `"<slug>": {"name": "...", "desc": "..."}` 再重跑脚本。

链接可用性已核对：生成时 69 条 `x.ai/bot/<token>` 与 69 条详情页全部返回 HTTP 200。

## 已知缺口

1. **只收官方市场里的模板。** 创作者自己在 X 上发、但没进官方市场的分享链接（同样是 `x.ai/bot/<token>` 形式）
   社区里数量远多于 69 个，但没有官方目录背书、真伪与存活难以核实，本站一律不收。
   如果以后要扩，建议单开一个「社区收录」页并逐条标注来源帖，不要和官方目录混排。
2. **是快照不是实时。** 官方市场持续新增，本站数据要跑一次 `refresh.py` 才更新。页头显示的快照日期就是上次刷新时间。
3. **安装量 / 评分没有收录。** 官方页面返回的 `installCount` 当前全部为 0，看不出真实热度，展示出来只会误导，所以整列不做。
4. **分类以官方为准。** 官方给的是 9 个分类，其中 `From Grok Bot Team`（官方精选）与业务分类可以叠加；
   有 2 个模板官方没打任何分类，站内归入「其他」，没有替官方补分类。
5. **没有实际安装或运行过任何模板。** 核对只到「链接返回 200 且页面标题与模板名一致」这一层。
6. **`x.ai/bot` 下载页本身抓不到。** 该路径对我们的出口 IP 返回 Cloudflare 403，
   但 `x.ai/bot/marketplace` 及其子页可以正常访问，所以模板数据不受影响。

## 合规口径

- 页眉、页脚、以及本 README 都写明 **非官方**，与 xAI / SpaceXAI / Cursor / Anysphere 无隶属或合作关系。
- 不伪造安装流程：站内没有任何"一键安装"的假动作，点击即离站到 x.ai。
- 不复制官方模板的完整 prompt / 技能 / 例行任务内容，只做导航与中文摘要。
- Grok、Grok Bot、Cursor 为各自权利人商标，此处仅作指称性使用。

## 部署

任何静态托管都能直接用（GitHub Pages / Cloudflare Pages / Vercel）。
仓库是 private，用 GitHub Pages 需要仓库可公开或使用付费方案，具体见
[`drafts/2026-09-07-assets.md`](../../drafts/2026-09-07-assets.md)。
