# AdSense 网站审核政策基线

本文件是面向普通内容网站的蒸馏基线，最后在线核对日期：**2026-08-12**。政策会变化；正式审计先检查本文末尾的官方变更日志和相关原文。

## 证据标签

- **R—官方要求**：官方使用 must、may not、required、need to fix 等约束性表述，或明确列为资格条件。
- **Q—官方质量信号**：官方明确用于站点准备度或常见拒审原因，但没有公开机械阈值。
- **C—条件要求**：只对某地区、内容类型、实现方式或账户状态适用。
- **B—最佳实践**：有帮助但不是普遍审核硬门槛。不得改写成 R。

## 一、账户与申请资格

| ID | 标签 | 核查要求 | 判定提示 |
|---|---|---|---|
| A01 | R | 申请人年满 18 岁；未满 18 岁由家长或监护人用其账户申请并收款。 | 只能由用户或账户资料确认。 |
| A02 | R | 每个发布商只允许一个 AdSense 账户；被因无效流量或政策终止者不得另开新账户。 | 同一收款人、地址、电话等可能触发重复账户。 |
| A03 | R | 拥有自己的内容，并能控制站点 HTML 或用 Google 支持的方式验证所有权。 | 普通站点需能放置 AdSense 代码；Search Console 或 ads.txt 也可能作为站点连接/验证方式。 |
| A04 | R | 账户、付款和站点声明必须真实、完整，不得有误导性遗漏。 | 包括 ads.txt、URL、地理位置和广告请求中的信息。 |
| A05 | R | 内容主要语言必须在 Google 支持列表中。 | 简体中文、繁体中文和英文均在当前列表中；多语言站点按页面主要语言检查。 |
| A06 | C | 发布商及使用场景不得违反适用制裁和出口管制。 | 只在相关主体、地区或受限方场景下展开。 |

## 二、站点连接与技术可达性

| ID | 标签 | 核查要求 | 判定提示 |
|---|---|---|---|
| T01 | R | 提交正确 URL，站点已发布且在线。 | 空白测试页、模板站、建设中页面会失败。 |
| T02 | R | 审核时 AdSense 能在无需密码的情况下访问站点。 | 批准后可为受保护内容配置 crawler login；审核前登录墙是阻塞项。 |
| T03 | R | robots.txt、WAF、CDN 或地区限制不得阻止 AdSense 抓取工具。 | 同时检查 `Mediapartners-Google` 和通用规则；脚本探测只是近似证据。 |
| T04 | R | 使用 HTTPS 时证书须由认可机构签发，且 HTTP 重定向到 HTTPS。 | 自签名、证书错误或重定向循环是阻塞项。 |
| T05 | R | 按账户给出的方式连接/验证站点。若用代码，应放在申请站点页面的 `<head>` 与 `</head>` 之间。 | 也可能使用 Search Console 所有权或 ads.txt 方式；以账户界面为准。 |
| T06 | B/C | ads.txt 非强制但强烈建议；一旦使用，发布商必须被正确列为授权卖方。 | 不得把“没有 ads.txt”单独判为普遍拒审原因。 |

## 三、内容价值与完整性

| ID | 标签 | 核查要求 | 判定提示 |
|---|---|---|---|
| C01 | Q | 提供足够的独特、有价值、相关内容，使 Google 能理解站点主题，并给用户访问和再次访问的理由。 | Google 未公布文章数、字数、流量或域名年龄阈值。 |
| C02 | Q/R | 页面应有完整句子和段落；不应主要是图片、视频、标题、导航、提醒或广告，也不能是建设中、空模板或低价值页面。 | “内容量近似值”只用于抽样，不是阈值。 |
| C03 | R | 不得在没有实质评论、策展或增量价值时复制、轻改、抓取或嵌入他人内容；同时遵守版权。 | 嵌入视频、图片或聚合信息必须有显著原创增量。 |
| C04 | Q/R | 不在自动生成、几乎无原创内容的页面放广告；联盟内容若无额外功能或价值，只能是站点很小的一部分。 | 检查批量模板页、参数页、门页和关键词变体。 |
| C05 | R | 不在违反 Google 网页搜索垃圾政策的页面展示 Google 广告。 | 特别检查伪装、门页、过期域名滥用、被黑内容、规模化低价值内容、抓取和站点声誉滥用等当前规则。 |
| C06 | R | 不得让广告或付费推广材料多于发布者内容。 | 适用于实际广告布局；申请前也可审查预留位和第三方广告。 |
| C07 | Q/R | 域名历史不是独立年龄门槛；但旧垃圾路径、被黑内容、恶意跳转或以操纵排名为主要目的的低价值过期域名再利用，会分别落入安全、体验或搜索垃圾政策。 | 按 [domain-history.md](domain-history.md) 建立时间线并映射当前证据，不因换过主题或购买二手域名单独定罪。 |

