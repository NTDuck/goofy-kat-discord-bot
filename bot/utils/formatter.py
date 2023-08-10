
def status_update_prefix(msg: str, success=False) -> str:
    prefix = "success" if success else "error"
    return f"**{prefix}**: {msg}."