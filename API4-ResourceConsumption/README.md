# API4:2023 — 資源消耗不受限(Unrestricted Resource Consumption)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-19),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

API 缺乏防止過度使用的保護。本專案示範最直接的一種:分頁查詢端點直接採信用戶端
的 `limit`,沒有上限。攻擊者送一個超大的 `limit`,伺服器就一次組出巨量回應,吃光
記憶體/CPU/頻寬,造成阻斷服務(DoS)或推高雲端成本。對應技能筆記的「沒限制單一
請求回傳的記錄數量」案例。

## 這個專案怎麼示範

一個查詢端點 `GET /api/records?limit=N`,背後是百萬筆的資料集:

- **vulnerable_app.py**:`limit` 完全由用戶端決定,沒有上限。
- **secure_app.py**:對 `limit` 做伺服器端驗證並套用硬上限(`MAX_LIMIT=100`),
  要求再多也只給到上限。
- **attack.py**:要求 `limit=100000`,量測實際回傳的筆數與 payload 大小。
- **run_demo.py**:一鍵起兩版、跑同一支攻擊,印出前後對照。
- **records_db.py**:共用假資料集(查詢時才切片產生,不預先實體化)。

攻防核心對照:

```python
# vulnerable:limit 無上限,用戶端要多少給多少
limit = int(request.args.get("limit", DEFAULT_LIMIT))

# secure:套用硬上限,超過就夾到 MAX_LIMIT
effective_limit = min(requested, MAX_LIMIT)
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
[1] 有漏洞版:[漏洞成立] 要求 100,000 筆、實得 100,000 筆(約 8.5 MB),伺服器毫無節制
[2] 修補後版:[已防禦] 要求 100,000 筆、只給 100 筆(約 0.01 MB),上限生效
```
(demo 取 10 萬筆兼顧速度與說服力;真實攻擊會送更大值直到伺服器崩潰或帳單暴增。)

## 對應的防禦重點(來自技能筆記)

- 伺服器端驗證查詢字串與 body 參數,特別是控制回傳筆數的參數;限制所有輸入的
  大小上限(字串長度、陣列元素數)。
- 對呼叫次數做速率限制;用 Docker 等限制記憶體/CPU/程序數。
- 為執行時間、可分配記憶體、第三方服務花費設定上限。

## 可延伸(想深入時)

- 加一層「每分鐘請求數」的速率限制(如 flask-limiter),示範參數上限之外的另一
  道防線。
- 用 Docker 對容器設記憶體上限,示範即使應用層漏了,基礎設施層仍能兜底。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-19。</sub>
