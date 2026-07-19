# API8:2023 — 安全設定錯誤(Security Misconfiguration)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-20),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

安全設定錯誤是個「大雜燴」類別,涵蓋各種主機 / 應用層的錯誤設定:錯誤標頭、預設
帳號、開放不必要的 HTTP 方法、缺輸入淨化、**詳細的錯誤訊息**等。本專案挑其中最好
演、也最常見的一種:**把完整例外堆疊(traceback)回給用戶端**。堆疊裡的伺服器檔案
路徑、目錄結構、框架與例外型別,全成了攻擊者偵察系統的線索。

## 這個專案怎麼示範

一個會因輸入而觸發例外的端點 `GET /api/divide?a=&b=`(b=0 觸發 ZeroDivisionError):

- **vulnerable_app.py**:例外發生時把 `traceback.format_exc()` 直接回給用戶端。
- **secure_app.py**:例外只記在伺服器端日誌(`app.logger.error(..., exc_info=True)`),
  對外一律回統一的 `{"error": "internal server error"}`。
- **attack.py**:送 `a=10&b=0` 觸發例外,檢查回應有沒有洩漏堆疊。
- **run_demo.py**:一鍵起兩版、跑同一支攻擊,印出前後對照。

攻防核心對照:

```python
# vulnerable:把完整 traceback 回給用戶端
return jsonify({"error": "internal error", "traceback": traceback.format_exc()}), 500

# secure:細節記伺服器端,對外只回一般訊息
app.logger.error("divide 發生例外", exc_info=True)
return jsonify({"error": "internal server error"}), 500
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
# 上傳本資料夾的 4 個 .py 到工作目錄,或 git clone 後 cd 進來
!python run_demo.py
```

## 驗證結果(2026-07-20 本機實跑)

```
[1] 有漏洞版:[漏洞成立] 回應洩漏完整堆疊,例如:File ".../API8-Misconfiguration/vulnerable_app.py", line 22, in divide
[2] 修補後版:[已防禦] 只回一般錯誤訊息,未洩漏堆疊(status=500)
```
漏洞版連伺服器**完整檔案路徑**(含目錄結構、使用者名稱)都露了出來——這正是攻擊者
拿來繪製系統地圖、找下一個突破口的情報。

## 對應的防禦重點(來自技能筆記)

- 強制 API 回應(含錯誤回應)符合 schema,防止洩漏例外堆疊等系統細節。
- 可重複的環境硬化流程 + 自動化持續評估設定(關 debug、限制 HTTP 方法、移除
  預設帳號、全程加密)。
- 錯誤細節記在伺服器端日誌供除錯,絕不回給用戶端。

## 這一項的「大雜燴」還有哪些面向(本 demo 只演其一)

安全設定錯誤還包括:開著 debug 模式、開放不必要的 HTTP 動詞(如未擋 `TRACE`/
`PUT`)、使用預設帳密、缺 CORS / 安全標頭、目錄列表開啟等。本 demo 聚焦「錯誤
訊息洩漏」,其餘面向可作為延伸。

## 可延伸(想深入時)

- 加一個「只允許白名單 HTTP 方法、其餘回 405」的示範,對應「限制不必要的動詞」。
- 加安全標頭(如關閉 `Server` 版本標頭、加 `X-Content-Type-Options`),對應標頭
  硬化。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-20。</sub>
