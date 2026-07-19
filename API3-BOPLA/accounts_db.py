"""共用的註冊工具(vulnerable / secure 兩版都用)。

情境:一個註冊端點,建立使用者後回傳令牌;另有一個只有管理員能用的端點。
攻擊者想在註冊時偷偷把自己變成管理員(privilege escalation)。
"""

import secrets

# 修補版才會用到:註冊時「唯一允許」由用戶端設定的欄位白名單。
# is_admin 刻意不在其中——權限只能由後端決定,不能由用戶端輸入指定。
ALLOWED_REGISTRATION_FIELDS = ("name", "email", "password")


def new_token():
    """產生一組不可預測的工作階段令牌。"""
    return secrets.token_hex(8)
