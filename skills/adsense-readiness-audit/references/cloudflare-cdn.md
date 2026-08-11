# Cloudflare/CDN 与 AdSense 可达性审查

本参考用于审查由 Cloudflare 代理、托管或保护的站点。最后在线核对日期：**2026-08-12**。

## 目录

1. 判定边界
2. 公开面检测
3. Cloudflare 配置面检查
4. 故障与判级矩阵
5. 修复和复验
6. 官方来源

## 一、判定边界

- 使用 Cloudflare、橙云代理、Cloudflare Pages、Workers 或 Cloudflare DNS 本身不是 AdSense 风险。
- Google 要求站点已上线、可连接、可验证，并允许相关抓取工具访问。只有 Cloudflare/CDN 配置造成了不可达、挑战、错误内容、验证失败、重定向、TLS 或实际脚本故障时，才映射为阻塞。
- `Mediapartners-Google` 用于广告内容抓取；`Google-Display-Ads-Bot` 还会在添加站点时参与验证。二者与 Google 搜索抓取不是同一个检查面。
- 不用伪造 Google User-Agent 的单次请求证明真实 Google 爬虫一定被允许或拦截。Cloudflare 可能结合 IP、反向 DNS、签名和行为识别 Verified Bots；优先使用 AdSense 抓取报告、Cloudflare Security Events/Logs 和源站日志中的真实请求。
- 不要求特定 Cloudflare 套餐、是否开启代理或固定 SSL/TLS 模式。判定公开结果和实际抓取结果，不把服务商最佳实践冒充 Google 审核规则。

## 二、公开面检测

先运行：

```bash
python scripts/site_probe.py https://example.com --max-pages 30 --format markdown
```

脚本会记录选定响应头，并检查：

- `Server: cloudflare`、`CF-Ray`、`CF-Cache-Status` 等 Cloudflare 线索；缺少这些头不能证明未使用 Cloudflare，域名可能只使用其 DNS、采用部分代理或隐藏/改写响应头。
- `CF-Mitigated: challenge`。Cloudflare 将该响应头定义为 Challenge Page 的可靠响应信号。
- Cloudflare `520`–`526` 响应，以及受影响 URL。
- 首页、`robots.txt` 和 `ads.txt` 的响应状态与 Cloudflare 信号。
- `Mediapartners-Google` 和 `Google-Display-Ads-Bot` 在 `robots.txt` 中的近似可抓取结果。
- CSP、缓存状态、AdSense 脚本信号、HTTP→HTTPS 和最终 URL。

再人工覆盖：

1. 裸域和 `www` 的 HTTP/HTTPS 组合。
2. 首页、代表性内容页、隐私页、`robots.txt`、`ads.txt` 和放置 AdSense 验证代码的页面。
3. 桌面与移动端；若业务有地域规则，覆盖主要服务地区。
4. 普通访问、无 Cookie 新会话，以及用户实际可复现的挑战或错误路径。
5. 记录时间、URL、状态码、最终 URL、`CF-Ray`、可见页面类型和响应头。不要把自定义错误页上的文案当成唯一依据。

## 三、Cloudflare 配置面检查

公开信号不足时，请用户提供只读截图或导出，不代替用户修改生产规则：

- **DNS**：zone 是否 Active；权威名称服务器是否生效；裸域/`www` 的 A、AAAA、CNAME 是否指向当前源站或 Pages/Workers 项目；是否残留旧源站和错误 IPv6。
- **源站健康**：Cloudflare 是否能连接源站；源站防火墙是否错误阻止 Cloudflare IP；是否有超时、过载、端口或 Authenticated Origin Pull 配置冲突。
- **SSL/TLS 与重定向**：Encryption mode、Edge Certificates、Always Use HTTPS、HSTS、Redirect Rules、Page Rules 和源站跳转是否形成循环；公众看到的证书是否有效。
- **WAF/Bots**：Security Events 中是否有对真实 `Mediapartners-Google`、`Google-Display-Ads-Bot` 或相关 Google 抓取的 Block、Managed Challenge、JS Challenge、Rate Limit；检查 Bot Fight Mode、Super Bot Fight Mode、custom rules 和 exceptions。
- **Access/地域/IP**：Cloudflare Access、country/IP/ASN 规则、浏览器完整性检查和 Under Attack 行为是否把公开内容变成登录或挑战页面。
- **Workers/规则**：Workers、Snippets、Transform Rules、URL Rewrites、Redirects 是否按主机、路径、地区、设备、来源或 User-Agent 返回不同业务、跨域跳转或错误状态。
- **缓存**：Cache Rules、Cache Everything、Bypass、Browser Cache、旧部署缓存是否让 Google 看到占位页、旧站、缺少验证代码的 HTML、过期 `robots.txt` 或 `ads.txt`。
- **前端变换**：Rocket Loader、Zaraz、响应头 Transform Rules 和 CSP 是否实际阻止或延迟 AdSense/验证脚本。只有浏览器控制台、网络请求或 Google 连接失败能证实影响；仅开启功能不是问题。

