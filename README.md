# OWASP API Security Lab — 逐項實作十大 API 弱點與防禦

> **對應技能筆記**:[`docs/owasp-api-security-top-10.md`](docs/owasp-api-security-top-10.md)
> **來源**:freeCodeCamp《OWASP API Security Top 10 Course》
> <https://www.youtube.com/watch?v=YYe0FdfdgDU>

> ⚠️ **安全警語**:本 repo 是**刻意設計成脆弱**的教學程式碼,用於學習 OWASP API
> Security Top 10 的攻防。**請勿部署到任何對外或正式環境**,只在本機 / Colab 執行。
>
> ✅ **目前進度**:**API1 ~ API10 十項全數完成**,每一項都含 vulnerable / secure /
> 攻擊腳本 / 一鍵展示,並在本機實跑通過(攻擊成功 → 修補 → 攻擊失敗)。

---

## 為什麼做這個專案

看的那門課是**概念課**——它把 OWASP API Security Top 10 講得很清楚,但全程沒有
帶觀眾動手攻擊或修補(影片自己也說,hands-on 的 API 滲透測試是另一門姊妹課)。
所以「以實作影片內容為目標」的正確詮釋是:**把課堂上聽懂的十項風險,親手變成可
以攻擊、也可以修補的東西**。聽懂 ≠ 會做;這個專案就是補上「會做」這一段,順便
產出可放進履歷、面試官能追問驗證的成果。

## 專案目標

打造一個**刻意脆弱的 API 靶場(vulnerable API)**,對 OWASP API Top 10 的每一項:

1. 在靶場裡實作出該漏洞(vulnerable 版本)。
2. 寫一段能重現攻擊的腳本或步驟,證明漏洞成立。
3. 提交一個修補(secure 版本),再跑一次攻擊證明已被擋下。

十項各自獨立、各自可驗證——**不是一次做完,而是十個小步,每步都有「攻擊成功 →
修補 → 攻擊失敗」的可展示證據**。

## 實作目標

此專案完成後,可佐證下列履歷技能(對應技能筆記的「習得能力總結」):

- 能辨識並利用 API 授權類漏洞(BOLA / BFLA / BOPLA),並實作 RBAC 與物件層級
  授權檢查加以修補。
- 能實作認證強化措施(速率限制、帳號鎖定、敏感操作重新驗證)防範暴力破解。
- 能設計並執行 API 攻擊腳本(如 IDOR 枚舉、批量賦值、SSRF),具備基本紅隊視角。
- 能建置具 CI 授權測試的安全開發流程(授權測試不過就不部署)。
- 熟悉 API 安全工具鏈(Burp Suite / OWASP ZAP)進行掃描與驗證。

> 目前這些尚未有成果支撐,**待專案各階段完成後才回填履歷**(遵循流水線的回饋
> 迴路,不預先寫入無成果支撐的技能)。

## 可行性評估與技術選型(誠實版)

- **可行性:高**。這是資安學習的標準路徑,有大量成熟的開源脆弱 API 靶場可直接
  參考或當骨架,不必從零造靶。**動手前先做研究與重用**(依開發工作流程):
  先用 GitHub 搜尋現成的 vulnerable API 專案(例如社群常用的 crAPI、VAmPI、
  DVGA 一類刻意脆弱 API),評估哪個涵蓋度最高、最適合當骨架,再決定是「直接用
  現成靶場練攻防」還是「自建最小靶場」。
- **學習價值:高**。親手寫出漏洞比只讀定義深刻得多,而且修補環節逼你理解防禦
  的真實成本。
- **與履歷對應:直接**。每一項都能對應一條可被面試追問的技能。
- **建議技術棧**:一個輕量 Web 框架(Python FastAPI/Flask 或 Node/Express 皆可,
  依熟悉度選)+ SQLite/JSON 資料層 + 攻擊腳本用 Python `requests` 或 Postman/
  Burp。環境為 Windows 11 + PowerShell,若用 Docker 做資源限制示範(API4)需
  先確認本機 Docker 可用。

## 建議 MVP(最小可行版本)

**十項風險 = 十個子專案**(2026-07-16 決定)。本 lab 是傘專案,底下每一項 OWASP
API 風險各開一個子資料夾,自帶 README + 可執行程式碼,獨立完成一次「vulnerable →
攻擊腳本 → secure」攻防閉環。依使用者要求**一項一項規劃與開發**,不一次爆量。

- **技術棧**:Python + Flask(vulnerable/secure app)+ requests(攻擊腳本)。
- **執行環境**:**Colab 優先**。每個子專案提供 `run_demo.py`——用背景執行緒起
  Flask、同進程用 requests 打 localhost,一鍵演示攻擊前後差異,可直接在 Colab
  以 `!python run_demo.py` 或貼成單一 cell 執行展示。本機亦可跑。
- **子專案資料夾命名**:`API<n>-<簡稱>/`(例:`API1-BOLA/`)。

## 目前狀態

- 技能筆記與複習材料(quiz、study-guide)已就緒。
- **API1–API10 十項全數完成**(BOLA、BrokenAuth、BOPLA、ResourceConsumption、BFLA、BusinessFlows、SSRF、Misconfiguration、InventoryMgmt、UnsafeConsumption,皆本機實跑通過)。

## 下一步

1. 完成 API1-BOLA 子專案(README + Flask 靶場 + 攻擊腳本 + Colab 展示),
   確認能在 Colab 跑出「攻擊成功 → 修補 → 攻擊失敗」。
2. 以 API1 為樣板,依序展開 API2 … API10(每項一輪,經使用者確認再進下一項)。
3. 每完成一項,回本表更新狀態,並評估是否回填資安履歷。

## 進度追蹤表

| 項目 | 子資料夾 | vulnerable | 攻擊腳本 | secure 修補 | Colab 展示 | 狀態 |
|------|------|:---:|:---:|:---:|:---:|------|
| API1 BOLA | `API1-BOLA/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |
| API2 認證失效 | `API2-BrokenAuth/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |
| API3 BOPLA | `API3-BOPLA/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |
| API4 資源消耗 | `API4-ResourceConsumption/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |
| API5 BFLA | `API5-BFLA/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |
| API6 業務流程濫用 | `API6-BusinessFlows/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |
| API7 SSRF | `API7-SSRF/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |
| API8 設定錯誤 | `API8-Misconfiguration/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |
| API9 庫存管理 | `API9-InventoryMgmt/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |
| API10 不安全取用 | `API10-UnsafeConsumption/` | ☑ | ☑ | ☑ | ☑ | ✅ 完成(本機實跑通過) |

---

<sub>來源:freeCodeCamp《OWASP API Security Top 10 Course》。專案設計為可持續更新,
小步前進、每步可驗證。建立日期 2026-07-16。</sub>
