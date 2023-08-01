
def status_update_prefix(msg: str, is_success=False) -> str:
    prefix = "success" if is_success else "error"
    return f"**{prefix}**: {msg}."

def err_lack_perm(target: str, perm: str) -> str:
    return status_update_prefix(f"`{target}` does not have required permission `{perm}`")