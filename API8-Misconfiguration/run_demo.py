"""一鍵展示:同時起 vulnerable 與 secure 兩版 Flask,對兩者跑同一支錯誤洩漏攻擊,
印出「洩漏堆疊 → 修補 → 只回一般訊息」的對照。

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

logging.getLogger("werkzeug").setLevel(logging.ERROR)
# 修補版會用 app.logger.error 記錯誤,demo 時把它靜音,避免蓋掉攻防對照輸出。
logging.getLogger("secure_app").setLevel(logging.CRITICAL)

VULNERABLE_PORT = 5081
SECURE_PORT = 5082
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
    print("OWASP API8:2023 安全設定錯誤 — 錯誤訊息洩漏堆疊 展示")
    print("=" * 60)

    print("\n[1] 攻擊『有漏洞』版本(把完整 traceback 回給用戶端):")
    with BackgroundServer(vulnerable_app.create_app(), VULNERABLE_PORT):
        leaked, message = attack.run_error_leak_attack(f"http://127.0.0.1:{VULNERABLE_PORT}")
    print("    " + ("[漏洞成立] " if leaked else "[已防禦] ") + message)

    print("\n[2] 攻擊『修補後』版本(細節只記伺服器端,對外回一般訊息):")
    with BackgroundServer(secure_app.create_app(), SECURE_PORT):
        leaked, message = attack.run_error_leak_attack(f"http://127.0.0.1:{SECURE_PORT}")
    print("    " + ("[漏洞成立] " if leaked else "[已防禦] ") + message)

    print("\n結論:同一支攻擊,漏洞版把伺服器堆疊細節洩漏給攻擊者,修補版只回不洩密的一般訊息。")


if __name__ == "__main__":
    main()
