# 域名历史、旧站残留与阻塞项审查

本参考用于回答“这个域名以前做什么”以及“还有什么会阻止 AdSense 审核”。最后在线核对日期：**2026-08-12**。

## 目录

1. 原则与证据等级
2. 域名前身用途时间线
3. 当前注册、DNS 与基础设施
4. 旧 URL、索引和安全残留
5. 过期域名滥用与用途切换
6. 完整阻塞项登记表
7. 判级规则
8. 复验与输出模板
9. 来源索引

## 一、原则与证据等级

域名历史不是 Google 公布的独立 AdSense 年龄门槛。审查历史的目的，是发现仍会影响当前站点的垃圾政策、安全、可抓取性、所有权、内容价值或用户体验问题。

按可靠度使用证据：

1. **当前一手证据**：当前 HTTP 响应、源代码、DNS、TLS、robots、页面内容、用户自己的 AdSense/Search Console 后台。
2. **权威登记证据**：注册局/注册商通过 RDAP 返回的当前公开注册数据。它不等于完整所有权历史。
3. **历史快照证据**：Internet Archive 等保存的当时页面。快照可以证明某个 URL 在某次抓取时呈现过什么，不能证明经营者身份或完整站史。
4. **搜索残留证据**：Google `site:` 结果、缓存摘要、旧 sitemap、外链目标。摘要可能过时，必须打开目标 URL 复验。
5. **第三方信誉信号**：安全扫描、黑名单、外链数据库、流量估算。只能用作排查线索，除非当前可复现或有 Google 官方后台佐证。
6. **推断**：由时间、主题和技术变化推断的用途切换或易主可能性。必须明确写“推断”，不能冒充事实。

每条重要结论记录 `来源 URL/后台位置、抓取或事件日期、现场摘要、证据类型、置信度`。证据冲突时保留冲突，不强行合并。

## 二、域名前身用途时间线

### 2.0 保留/特殊用途域名快速判定

先查 IANA Example Domains 与 Special-Use Domain Names registry。Special-Use 名称及其子域可能具有非普通公网 DNS 语义；`example.com`、`example.net` 和 `example.org` 明确不可注册或转让，也不为生产应用设计。

若目标属于这些名称：

1. 记录命中的 IANA 条目、用途和查询日期。
2. 若申请人不可能拥有或控制该域名，标为所有权 `P0`；不要把它误写成普通内容质量问题。
3. 给出当前页面与最少量历史快照，说明其真实用途，然后停止深度内容/流量推断。
4. 对其他 Special-Use 名称先读取对应 RFC；“特殊用途”不自动等于同一种处置，但必须确认它是否能作为 AdSense 可验证的公网生产站点。

### 2.1 标准步骤

1. 规范化主机名：记录 Unicode 和 punycode；区分裸域、`www`、常见子域与完全不同的可注册域。
2. 从 Internet Archive 日历或 CDX 数据中找出最早、最近和用途变化附近的快照。
3. 每个有覆盖的自然年至少抽一个代表性首页；快照很多时按“最早 + 每年/每阶段 + 最近”采样，而非只看两个端点。
4. 对关键年份补查 `/about`、`/contact`、分类页或当时导航中能解释业务的页面。
5. 记录标题、品牌名、主要语言、主题、站点类型、商业模式、联系方式/组织名、主要出站目标。
6. 把连续相同用途合并为区间；在品牌、语言、行业、模板、注册事件、DNS 或跳转发生明显变化时建立变化点。
7. 至少用第二种线索复核高风险变化：Common Crawl、旧搜索结果、历史 DNS、外链锚文本、旧证书或用户交易资料。

### 2.2 用途分类

使用中性、可复核的类别，例如：

- 企业/机构官网、媒体/博客、论坛/UGC、工具/SaaS、电商、联盟/评测、目录/聚合、下载/流媒体、停放页、出售页、占位页、跳转域名、无法判断。
- 若出现成人、赌博、药品、破解、仿冒、恶意下载等高风险主题，记录具体页面和日期，不给整个历史时期贴无证据标签。
- 若快照只有框架、资源损坏或跳到实时网页，标记“不足以判断”。

### 2.3 归档局限

- Wayback Machine 可能因爬虫未发现、登录、robots、技术失败或站长请求而缺失页面。
- 归档页面可能缺图片、CSS、JavaScript 或站内链接；访问归档时可能跳到临近日期甚至实时页面。
- 没有快照不代表域名从未使用；一张快照也不能代表整个年份。
- 不把归档中的姓名、邮箱或旧组织自动归因给当前申请人。

## 三、当前注册、DNS 与基础设施

### 3.1 RDAP

优先通过 IANA RDAP DNS bootstrap 定位权威服务，再查询当前域名对象。记录：

- 域名句柄、当前状态、注册/最近更新/到期等事件及其事件名称。
- 注册商、权威名称服务器、DNSSEC、公开 notices/remarks。
- 被隐去或未返回的字段，以及查询时间。

限制：