## 四、故障与判级矩阵

| 现场证据 | AdSense 映射 | 建议判级 |
|---|---|---|
| DNS 不解析、错误源站、持续 `520`–`526`、TLS 失败或重定向循环 | 站点不可达/主机故障 | 当前可复现时 `P0` |
| 实际 Google 广告爬虫被 WAF、Bot、Access、地域/IP 或速率规则拦截/挑战 | 抓取或站点验证失败 | 后台/日志确认时 `P0` |
| 首页或验证页返回 `CF-Mitigated: challenge`，无法直接取得发布者内容 | 无密码公开访问和可抓取性不足 | 持续可复现时 `P0`；仅单一探测客户端时先 `P1/P2` 复核 |
| Workers/Redirect Rules 向审核路径返回错误域名、登录页、空白页或占位站 | URL、所有权、内容或体验冲突 | 当前可复现时 `P0` |
| 缓存持续提供旧站、旧垃圾内容或缺少账户连接信号的 HTML | 连接失败、历史残留或内容不一致 | 依结果为 `P0/P1` |
| `robots.txt` 明确禁止相关 Google 广告爬虫 | 抓取失败 | 当前规则确认时 `P0` |
| `ads.txt` 被挑战、错误重定向或不是根域 `200` | 授权库存抓取问题 | ads.txt 已使用时按实际错误登记；不要把未创建 ads.txt 单独定为 P0 |
| Rocket Loader/CSP/脚本变换仅“可能影响”，尚无故障证据 | 需要浏览器和后台复验 | `P2`，不能直接定罪 |
| 只有 Cloudflare 响应头、Cloudflare DNS 或橙云代理 | 无违规事实 | `未发现`，不是 P3 整改项 |

Cloudflare 错误码只说明技术故障类别，不自动证明故障长期存在。单次瞬时 `5xx` 要结合重复请求、不同时间/地区、Cloudflare Error Analytics、源站日志和 AdSense 抓取记录再判断持续性。

## 五、修复和复验

1. 先修 DNS、源站、TLS 和循环跳转，再处理抓取例外；不要用缓存或自定义错误页掩盖源站故障。
2. 根据 Security Events/Logs 定位命中的具体产品和规则。优先做最小范围的规则修复；不要无证据地关闭全部安全保护。
3. 若 Bot Fight Mode 本身造成已证实故障，注意该产品不能用普通 WAF custom rule 精细调整；按当前 Cloudflare 产品能力关闭或更换可配置方案，并复验。
4. 清理冲突的 Access、地域/IP、Rate Limiting、Workers 和 Redirect Rules，确保审核 URL 无需登录、验证码或 POST 数据即可返回完整内容。
5. 修复后清除相关缓存，重新请求首页、代表页、`robots.txt`、`ads.txt` 和验证页，保存新的 `CF-Ray` 和状态码。
6. 在 AdSense 的 Sites/连接状态和 crawler issues 中复验；在 Cloudflare Security Events/Logs 与源站日志中确认真实 Google 请求不再被拦。Google 抓取缓存更新可能滞后，不把公开脚本的一次成功当作后台已经恢复。

## 六、官方来源

Google 要求：

- [Fix AdSense crawler issues](https://support.google.com/adsense/answer/2381908?hl=en)
- [About the AdSense ads crawler](https://support.google.com/adsense/answer/99376?hl=en)
- [Connect your site to AdSense](https://support.google.com/adsense/answer/7584263?hl=en)
- [Give access to the AdSense crawler in robots.txt](https://support.google.com/adsense/answer/10532?hl=en)
- [Ensure ads.txt files can be crawled](https://support.google.com/adsense/answer/7679060?hl=en)

Cloudflare 实现事实：

- [Detect a Challenge Page response](https://developers.cloudflare.com/cloudflare-challenges/challenge-types/challenge-pages/detect-response/)
- [Cloudflare 5xx errors](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-5xx-errors/)
- [ERR_TOO_MANY_REDIRECTS](https://developers.cloudflare.com/ssl/troubleshooting/too-many-redirects/)
- [Bot Fight Mode](https://developers.cloudflare.com/bots/get-started/bot-fight-mode/)
- [Verified bots](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/)
- [Rocket Loader](https://developers.cloudflare.com/speed/optimization/content/rocket-loader/)
- [Content Security Policies and Cloudflare](https://developers.cloudflare.com/fundamentals/reference/policies-compliances/content-security-policies/)

只有 Google 来源定义 AdSense 要求；Cloudflare 来源用于解释响应信号和产品行为。
