"""一鍵展示:起一個(被控制的)第三方服務 + vulnerable / secure 兩版 app,對兩版
跑同一支攻擊,印出「金額被污染成負數 → 修補 → 惡意值被拒用」的對照。

Colab 用法:!python run_demo.py(或把本檔內容貼成一個 cell 執行)。
整個過程在同一進程內完成,不需開對外連接埠。
"""

import logging
import threading
import time

from werkzeug.serving import make_server

import attack
import secure_app
import third_party_api
import vulnerable_app

logging.getLogger("werkzeug").setLevel(logging.ERROR)

THIRD_PARTY_PORT = 5100
VULNERABLE_PORT = 5101
SECURE_PORT = 5102
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
    print("OWASP API10:2023 不安全地取用 API — 過度信任第三方資料 展示")
    print("=" * 60)

    # 第三方(已被攻擊者控制)全程開著,回傳惡意折扣。
    with BackgroundServer(third_party_api.create_app(), THIRD_PARTY_PORT):
        print("\n[1] 攻擊『有漏洞』版本(未驗證第三方折扣就套進金額):")
        with BackgroundServer(vulnerable_app.create_app(), VULNERABLE_PORT):
            poisoned, message = attack.run_unsafe_consumption_attack(f"http://127.0.0.1:{VULNERABLE_PORT}")
        print("    " + ("[漏洞成立] " if poisoned else "[已防禦] ") + message)

        print("\n[2] 攻擊『修補後』版本(把第三方資料當使用者輸入驗證):")
        with BackgroundServer(secure_app.create_app(), SECURE_PORT):
            poisoned, message = attack.run_unsafe_consumption_attack(f"http://127.0.0.1:{SECURE_PORT}")
        print("    " + ("[漏洞成立] " if poisoned else "[已防禦] ") + message)

    print("\n結論:同一支攻擊,漏洞版讓被污染的第三方折扣把金額算成負數,修補版驗證後拒用惡意值。")


if __name__ == "__main__":
    main()
