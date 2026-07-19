# API1:2023 — 物件層級授權失效(BOLA)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-16),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

API 只檢查「你有沒有登入」(認證),卻沒檢查「你要拿的這筆資料是不是你的」
(物件層級授權)。攻擊者換掉請求裡的資源 id,就能讀到別人的資料。對應技能筆記
的 Bruce/Harvey Dent 醫院案例。

## 這個專案怎麼示範

一個 `GET /api/users/<id>` 端點,回傳含敏感欄位 `ssn` 的使用者記錄:

- **vulnerable_app.py**:登入即可讀任何 id → BOLA 成立。
- **secure_app.py**:加擁有者授權檢查(`requester_id != user_id` → 403)→ 擋下。
- **attack.py**:以 Alice(id=1)身分去讀 Bob(id=2)的資料,靠回應差異判定漏洞。
- **run_demo.py**:一鍵起兩版、跑同一支攻擊,印出前後對照。
- **users_db.py**:共用假資料與令牌對照(記憶體內,重啟還原)。

攻防核心對照(vulnerable → secure 只差這段擁有者檢查):

```python
# secure_app.py:存取物件前先驗證擁有者
if requester_id != user_id:
    return jsonify({"error": "forbidden"}), 403
```

## 怎麼跑

**本機**:
```bash
pip install flask requests
python run_demo.py
```

**Colab**(展示用):新增一個 cell 貼上並執行——
```python
!pip -q install flask requests
# 把本資料夾的 5 個 .py 上傳到 Colab 工作目錄(或 git clone 後 cd 進來)
!python run_demo.py
```
`run_demo.py` 用背景執行緒起 Flask、同進程用 requests 打 localhost,不需對外
連接埠,適合 Colab。預期輸出:漏洞版讀到 Bob 的 ssn,修補版被 403 擋下。

## 驗證結果(2026-07-16 本機實跑)

```
[1] 攻擊『有漏洞』版本:[漏洞成立] 越權成功!讀到 Bob 的 ssn = B987654321
[2] 攻擊『修補後』版本:[已防禦] 越權被擋(status=403),授權檢查生效
```

## 對應的防禦重點(來自技能筆記)

- 每個用用戶端輸入去查資料庫的函數都要做授權檢查(RBAC + 使用者原則)。
- 資源 id 改用不可預測的 GUID/UUID,增加枚舉難度(本 demo 用連號 id 是為了
  凸顯漏洞;正式版應改 UUID)。
- 寫專門測授權的自動化測試,測試沒過就不部署。

## 可延伸(想深入時)

- 把 id 換成 UUID,示範「不可預測 id」如何降低枚舉風險(但不能取代授權檢查)。
- 加一個 pytest,把 attack.py 的判定包成「漏洞版應洩漏、修補版應 403」的斷言,
  對應「授權自動化測試」那條防禦。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-16。</sub>
