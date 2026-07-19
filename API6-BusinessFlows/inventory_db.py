"""共用的庫存與令牌工具(vulnerable / secure 兩版都用)。

情境:一件熱門限量商品(PS5)開賣。業務流程本身沒有技術漏洞,但若缺乏防自動化
措施,黃牛(scalper)就能用機器人在瞬間把庫存整批掃空,讓一般人買不到——這就是
「敏感業務流程存取不受限」。
"""

ITEM_NAME = "PS5"
INITIAL_STOCK = 10  # 限量庫存

# token -> 買家帳號名稱。真實系統不會這樣硬編碼,此處只為 demo 認證。
TOKENS = {
    "scalper-token": "scalper",
}


def seed_stock():
    """回傳全新的庫存狀態副本。"""
    return {ITEM_NAME: INITIAL_STOCK}


def resolve_token(auth_header):
    """從 `Authorization: Bearer <token>` 標頭解出買家名稱,失敗回傳 None。"""
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[len("Bearer "):].strip()
    return TOKENS.get(token)
