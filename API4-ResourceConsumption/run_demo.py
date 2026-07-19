"""一鍵展示:同時起 vulnerable 與 secure 兩版 Flask,對兩者跑同一支資源耗盡攻擊,
印出「毫無節制 → 修補 → 上限生效」的對照。

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

VULNERABLE_PORT = 5041
SECURE_PORT = 5042
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
    print("OWASP API4:2023 資源消耗不受限 — 超大 limit 查詢 展示")
    print("=" * 60)

    print("\n[1] 攻擊『有漏洞』版本(limit 無上限):")
    with BackgroundServer(vulnerable_app.create_app(), VULNERABLE_PORT):
        unrestricted, message = attack.run_resource_exhaustion_attack(f"http://127.0.0.1:{VULNERABLE_PORT}")
    print("    " + ("[漏洞成立] " if unrestricted else "[已防禦] ") + message)

    print("\n[2] 攻擊『修補後』版本(limit 套用硬上限):")
    with BackgroundServer(secure_app.create_app(), SECURE_PORT):
        unrestricted, message = attack.run_resource_exhaustion_attack(f"http://127.0.0.1:{SECURE_PORT}")
    print("    " + ("[漏洞成立] " if unrestricted else "[已防禦] ") + message)

    print("\n結論:同一支攻擊,漏洞版回傳巨量資料吃光資源,修補版把筆數夾到上限。")


if __name__ == "__main__":
    main()