## 四、导航与用户体验

| ID | 标签 | 核查要求 | 判定提示 |
|---|---|---|---|
| U01 | Q/R | 导航清晰、可读、功能正常、目标准确，并跨主要设备/浏览器正常显示。 | 检查菜单、下拉、分页、面包屑和关键 CTA。 |
| U02 | Q/R | 不得有死链、虚假下载/流媒体声明、无关或误导跳转、内容与页面主题/承诺不一致。 | 记录具体 URL 和交互路径。 |
| U03 | R | 不得用弹窗、强制重定向、下载、恶意软件或其他方式妨碍导航。 | 也不得让广告像菜单、下载按钮或内容。 |
| U04 | R | Google 广告不得遮挡内容/操作、紧贴动作控件造成误点，或形成只能点击广告才能离开的死路。 | 动态和移动端布局必须人工检查。 |
| U05 | R | 页面不得包含 abusive experiences、恶意软件或不受欢迎的软件体验，并应符合 Better Ads Standards。 | 软件/下载站需检查功能、安装后果、卸载和条款披露。 |

## 五、流量与广告行为

| ID | 标签 | 核查要求 | 判定提示 |
|---|---|---|---|
| F01 | R | 点击和展示必须来自真实兴趣；不得自点、人工或自动刷量。 | 账户历史和分析数据通常需要用户提供。 |
| F02 | R | 不得请求、诱导、奖励用户点击/观看普通广告，也不得用箭头、误导图片或标签吸引注意。 | 合规的 rewarded inventory 另按专门政策。 |
| F03 | R | 不得使用 paid-to-click、paid-to-surf、autosurf、click exchange、群发垃圾邮件、恶意广告或软件触发流量。 | 若购买推广流量，还要满足 Google 落地页质量要求。 |
| F04 | R | 广告代码、位置和行为不得人为抬高效果或损害广告主。 | 检查弹窗/邮件/非内容页/私密通信页等不适当位置。 |

## 六、Google Publisher Policies

以下是禁止货币化的核心类别。发现明确实例时标为 P0，并引用当前官方细则；不要仅凭关键词定罪。

- 非法内容和侵犯他人合法权利。
- 侵犯版权、销售或推广假冒商品。
- 危险或贬损内容、骚扰、仇恨、伤害威胁、恐怖组织相关内容、勒索。
- 虐待动物及濒危/受威胁物种制品交易。
- 虚假陈述、冒充、隐瞒发布者或内容目的、欺骗做法、重大有害虚假主张、相关操纵媒体。
- 协助欺骗、黑客/破解、未经授权监控等不诚实行为。
- 露骨色情、非自愿性主题、色情深度伪造、补偿性行为、邮购新娘。
- 面向家庭的内容中出现不适宜成人主题。
- 任何儿童性虐待、剥削或危害内容。
- 无发布者内容、低价值、建设中、仅用于提醒/导航的库存。
- 无增量的复制内容、广告多于发布者内容、不支持的主要语言。
- 不诚实声明、干扰式广告、脱离上下文的广告。
- 隐私、识别用户、设备/精确位置、儿童定向、搜索垃圾、恶意软件、Better Ads、授权库存和制裁方面的违规。

页面上的 UGC、评论、其他广告、嵌入和外链也计入审核范围；站点可能因其中的内容承担责任。

## 七、Google Publisher Restrictions

限制内容不是自动的政策违规，但广告来源会减少，可能没有广告。分别报告“合规风险”和“变现限制”。当前主要内容限制包括：

- 性暗示/裸露等非露骨性内容；震惊内容或大量粗俗语言。
- 爆炸物、枪支及配件、其他武器。
- 烟草、娱乐性毒品。
- 酒类在线销售或滥用。
- 在线赌博（按用户所在地有列明例外地区，审计时必须重查当前名单）。
- 处方药在线销售、未经批准的药品或补充剂。
- 从 Google Play 因政策违规下架的应用。

另有广告与内容互相遮挡以及视频库存限制。涉及这些形式时读取完整官方页面。

## 八、隐私与区域同意

