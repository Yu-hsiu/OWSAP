"""一鍵展示:同時起 vulnerable 與 secure 兩版 Flask,對兩者跑同一支舊版 API 探測
攻擊,印出「走舊版偷資料 → 修補 → 舊版退役擋下」的對照。

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

VULNERABLE_PORT = 5091
SECURE_PORT = 5092
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
    print("OWASP API9:2023 庫存管理不當 — 被遺忘的舊版 API 展示")
    print("=" * 60)

    print("\n[1] 攻擊『有漏洞』版本(舊版 v1 還活著、當年沒認證):")
    with BackgroundServer(vulnerable_app.create_app(), VULNERABLE_PORT):
        leaked, message = attack.run_shadow_api_attack(f"http://127.0.0.1:{VULNERABLE_PORT}")
    print("    " + ("[漏洞成立] " if leaked else "[已防禦] ") + message)

    print("\n[2] 攻擊『修補後』版本(舊版 v1 已退役,只留有認證的 v2):")
    with BackgroundServer(secure_app.create_app(), SECURE_PORT):
        leaked, message = attack.run_shadow_api_attack(f"http://127.0.0.1:{SECURE_PORT}")
    print("    " + ("[漏洞成立] " if leaked else "[已防禦] ") + message)

    print("\n結論:同一支攻擊,漏洞版靠被遺忘的舊版 v1 繞過認證偷資料,修補版把 v1 退役後無路可走。")


if __name__ == "__main__":
    main()
