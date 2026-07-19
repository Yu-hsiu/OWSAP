"""一鍵展示:同時起 vulnerable 與 secure 兩版 Flask,對兩者跑同一支批量賦值提權
攻擊,印出「提權成功 → 修補 → 被擋」的對照。

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

VULNERABLE_PORT = 5021
SECURE_PORT = 5022
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
    print("OWASP API3:2023 BOPLA(批量賦值)— 註冊提權 展示")
    print("=" * 60)

    print("\n[1] 攻擊『有漏洞』版本(整包 body 綁進使用者記錄):")
    with BackgroundServer(vulnerable_app.create_app(), VULNERABLE_PORT):
        escalated, message = attack.run_mass_assignment_attack(f"http://127.0.0.1:{VULNERABLE_PORT}")
    print("    " + ("[漏洞成立] " if escalated else "[已防禦] ") + message)

    print("\n[2] 攻擊『修補後』版本(只取白名單欄位,is_admin 由後端決定):")
    with BackgroundServer(secure_app.create_app(), SECURE_PORT):
        escalated, message = attack.run_mass_assignment_attack(f"http://127.0.0.1:{SECURE_PORT}")
    print("    " + ("[漏洞成立] " if escalated else "[已防禦] ") + message)

    print("\n結論:同一支攻擊,漏洞版靠偷塞 is_admin 拿到管理員權限,修補版被白名單擋下。")


if __name__ == "__main__":
    main()
