# AdSense Readiness Audit Skill

一个面向 Codex 的公开 Skill，用 Google 官方资料审计内容型网站的 AdSense 申请与站点审核准备度。

它会先回答“这个域名以前做什么”，再检查 Cloudflare/CDN/WAF、旧站残留、安全信誉、账户资格、站点所有权与可抓取性、原创和低价值内容、导航与用户体验、Google Publisher Policies、流量、隐私披露、区域同意要求及 `ads.txt`，最后输出带证据的完整阻塞项登记表。

> [!IMPORTANT]
> 这是非官方社区项目，与 Google 没有隶属或合作关系。审计结果不是批准保证，也不构成法律意见。Google 政策可能随时更新；正式审计应重新打开相关官方页面核对。

## 能做什么

- 申请前检查网站是否具备送审条件。
- 用 Internet Archive 历史快照、RDAP、DNS、TLS 和跳转证据建立域名前身用途时间线。
- 先识别 IANA 保留/特殊用途域名；对不可注册、不可转让或不能由申请人控制的域名快速判定所有权阻塞。
- 排查旧垃圾路径、被黑内容、恶意软件、伪装、意外跳转、Search Console 手动处置和过期域名滥用风险。
- 检测 Cloudflare 响应头、Challenge Page、`520`–`526`、缓存和 robots 线索，并指导复核 WAF/Bots、Access、SSL/TLS、Workers/Redirects 与真实 Google 爬虫事件。
- 诊断 “site not ready”、低价值内容、导航问题等拒审原因。
- 区分明确政策要求、官方质量信号、区域条件项和一般优化建议。
- 避免把固定文章数、字数、流量或域名年龄传言当成官方硬门槛。
- 通过只读、同源、有限页面数的探测脚本收集技术证据。
- 对账户、所有权、抓取、域名历史、安全、搜索垃圾、内容价值、内容政策、体验、流量、广告实现、隐私、限制内容和后台状态十四个通道逐项登记；公开面无法证明的项目保留为未知。
- 按 `P0 硬性阻塞`、`P1 高拒审风险`、`P2 条件项`、`P3 优化项` 输出结果。

## 安装

### 用 Codex Skill Installer

在 Codex 中输入：

```text
$skill-installer
Install the skill from https://github.com/Ahdsds/adsense-readiness-audit-skill/tree/main/skills/adsense-readiness-audit
```

### 手动安装

克隆仓库后，把 `skills/adsense-readiness-audit` 复制到 `$CODEX_HOME/skills`；如果没有设置 `CODEX_HOME`，使用 `~/.codex/skills`。

macOS / Linux：

```bash
git clone https://github.com/Ahdsds/adsense-readiness-audit-skill.git
mkdir -p ~/.codex/skills
cp -R adsense-readiness-audit-skill/skills/adsense-readiness-audit ~/.codex/skills/
```

Windows PowerShell：

```powershell
git clone https://github.com/Ahdsds/adsense-readiness-audit-skill.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse -Path ".\adsense-readiness-audit-skill\skills\adsense-readiness-audit" -Destination "$env:USERPROFILE\.codex\skills\"
```

## 使用

最简单的调用方式：

```text
$adsense-readiness-audit 审计 https://example.com 的 AdSense 审核准备度
```

包含域名历史的调用方式：

```text
$adsense-readiness-audit 检查 https://example.com 以前做什么，并列出一切可能阻止 AdSense 审核通过的因素。
```

拒审诊断示例：

```text
$adsense-readiness-audit

请审计 https://example.com。
这是 Google 给出的拒审原因：网站尚未准备好展示广告。
请输出总体结论、P0/P1/P2/P3 风险、现场证据、修复顺序和重新送审检查表。
```

也可以上传拒审邮件或 Policy Center 截图，与网站一起检查。

## 技术探测脚本

Skill 可以调用内置脚本采集可达性、HTTPS、`robots.txt`、`ads.txt`、页面标题、语言、近似正文量、站内链接、常见信任页入口、AdSense 代码，以及 Cloudflare 响应头、挑战和 `520`–`526` 信号：

```bash
python skills/adsense-readiness-audit/scripts/site_probe.py https://example.com --max-pages 30 --format markdown
```

域名历史探测脚本会查询 IANA 引导的 RDAP 服务、当前 DNS/HTTP/HTTPS/TLS，以及有限数量的 Wayback Machine 首页快照：

```bash
python skills/adsense-readiness-audit/scripts/domain_history_probe.py example.com --wayback-snapshots 4 --format markdown
```

正文近似量不是 Google 审核阈值。域名年龄、换过主题、使用隐私保护或购买二手域名也不是独立拒审门槛。两个脚本都不能判断完整所有权历史、原创性、版权、合法性、流量质量、Google 后台状态或最终批准结果，必须结合人工审查。

## 仓库结构

```text
skills/adsense-readiness-audit/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── policy-baseline.md
│   ├── domain-history.md
│   └── cloudflare-cdn.md
└── scripts/
    ├── site_probe.py
    └── domain_history_probe.py
```

## 政策基线

仓库中的蒸馏基线最后核对于 2026-08-12，主要引用：

- [AdSense eligibility requirements](https://support.google.com/adsense/answer/9724?hl=en)
- [What to do when your site is not ready to show ads](https://support.google.com/adsense/answer/12176698?hl=en)
- [Google Publisher Policies](https://support.google.com/publisherpolicies/answer/10502938?hl=en)
- [Spam Policies for Google Web Search](https://developers.google.com/search/docs/essentials/spam-policies)
- [Manual actions report](https://support.google.com/webmasters/answer/9044175?hl=en)
- [Google Publisher Restrictions](https://support.google.com/publisherpolicies/answer/10437795?hl=en)
- [AdSense Program policies](https://support.google.com/adsense/answer/48182?hl=en)
- [Privacy-policy required content](https://support.google.com/adsense/answer/1348695?hl=en)
- [Consent requirements for EEA, UK and Switzerland publishers](https://support.google.com/adsense/answer/13554116?hl=en)
- [AdSense policy change log](https://support.google.com/adsense/answer/9336650?hl=en)
- [ICANN Lookup FAQ](https://lookup.icann.org/en/faq)
- [Wayback Machine general information](https://archivesupport.zendesk.com/hc/en-us/articles/360004716091-Wayback-Machine-General-Information)
- [IANA Example Domains](https://www.iana.org/help/example-domains)
- [IANA Special-Use Domain Names](https://www.iana.org/assignments/special-use-domain-names/special-use-domain-names.xhtml)
- [About the AdSense ads crawler](https://support.google.com/adsense/answer/99376?hl=en)
- [Fix AdSense crawler issues](https://support.google.com/adsense/answer/2381908?hl=en)
- [Cloudflare: Detect a Challenge Page response](https://developers.cloudflare.com/cloudflare-challenges/challenge-types/challenge-pages/detect-response/)
- [Cloudflare 5xx errors](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-5xx-errors/)

提交政策更新 PR 时，请提供对应的 Google 官方链接，并明确区分强制要求、质量信号、条件要求和经验建议。

## English

This repository contains a standalone Codex skill for auditing a content website's Google AdSense review readiness. It reconstructs a bounded domain-use timeline, checks historical residue and security signals, produces a complete blocker register, separates hard policy blockers from quality risks and conditional requirements, and includes read-only site and domain-history probes.

Install it with `$skill-installer` using the GitHub subdirectory URL above, then invoke:

```text
$adsense-readiness-audit Audit https://example.com for AdSense review readiness.
```

This is an unofficial community project. It is not affiliated with Google, does not guarantee approval, and is not legal advice.

## License

[MIT](LICENSE)
