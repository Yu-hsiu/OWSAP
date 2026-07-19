# API6:2023 — 敏感業務流程存取不受限(Unrestricted Access to Sensitive Business Flows)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-19),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

這一項的特別之處:漏洞不在單一技術缺陷,而在**業務流程被自動化濫用**。攻擊者
辨識出一個有價值的流程(限量商品購買),用機器人大量、快速地執行它,對業務造成
損害。本專案示範最經典的場景:黃牛(scalper)用一支腳本在瞬間把 PS5 庫存整批
掃空,一般人根本買不到。對應技能筆記的「PS5 搶購機器人」案例。

## 這個專案怎麼示範

一個限量購買端點 `POST /api/purchase`,庫存 10 台:

- **vulnerable_app.py**:只檢查登入與庫存,沒有每人限購 / 速率限制 / 真人檢測 →
  單一帳號的機器人可掃空全部庫存。
- **secure_app.py**:每個帳號限購上限(`MAX_PER_USER=1`),超過回 429。
- **attack.py**:用黃牛帳號迴圈狂刷購買,統計掃走幾台。
- **run_demo.py**:一鍵起兩版、跑同一支掃貨腳本,印出前後對照。
- **inventory_db.py**:共用庫存與令牌工具。

攻防核心對照:

```python
# vulnerable:只看有沒有庫存,不看是誰買了幾次
if stock[ITEM_NAME] <= 0:
    return jsonify({"error": "sold out"}), 409

# secure:每人限購,阻斷單一帳號 / 機器人掃貨
if purchased_by.get(buyer, 0) >= MAX_PER_USER:
    return jsonify({"error": f"每人限購 {MAX_PER_USER} 台"}), 429
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

## 驗證結果(2026-07-19 本機實跑)

```
[1] 有漏洞版:[漏洞成立] 黃牛用一個帳號掃走 10/10 台,庫存被清空,一般人買不到
[2] 修補後版:[已防禦] 黃牛只買到 1 台(每人限購生效),庫存留給其他人
```

## 對應的防禦重點(來自技能筆記)

- 業務層先識別可能被濫用的流程,工程層再選保護機制(裝置指紋、CAPTCHA / 生物
  辨識做真人檢測、分析非人類操作模式)。
- 必要時封鎖 Tor 出口節點與已知代理伺服器的 IP。
- 本 demo 用「每人限購」示範最直接的一道防線;真實世界會多層疊加。

## 這一項和「速率限制」有什麼不同?

API4(資源消耗)靠速率限制擋「請求太多」;API6 擋的是「**合法請求被拿去濫用
業務邏輯**」。即使每個請求都合規、速率也不算高,只要一個帳號能買走遠超公平份額
的限量商品,業務照樣受害——所以要的是**業務層級**的限制(每人限購、真人檢測),
不只是技術層級的節流。

## 可延伸(想深入時)

- 加一個簡單的「非人類模式偵測」:若同一 IP / 帳號在極短時間內請求數暴衝就標記,
  示範真人檢測那一層。
- 讓限購以「不同帳號但同裝置指紋」也會被綁在一起,示範黃牛換帳號也擋得住。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-19。</sub>
