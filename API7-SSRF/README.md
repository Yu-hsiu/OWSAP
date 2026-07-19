# API7:2023 — 伺服器端請求偽造(SSRF)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-20),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

當使用者能控制「伺服器要去抓的遠端資源」時,就可能發生 SSRF。攻擊者把 URL 換成
指向**內部服務**(伺服器碰得到、但攻擊者直接碰不到的位址,如雲端 metadata、內網
後台、localhost 檔案),借伺服器之手讀出內部機密。對應技能筆記的「更新庫存請求
裡帶 URL,被換成指向 localhost 密檔」案例。

## 這個專案怎麼示範

一個「幫你抓取遠端資源」的端點 `POST /api/fetch {url}`,加一個模擬的內部服務:

- **internal_service.py**:SSRF 的攻擊目標,回傳假雲端憑證。代表攻擊者碰不到、
  但 app 伺服器碰得到的內網資源。
- **vulnerable_app.py**:直接拿使用者的 URL 去 `urlopen`,不做任何驗證。
- **secure_app.py**:抓取前先驗證——限定 scheme(http/https)、主機必須在白名單
  (`ALLOWED_HOSTS`),內部 / localhost / 私有位址一律擋下。
- **attack.py**:把內部服務的 URL 塞進抓取端點,檢查回應裡有沒有內部憑證。
- **run_demo.py**:一鍵起內部服務 + 兩版 app、跑同一支攻擊,印出前後對照。
- **ssrf_common.py**:共用的假憑證與白名單設定。

攻防核心對照:

```python
# vulnerable:直接抓,不驗證目標
with urlopen(url, timeout=FETCH_TIMEOUT_SECONDS) as resp:
    body = resp.read()...

# secure:抓取前先過 scheme + 主機白名單
if parsed.scheme not in ALLOWED_SCHEMES: ...       # 只允許 http/https
if parsed.hostname not in ALLOWED_HOSTS: 403       # 內部 / localhost 不在白名單
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
[1] 有漏洞版:[漏洞成立] SSRF 成功!借伺服器讀到內部服務 .../metadata 的憑證(s3cr3t-internal-metadata-key)
[2] 修補後版:[已防禦] 被 403 擋下,白名單拒絕抓取內部主機
```

## 對應的防禦重點(來自技能筆記)

- 對來源、URL scheme、連接埠、媒體類型實施允許清單(allow list)。
- 隔離負責抓取資源的機制、停用 HTTP 重導向。
- 用經過測試、維護良好的 URL 解析器,並淨化所有用戶端輸入。

## 為什麼「白名單」比「黑名單」可靠

擋 SSRF 若用黑名單(例如「禁止 127.0.0.1」),攻擊者有一堆繞法:`localhost`、
`0.0.0.0`、`2130706433`(十進位 IP)、`[::1]`、DNS rebinding、重導向……黑名單
很難列全。**白名單**反過來只放行已知安全的目標,預設拒絕其餘,面對這些繞法穩健
得多。本 demo 用主機白名單;正式版還應在解析 DNS 後再確認 IP 不落在私有 / 保留
範圍,並停用重導向。

## 可延伸(想深入時)

- 加一個「解析 DNS → 檢查 IP 是否為私有 / 迴圈 / 保留範圍」的檢查,示範防 DNS
  rebinding 與十進位 IP 繞法。
- 在 attack.py 加幾個繞法變體(`http://localhost`、十進位 IP),示範黑名單為何
  容易被繞、白名單為何擋得住。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-20。</sub>
