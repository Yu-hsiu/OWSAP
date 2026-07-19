"""共用設定與內部服務的假機密(vulnerable / secure 兩版都用)。

情境:一個「幫你抓取遠端資源」的端點(例如抓 URL 產生預覽 / 匯入圖片)。使用者
可以控制伺服器要去抓的 URL。攻擊者把 URL 換成指向「內部服務」——一個攻擊者
自己碰不到、但伺服器碰得到的位址(如雲端 metadata、內網後台)——藉伺服器之手
讀出內部機密。這就是 SSRF(伺服器端請求偽造)。
"""

# 內部服務回傳的假雲端憑證(模擬只有內網 / 伺服器本身能讀到的敏感資料)。
FAKE_CREDENTIALS = {
    "service": "internal-metadata",
    "aws_access_key_id": "AKIA-INTERNAL-DO-NOT-LEAK",
    "aws_secret_access_key": "s3cr3t-internal-metadata-key",
}

# 用來判斷回應裡是否洩漏了內部機密的標記字串。
SECRET_MARKER = FAKE_CREDENTIALS["aws_secret_access_key"]

# 修補版的來源白名單:只允許抓取這些「已知安全的外部主機」。
# 內部 / localhost / 私有位址都不在其中,因此會被擋下。
ALLOWED_HOSTS = ("cdn.example.com", "images.example.com")
