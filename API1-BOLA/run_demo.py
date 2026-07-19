"""一鍵展示:同時起 vulnerable 與 secure 兩版 Flask,對兩者跑同一支 BOLA 攻擊,
印出「攻擊成功 → 修補 → 攻擊失敗」的對照。

Colab 用法(任一皆可):
    !python run_demo.py
或貼成一個 cell 執行本檔內容。整個過程在同一進程內完成(Flask 跑背景執行緒、
requests 打 localhost),不需開對外連接埠,適合 Colab 展示。
"""

import logging
import threading
import time

from werkzeug.serving import make_server

# 靜音 werkzeug 的存取日誌,讓 demo 輸出乾淨(只留我們自己印的攻防對照)。
logging.getLogger("werkzeug").setLevel(logging.ERROR)

import attack
import secure_app
import vulnerable_app

VULNERABLE_PORT = 5001
SECURE_PORT = 5002
SERVER_BOOT_SECONDS = 1.0


class BackgroundServer:
    """把 Flask app 跑在背景執行緒,demo 結束後可乾淨關閉。"""

    def __init__(self, app, port):
        self._server = make_server("127.0.0.1", port, app)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        time.sleep(SERVER_BOOT_SECONDS)  # 等伺服器就緒再打
        return self

    def __exit__(self, *_):
        self._server.shutdown()


def main():
    print("=" * 60)
    print("OWASP API1:2023 BOLA — 攻防展示")
    print("=" * 60)

    print("\n[1] 攻擊『有漏洞』版本(未做物件層級授權):")
    with BackgroundServer(vulnerable_app.create_app(), VULNERABLE_PORT):
        leaked, message = attack.run_bola_attack(f"http://127.0.0.1:{VULNERABLE_PORT}")
    print("    " + ("[漏洞成立] " if leaked else "[已防禦] ") + message)

    print("\n[2] 攻擊『修補後』版本(加了擁有者授權檢查):")
    with BackgroundServer(secure_app.create_app(), SECURE_PORT):
        leaked, message = attack.run_bola_attack(f"http://127.0.0.1:{SECURE_PORT}")
    print("    " + ("[漏洞成立] " if leaked else "[已防禦] ") + message)

    print("\n結論:同一支攻擊腳本,漏洞版洩漏他人 ssn,修補版被 403 擋下。")


if __name__ == "__main__":
    main()