| ID | 标签 | 核查要求 | 判定提示 |
|---|---|---|---|
| P01 | R | 有并遵守隐私政策，清楚披露使用 Google 产品导致的数据收集、共享和使用，以及 Cookie、Web Beacon、IP 地址或其他标识符。 | 披露第三方可能因广告投放设置/读取 Cookie 或使用 Web Beacon/IP。 |
| P02 | R | 披露 Google 等第三方供应商使用广告 Cookie、个性化依据以及用户退出个性化广告的方法。 | 若启用其他第三方广告网络，也披露供应商及退出方式。 |
| P03 | R | 不向 Google 传递可被识别为个人身份信息的数据；未经充分通知和事先明确同意，不得合并身份信息与先前的非身份数据。 | 检查 URL 参数、表单、分析和广告请求。 |
| P04 | C/R | 收集或使用精确位置时，及时披露用途和共享、事先明确同意、加密传输，并写入隐私政策。 | 只在使用精确位置数据时适用。 |
| P05 | C/R | 面向 13 岁以下儿童的站点/区域按 COPPA 要求通知或标记，并不得基于其活动做兴趣广告。 | 年龄和地区法律可能有额外要求。 |
| P06 | C/R | 向 EEA、英国或瑞士用户投放广告时，遵守 EU 用户同意政策；个性化广告需使用 Google 认证且集成 IAB TCF 的 CMP。 | 2026-03-01 起 IAB TCF v2.3 为强制版本；运行审计时重查过渡/版本状态。 |

隐私政策的存在不能替代实际同意机制或适用法律合规。此技能提供政策审计，不提供法律意见。

## 九、明确不是普遍硬门槛

Google 当前公开材料没有给出以下普遍批准数字：最低文章篇数、每篇最低字数、最低月流量、最低域名年龄、固定更新频率。Google 要求的是足够、独特、有价值、完整、可导航的内容，应以现场质量证据判断。

About、Contact 和 Terms 页面不是所有站点都被官方明文列为必须页面；它们常用于证明发布者身份、内容目的、联系方式和交易规则。将缺失标为 P1/P3 需给出与该站点业务相关的理由，不得冒充硬规则。

AI 辅助创作、WordPress 或其他 CMS、免费主题、同时使用其他广告网络本身都不等于不合格；实际内容、实现和政策合规才是判断对象。

域名旧、域名新、当前 RDAP 注册日期较近、使用隐私保护、历史上换过主题或曾被其他主体使用，也不是 Google 公布的独立 AdSense 拒审门槛。只有当历史检查发现当前仍存在的违规、安全、抓取、所有权、内容价值或用户体验问题时，才按对应政策判级。

## 十、官方来源索引

审计时优先打开与发现项直接对应的页面：

- [Eligibility requirements for AdSense](https://support.google.com/adsense/answer/9724?hl=en)
- [Owning the site you want to use to participate in AdSense](https://support.google.com/adsense/answer/91205?hl=en)
- [What to do when your site is not ready to show ads](https://support.google.com/adsense/answer/12176698?hl=en)
- [AdSense site management](https://support.google.com/adsense/answer/12131223?hl=en)
- [Fix AdSense crawler issues](https://support.google.com/adsense/answer/2381908?hl=en)
- [Google AdSense content and user experience](https://support.google.com/adsense/answer/10015918?hl=en)
- [Your AdSense account wasn't approved](https://support.google.com/adsense/answer/81904?hl=en)
- [AdSense Program policies](https://support.google.com/adsense/answer/48182?hl=en)
- [Google Publisher Policies](https://support.google.com/publisherpolicies/answer/10502938?hl=en)
- [Google Publisher Restrictions](https://support.google.com/publisherpolicies/answer/10437795?hl=en)
- [Languages Google publisher products support](https://support.google.com/adsense/answer/9727?hl=en)
- [Required privacy-policy content](https://support.google.com/adsense/answer/1348695?hl=en)
- [Consent requirements for EEA, UK and Switzerland publishers](https://support.google.com/adsense/answer/13554116?hl=en)
- [Publisher integration with IAB Europe TCF](https://support.google.com/adsense/answer/9804260?hl=en)
- [Ads.txt guide](https://support.google.com/adsense/answer/12171612?hl=en)
- [AdSense policy change log](https://support.google.com/adsense/answer/9336650?hl=en)
- [Google Publisher Standards change log](https://support.google.com/publisherpolicies/answer/10852414?hl=en)
- [Spam Policies for Google Web Search](https://developers.google.com/search/docs/essentials/spam-policies)
- [Manual actions report](https://support.google.com/webmasters/answer/9044175?hl=en)
- [Google Safe Browsing Site Status](https://transparencyreport.google.com/safe-browsing/search)

引用时链接到支持具体发现的页面，不要只链接变更日志或本文件。
