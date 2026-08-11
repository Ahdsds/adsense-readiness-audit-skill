# AdSense Readiness Audit Skill

一个面向 Codex 的公开 Skill，用 Google 官方资料审计内容型网站的 AdSense 申请与站点审核准备度。

它会检查账户资格、站点所有权与可抓取性、原创和低价值内容、导航与用户体验、Google Publisher Policies、流量、隐私披露、区域同意要求及 `ads.txt`，然后输出带证据的分级整改清单。

> [!IMPORTANT]
> 这是非官方社区项目，与 Google 没有隶属或合作关系。审计结果不是批准保证，也不构成法律意见。Google 政策可能随时更新；正式审计应重新打开相关官方页面核对。

## 能做什么

- 申请前检查网站是否具备送审条件。
- 诊断 “site not ready”、低价值内容、导航问题等拒审原因。
- 区分明确政策要求、官方质量信号、区域条件项和一般优化建议。
- 避免把固定文章数、字数、流量或域名年龄传言当成官方硬门槛。
- 通过只读、同源、有限页面数的探测脚本收集技术证据。
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

拒审诊断示例：

```text
$adsense-readiness-audit

请审计 https://example.com。
这是 Google 给出的拒审原因：网站尚未准备好展示广告。
请输出总体结论、P0/P1/P2/P3 风险、现场证据、修复顺序和重新送审检查表。
```

也可以上传拒审邮件或 Policy Center 截图，与网站一起检查。

## 技术探测脚本

Skill 可以调用内置脚本采集可达性、HTTPS、`robots.txt`、`ads.txt`、页面标题、语言、近似正文量、站内链接、常见信任页入口和 AdSense 代码信号：

```bash
python skills/adsense-readiness-audit/scripts/site_probe.py https://example.com --max-pages 30 --format markdown
```

正文近似量不是 Google 审核阈值。脚本也不能判断原创性、版权、合法性、流量质量或最终批准结果，必须结合人工审查。

## 仓库结构

```text
skills/adsense-readiness-audit/
├── SKILL.md
├── agents/openai.yaml
├── references/policy-baseline.md
└── scripts/site_probe.py
```

## 政策基线

仓库中的蒸馏基线最后核对于 2026-08-12，主要引用：

- [AdSense eligibility requirements](https://support.google.com/adsense/answer/9724?hl=en)
- [What to do when your site is not ready to show ads](https://support.google.com/adsense/answer/12176698?hl=en)
- [Google Publisher Policies](https://support.google.com/publisherpolicies/answer/10502938?hl=en)
- [Google Publisher Restrictions](https://support.google.com/publisherpolicies/answer/10437795?hl=en)
- [AdSense Program policies](https://support.google.com/adsense/answer/48182?hl=en)
- [Privacy-policy required content](https://support.google.com/adsense/answer/1348695?hl=en)
- [Consent requirements for EEA, UK and Switzerland publishers](https://support.google.com/adsense/answer/13554116?hl=en)
- [AdSense policy change log](https://support.google.com/adsense/answer/9336650?hl=en)

提交政策更新 PR 时，请提供对应的 Google 官方链接，并明确区分强制要求、质量信号、条件要求和经验建议。

## English

This repository contains a standalone Codex skill for auditing a content website's Google AdSense review readiness. It produces evidence-backed findings, separates hard policy blockers from quality risks and conditional requirements, and includes a bounded read-only technical probe.

Install it with `$skill-installer` using the GitHub subdirectory URL above, then invoke:

```text
$adsense-readiness-audit Audit https://example.com for AdSense review readiness.
```

This is an unofficial community project. It is not affiliated with Google, does not guarantee approval, and is not legal advice.

## License

[MIT](LICENSE)
