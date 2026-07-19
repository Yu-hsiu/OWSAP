"""一鍵展示:同時起 vulnerable 與 secure 兩版 Flask,對兩者跑同一支暴力破解攻擊,
印出「帳號接管 → 修補 → 被鎖定」的對照。

Colab 用法:!python run_demo.py(或把本檔內容貼成一個 cell 執行)。
整個過程在同一進程內完成,不需開對外連接埠。
"""

import logging
import threading
import time

from werkzeug.serving import make_server

import attack
import secure_app
import vulnerable_app

# 靜音 werkzeug 的存取日誌(暴力破解會刷出上千行請求紀錄),只留攻防對照。
logging.getLogger("werkzeug").setLevel(logging.ERROR)

VULNERABLE_PORT = 5011
SECURE_PORT = 5012
SERVER_BOOT_SECONDS = 1.0


class BackgroundServer:
    """把 Flask app 跑在背景執行緒,demo 結束後可乾淨關閉。"""

    def __init__(self, app, port):
        self._server = make_server("127.0.0.1", port, app)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        time.sleep(SERVER_BOOT_SECONDS)
        return self

    def __exit__(self, *_):
        self._server.shutdown()


def main():
    print("=" * 60)
    print("OWASP API2:2023 認證失效 — 暴力破解密碼重置驗證碼 展示")
    print("=" * 60)

    print("\n[1] 攻擊『有漏洞』版本(驗證碼嘗試次數無限制):")
    with BackgroundServer(vulnerable_app.create_app(), VULNERABLE_PORT):
        taken_over, message = attack.run_bruteforce_attack(f"http://127.0.0.1:{VULNERABLE_PORT}")
    print("    " + ("[漏洞成立] " if taken_over else "[已防禦] ") + message)

    print("\n[2] 攻擊『修補後』版本(達失敗上限即鎖定):")
    with BackgroundServer(secure_app.create_app(), SECURE_PORT):
        taken_over, message = attack.run_bruteforce_attack(f"http://127.0.0.1:{SECURE_PORT}")
    print("    " + ("[漏洞成立] " if taken_over else "[已防禦] ") + message)

    print("\n結論:同一支暴力破解腳本,漏洞版枚舉即接管帳號,修補版數次嘗試即被 429 鎖定。")


if __name__ == "__main__":
    main()
