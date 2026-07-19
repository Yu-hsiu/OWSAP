"""模擬「已被攻擊者控制的第三方折扣服務」。

代表我方應用去取用的外部 API。攻擊者已能左右它的回應(供應鏈被入侵、或走未
加密通道被 MITM),於是它回傳一個惡意的折扣百分比。
"""

from flask import Flask, jsonify

from consumption_common import MALICIOUS_DISCOUNT_PERCENT


def create_app():
    app = Flask(__name__)

    @app.get("/coupon")
    def coupon():
        return jsonify({"discount_percent": MALICIOUS_DISCOUNT_PERCENT}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5100)
