"""模擬「內部服務」——SSRF 攻擊真正想打到的目標。

代表一個只有內網 / 伺服器本身碰得到、攻擊者無法直接存取的位址(例如雲端
metadata 服務 169.254.169.254、內網後台)。在 demo 裡它跑在一個 localhost 埠,
攻擊者不直接打它,而是「借」有漏洞的 app 之手去打它。
"""

from flask import Flask, jsonify

from ssrf_common import FAKE_CREDENTIALS


def create_app():
    app = Flask(__name__)

    @app.get("/metadata")
    def metadata():
        return jsonify(FAKE_CREDENTIALS), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5070)
