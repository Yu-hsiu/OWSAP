"""一鍵展示:同時起 vulnerable 與 secure 兩版 Flask,對兩者跑同一支黃牛掃貨攻擊,
印出「掃空庫存 → 修補 → 限購擋下」的對照。

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

VULNERABLE_PORT = 5061
SECURE_PORT = 5062
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
    print("OWASP API6:2023 敏感業務流程存取不受限 — 黃牛掃貨 展示")
    print("=" * 60)

    print("\n[1] 攻擊『有漏洞』版本(購買端點無每人限購 / 無防自動化):")
    with BackgroundServer(vulnerable_app.create_app(), VULNERABLE_PORT):
        abused, message = attack.run_scalper_attack(f"http://127.0.0.1:{VULNERABLE_PORT}")
    print("    " + ("[漏洞成立] " if abused else "[已防禦] ") + message)

    print("\n[2] 攻擊『修補後』版本(每個帳號限購上限):")
    with BackgroundServer(secure_app.create_app(), SECURE_PORT):
        abused, message = attack.run_scalper_attack(f"http://127.0.0.1:{SECURE_PORT}")
    print("    " + ("[漏洞成立] " if abused else "[已防禦] ") + message)

    print("\n結論:同一支掃貨腳本,漏洞版一個帳號清空庫存,修補版被每人限購擋在上限。")


if __name__ == "__main__":
    main()
