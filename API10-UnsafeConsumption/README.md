# API10:2023 — 不安全地取用 API(Unsafe Consumption of APIs)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-20),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

前九項多在講「API 提供者」怎麼被打;這一項視角在「**取用者**」。開發者容易過度
信任第三方 API 回來的資料,不像對待使用者輸入那樣驗證與淨化。一旦第三方被入侵
或走未加密通道被 MITM,回傳的惡意資料就會流進我方系統造成損害。對應技能筆記
的「過度信任第三方數據」案例。

## 這個專案怎麼示範

結帳流程向「第三方折扣服務」取得折扣百分比,再據以計算最終金額:

- **third_party_api.py**:模擬**已被攻擊者控制**的第三方,回傳荒謬折扣(100000%)。
- **vulnerable_app.py**:`POST /api/checkout` 拿到折扣後**未驗證**就套進計算 →
  最終金額變成負數(店家倒貼)。
- **secure_app.py**:把第三方折扣當使用者輸入驗證(型別 + 0–100 範圍),不合理
  就拒用(視為無折扣)。
- **attack.py**:觸發一次結帳,檢查最終金額是否被污染成負數。
- **run_demo.py**:一鍵起第三方 + 兩版 app、跑同一支攻擊,印出前後對照。
- **consumption_common.py**:共用的第三方 URL 與驗證範圍設定。

攻防核心對照:

```python
# vulnerable:未驗證第三方折扣就直接使用
discount_percent = resp.json()["discount_percent"]
final_price = base_price * (1 - discount_percent / 100)

# secure:把第三方資料當使用者輸入驗證,不合理就拒用
discount_percent = sanitize_discount(resp.json().get("discount_percent"))  # 非 0–100 一律回 0
```

## 怎麼跑

**本機**:
```bash
pip install flask requests
python run_demo.py
```

**Colab**(展示用):
```python
!pip -q install flask requests
# 上傳本資料夾的 6 個 .py 到工作目錄,或 git clone 後 cd 進來
!python run_demo.py
```

## 驗證結果(2026-07-20 本機實跑)

```
[1] 有漏洞版:[漏洞成立] 最終金額被算成 -99900.0(原價 100),店家反而倒貼給攻擊者
[2] 修補後版:[已防禦] 最終金額 100.0 維持正常(第三方惡意值被拒用),攻擊失敗
```

## 對應的防禦重點(來自技能筆記)

- 把第三方資料視為與使用者輸入同等風險,使用前務必驗證與淨化。
- 評估服務供應商時審查其 API 安全狀態,並確保所有互動均透過加密通道。
- 維護已知且安全的重導向清單,不要盲從第三方 API 的重導向指令。

## 這一項的心態轉變:信任邊界

多數驗證只做在「使用者 → 我」這條邊界,卻默認「第三方 → 我」是可信的。但你的
安全等於你信任鏈上最弱的一環——第三方被入侵,你就被入侵。把每一個外部資料來源
(使用者、合作夥伴 API、上游服務)都放進同一套驗證標準,才是穩健的做法。

## 可延伸(想深入時)

- 換一種惡意 payload:第三方回傳一段含 HTML/JS 的字串,示範未淨化就渲染造成的
  XSS 類問題(注入面向)。
- 示範第三方回傳惡意重導向 URL,取用者盲從 → 對應「維護安全重導向清單」防線
  (與 API7 SSRF 的白名單思路呼應)。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-20。</sub>