- RDAP 是当前注册数据，不是完整 WHOIS 历史；公开数据会因法律、注册局和注册商政策而不同。
- `registration` 日期可能反映当前注册生命周期，不能单独证明首次注册、首次建站或最近易主时间。
- 隐私/代理保护本身不是 AdSense 违规，也不是自动风险分。
- 不在报告中复制与任务无关的个人联系数据。

### 3.2 DNS、TLS 和跳转

检查裸域与 `www` 的 A/AAAA/CNAME 结果、权威 DNS、HTTPS 证书有效期和名称覆盖、HTTP→HTTPS、`www`↔裸域规范化、跨域终点及重定向循环。

以下现象需要深入，而不是自动定罪：

- RDAP/DNS/证书/页面品牌在短期内同时变化，可能代表迁移或易主。
- 首页正常但旧子域、随机路径、移动端或特定来源跳到其他域。
- HTTP、HTTPS、`www` 和裸域展示不同业务。

## 四、旧 URL、索引和安全残留

### 4.1 旧路径发现

从历史快照 URL、旧 sitemap、Google `site:` 查询、Search Console 页面索引报告、服务器日志和外链报告建立旧 URL 样本。重点查：

- 成人、赌博、药品、贷款、破解、流媒体、下载、优惠券、外语关键词等与当前主题无关的路径。
- `/wp-content/`、上传目录、站内搜索、用户资料、论坛、API 参数页和旧子域中的注入页。
- 批量 200 空页、软 404、无限参数组合、被索引搜索页、旧内容全部跳首页。
- 仍返回 200 的旧品牌/旧业务、跨域跳转、恶意 JavaScript、iframe、自动下载或通知诱导。

不要只看搜索摘要。打开代表 URL，比较普通浏览器、移动端和必要的 User-Agent/Referrer 条件；可疑跳转应保存完整重定向链。

### 4.2 Google 安全和后台证据

公开检查 Google Safe Browsing Transparency Report 的 Site Status。若用户有 Search Console，要求查看：

- **Security issues**：被黑内容、恶意软件、社会工程、异常下载等。
- **Manual actions**：处置类型、影响范围、历史消息和复议状态。
- **Pages/URL Inspection**：Google 所见内容、索引状态、规范 URL、抓取障碍。
- **Links/Performance**：突然出现的无关落地页、异常查询、旧垃圾外链和流量尖峰。

公开 Safe Browsing 无警告不等于网站绝对安全；Search Console 无手动处置也不证明不存在算法评价、AdSense 政策问题或低价值问题。

### 4.3 清理标准

- 移除注入内容、后门和恶意代码，修补入口并轮换凭据。
- 对无替代内容的旧 URL 返回 404/410；有明确新对应页才做一对一 301，避免全部跳首页。
- 删除或修复旧 sitemap、内部链接、canonical、hreflang 和站内搜索暴露。
- 统一裸域/`www`/HTTP/HTTPS 和主要模板；复验不同设备与来源。
- 在 Search Console 复验安全问题/手动处置并按官方流程请求审核；不要仅靠临时删除 URL 工具掩盖内容。

## 五、过期域名滥用与用途切换

Google 将“购买并重新利用过期域名，主要为了操纵搜索排名，同时承载对用户几乎没有价值的内容”定义为 expired domain abuse。

只有同时有证据支持下列核心要素时，才报告该违规：

1. 域名经历过期/重新注册或有可信的二手收购证据；
2. 新用途明显在利用旧域名既有排名/声誉信号；
3. 当前承载内容主要用于操纵排名，并且对用户几乎没有价值。

以下情况不能单独定为过期域名滥用：

- 域名历史很长、最近才登记、换过行业、从别人手里买来、旧外链很多或使用隐私保护。
- 在旧域名上建立真实、独立、有价值的新业务。
- 页面上合理说明品牌迁移或业务转型。

但用途突变可以触发进一步抽样，尤其是旧政府/学校/医疗/公益站转为赌场、药品、贷款或薄联盟内容时。Publisher Policies 明确禁止在违反 Google 网页搜索垃圾政策的页面上放 Google 广告，因此已证实的过期域名滥用属于 AdSense 阻塞证据。

## 六、完整阻塞项登记表

每次完整审计必须逐行给状态，不得只列发现的问题。

