from urllib.parse import unquote, urlsplit


def safe_redirect_target(target: str | None, fallback: str) -> str:
    if (
        not target
        or target.startswith("//")
        or target[0].isspace()
        or "\\" in target
    ):
        return fallback

    try:
        parsed = urlsplit(target)
    except ValueError:
        return fallback
    decoded_path = unquote(parsed.path)
    if (
        parsed.scheme
        or parsed.netloc
        or not parsed.path.startswith("/")
        or parsed.path.startswith("//")
        or decoded_path.startswith("//")
        or "\\" in decoded_path
    ):
        return fallback

    return target
