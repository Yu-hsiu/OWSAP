# API2:2023 — 認證失效(Broken Authentication)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-16),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

認證流程的任何弱點。這裡示範最經典的一種:密碼重置的驗證碼端點**不限制猜錯
次數**,攻擊者可以無限嘗試,把整個驗證碼空間枚舉一遍必定猜中,接管任何帳號。
對應技能筆記的「6 位數驗證碼 + 無限次請求 → 100 萬次猜中」案例。

## 這個專案怎麼示範

密碼重置流程兩個端點:`POST /api/reset/request`(產生驗證碼)、
`POST /api/reset/verify`(用驗證碼重設密碼):

- **vulnerable_app.py**:verify 端點對同一 email 猜錯次數無限制 → 可暴力枚舉。
- **secure_app.py**:每個 email 猜錯達上限(5 次)即鎖定回 429 → 枚舉被擋。
- **attack.py**:觸發重置後,從 000 枚舉到 999 嘗試猜中並改密碼。
- **run_demo.py**:一鍵起兩版、跑同一支暴力破解,印出前後對照。
- **auth_db.py**:共用假帳號與驗證碼工具。

> **關於驗證碼長度**:真實世界是 6 位數(10^6),本 demo 壓成 **3 位數(1000)**
> 純粹為了讓暴力破解在幾秒內跑完。漏洞本質(缺速率限制/鎖定 → 可枚舉)與位數
> 無關;位數只影響要送幾次請求。

攻防核心對照(vulnerable → secure 只差這段鎖定邏輯):

```python
# secure_app.py:達失敗上限即鎖定,阻斷暴力枚舉
if failed_attempts.get(email, 0) >= MAX_VERIFY_ATTEMPTS:
    return jsonify({"error": "too many attempts, locked"}), 429
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
# 上傳本資料夾的 5 個 .py 到工作目錄,或 git clone 後 cd 進來
!python run_demo.py
```

## 驗證結果(2026-07-16 本機實跑)

```
[1] 有漏洞版:[漏洞成立] 帳號接管!第 481 次猜中驗證碼 480,密碼已被改成攻擊者的
[2] 修補後版:[已防禦] 第 6 次嘗試即被鎖定(429),暴力破解被擋下
```
(猜中的次數每次會不同,因為驗證碼是密碼學隨機產生。)

## 對應的防禦重點(來自技能筆記)

- 認證端點加速率限制、帳號鎖定、CAPTCHA、多因素認證(MFA)。
- 不自幹認證/令牌/密碼儲存,使用成熟的安全標準。
- 變更密碼/email/MFA 等敏感動作要求重新驗證身分。

## 可延伸(想深入時)

- 把單純鎖定換成指數退避 + 驗證碼有效期(過期即失效),更貼近真實防禦。
- 加一個 6 位數 + 速率限制的版本,示範「即使碼夠長,沒有速率限制仍可被跑」與
  「有速率限制後,長碼才真正有意義」的關係。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-16。</sub>
