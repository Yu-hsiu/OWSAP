"""不安全取用攻擊腳本:觸發一次結帳,讓應用去取用「已被控制的第三方」,
看被污染的折扣有沒有流進金額計算。

同一支腳本打 vulnerable 與 secure 兩版,靠最終金額證明漏洞是否成立:
- vulnerable:未驗證第三方折扣 → 荒謬折扣讓最終金額變負數 → 店家倒貼。
- secure:驗證第三方資料、拒用不合理值 → 金額維持正常 → 攻擊失敗。
"""

import requests

BASE_PRICE = 100
REQUEST_TIMEOUT_SECONDS = 5


def run_unsafe_consumption_attack(base_url):
    """回傳 (是否被污染, 說明字串)。是否被污染=True 代表漏洞成立。"""
    resp = requests.post(
        f"{base_url}/api/checkout",
        json={"base_price": BASE_PRICE},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if resp.status_code != 200:
        return False, f"結帳未成功(status={resp.status_code})"

    data = resp.json()
    final_price = data.get("final_price", 0)
    if final_price < 0:
        return True, f"最終金額被算成 {final_price}(原價 {BASE_PRICE}),店家反而倒貼給攻擊者"
    return False, f"最終金額 {final_price} 維持正常(第三方惡意值被拒用),攻擊失敗"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5101"
    poisoned, message = run_unsafe_consumption_attack(target)
    print(("[漏洞成立] " if poisoned else "[已防禦] ") + message)
