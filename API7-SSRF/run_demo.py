"""一鍵展示:起一個內部服務 + vulnerable / secure 兩版 app,對兩版跑同一支 SSRF
攻擊,印出「竊取內部機密 → 修補 → 被白名單擋下」的對照。

Colab 用法:!python run_demo.py(或把本檔內容貼成一個 cell 執行)。
整個過程在同一進程內完成,不需開對外連接埠。
"""

import logging
import threading
import time

from werkzeug.serving import make_server

import attack
import internal_service
import secure_app
import vulnerable_app

logging.getLogger("werkzeug").setLevel(logging.ERROR)

INTERNAL_PORT = 5070
VULNERABLE_PORT = 5071
SECURE_PORT = 5072
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
    print("OWASP API7:2023 SSRF(伺服器端請求偽造)— 竊取內部服務機密 展示")
    print("=" * 60)

    internal_url = f"http://127.0.0.1:{INTERNAL_PORT}/metadata"

    # 內部服務全程開著(代表攻擊者碰不到、但 app 伺服器碰得到的內網資源)。
    with BackgroundServer(internal_service.create_app(), INTERNAL_PORT):
        print("\n[1] 攻擊『有漏洞』版本(抓取端點不驗證目標):")
        with BackgroundServer(vulnerable_app.create_app(), VULNERABLE_PORT):
            stolen, message = attack.run_ssrf_attack(f"http://127.0.0.1:{VULNERABLE_PORT}", internal_url)
        print("    " + ("[漏洞成立] " if stolen else "[已防禦] ") + message)

        print("\n[2] 攻擊『修補後』版本(抓取前過主機白名單):")
        with BackgroundServer(secure_app.create_app(), SECURE_PORT):
            stolen, message = attack.run_ssrf_attack(f"http://127.0.0.1:{SECURE_PORT}", internal_url)
        print("    " + ("[漏洞成立] " if stolen else "[已防禦] ") + message)

    print("\n結論:同一支攻擊,漏洞版借伺服器讀出內部憑證,修補版被白名單擋在抓取前。")


if __name__ == "__main__":
    main()
