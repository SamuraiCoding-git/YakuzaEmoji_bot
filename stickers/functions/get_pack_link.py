import uuid


def get_pack_link(bot_username: str, user_id: int):
    return f"{bot_username}_{uuid.uuid4().hex[:10]}_{user_id}"