| 通道 | 可能阻塞或高风险因素 | 公开面能否确认 |
|---|---|---|
| 账户资格 | 未满 18 岁、重复账户、被终止后另开账户、虚假/不完整信息、不支持语言、制裁限制 | 通常不能；用户/后台确认 |
| 域名所有权 | 无法控制 HTML/验证、提交错域名、站点未加入 Sites、验证信号不匹配 | 部分；最终看 AdSense |
| 上线与抓取 | 域名/DNS 故障、404/5xx、登录墙、robots、WAF/CDN、地域/IP 阻断、无效 TLS、重定向循环 | 多数可抽查，后台补证 |
| 域名历史 | 已证实过期域名滥用、旧垃圾路径仍在线、被黑内容、伪装/恶意跳转、不同主机展示冲突业务 | 部分；后台更强 |
| 安全信誉 | Safe Browsing 警告、Search Console 安全问题、恶意/不受欢迎软件、社会工程、滥用体验 | 公开 + 后台 |
| 搜索垃圾 | 规模化低价值、抓取、门页、薄联盟、关键词/隐藏文本、链接垃圾、站点声誉滥用、UGC 垃圾 | 需全站抽样 |
| 内容价值 | 内容不足以理解主题、无独特增量、模板/占位/建设中、广告或推广多于发布者内容 | 可抽样；无机械阈值 |
| 内容政策 | 非法、侵权/仿冒、危险贬损、欺骗/冒充、不诚实行为、色情及儿童危害等禁止类别 | 需逐页与场景审查 |
| 用户体验 | 导航失效、死链、误导按钮、意外跳转、弹窗遮挡、强制下载、移动端不可用 | 可人工检查 |
| 流量 | 自点、诱导、机器人、点击交换、垃圾邮件、恶意软件或低质购买流量 | 公开通常不能确认 |
| 广告实现 | 代码缺失/放错域、广告伪装内容、误触布局、不适当页面、ads.txt 错误授权 | 部分可确认 |
| 隐私与同意 | 隐私披露缺失、向 Google 传 PII、精确位置/儿童处理错误、适用地区无合规 CMP/同意 | 部分；需地区测试 |
| 限制内容 | Publisher Restrictions 类别可能无广告需求；不要等同禁止内容 | 可识别内容，需求未知 |
| 后台状态 | Policy Center 未解决、Sites 非 Ready、抓取错误、手动处置/安全问题未清、审核仍待处理 | 只能由用户提供 |

“所有阻塞因素”指当前官方框架下的完整审查通道，不代表公开审计能看到 Google 内部信号。无法验证的行必须保留为未知，而不是省略。

## 七、判级规则

- `P0 硬性阻塞`：当前可复现的明确政策违规、站点不可达、所有权无法验证、后台明确未解决问题。
- `P1 高拒审风险`：明显低价值、用途切换后残留大量垃圾、历史与当前主题严重混杂、关键体验不完整，但没有公开机械阈值。
- `P2 条件项`：账户、流量、地区同意、Search Console/AdSense 后台等需用户证据，或只在特定业务/地区适用。
- `P3 优化项`：有助于清晰度、信任和可维护性，但不是普遍审核门槛。

域名历史本身不设风险分。每个历史事实必须映射到当前官方要求或现场风险后再判级。

## 八、复验与输出模板

### 8.1 域名前身用途时间线

| 时间/区间 | 证据来源 | 当时用途与标题 | 变化 | 置信度 | 当前影响 |
|---|---|---|---|---|---|
| 无可靠证据时 | 写明查询过的来源 | 无法核实 | 不推断 | 低 | 作为覆盖限制 |

### 8.2 阻塞项登记

状态只能使用：`已证实阻塞`、`高风险`、`条件项`、`未发现`、`无法从公开面核实`、`不适用`。

每行包含：`通道 | 状态 | 证据 | 官方映射 | 修复 | 复验`。把“未发现”限定为已检查的 URL、设备、地区和日期。

### 8.3 送审前最后复验

1. 重新抓取所有 P0/P1 URL、旧高风险路径、裸域/`www`/HTTP/HTTPS。
2. 在 Search Console 复验 Security issues、Manual actions、URL Inspection 和旧垃圾查询。
3. 在 AdSense 复验所有权连接、Sites 状态、Policy Center 与拒审原文。
4. 用真实移动设备或浏览器复验同意、导航、弹窗、下载和广告预留位。
5. 记录复验日期；不要用一次快照承诺后续一定获批。

## 九、来源索引

- [Google Publisher Policies](https://support.google.com/publisherpolicies/answer/10502938?hl=en)
- [Spam Policies for Google Web Search](https://developers.google.com/search/docs/essentials/spam-policies)
- [Manual actions report](https://support.google.com/webmasters/answer/9044175?hl=en)
- [Google Safe Browsing Site Status](https://transparencyreport.google.com/safe-browsing/search)
- [What to do when your site is not ready to show ads](https://support.google.com/adsense/answer/12176698?hl=en)
- [Fix AdSense crawler issues](https://support.google.com/adsense/answer/2381908?hl=en)
- [AdSense site management](https://support.google.com/adsense/answer/12131223?hl=en)
- [ICANN Lookup FAQ](https://lookup.icann.org/en/faq)
- [IANA RDAP DNS Bootstrap Registry](https://www.iana.org/assignments/rdap-dns/rdap-dns.xhtml)
- [IANA Example Domains](https://www.iana.org/help/example-domains)
- [IANA Special-Use Domain Names](https://www.iana.org/assignments/special-use-domain-names/special-use-domain-names.xhtml)
- [Wayback Machine General Information](https://archivesupport.zendesk.com/hc/en-us/articles/360004716091-Wayback-Machine-General-Information)
- [Using the Wayback Machine](https://archivesupport.zendesk.com/hc/en-us/articles/360004651732-Using-The-Wayback-Machine)

引用最接近发现的原文。Internet Archive、ICANN/IANA 负责历史和登记事实；只有 Google 来源可作为 Google 广告/搜索政策依据。
