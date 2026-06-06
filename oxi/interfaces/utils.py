def expand_vlan_range(value: str | list[str]) -> list[str]:
    """Expand values like '1,7,14-15' into individual VLAN IDs."""
    if isinstance(value, list):
        value = ",".join(str(item) for item in value)

    result: list[str] = []
    if not value:
        return result
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            try:
                start, end = int(start_s), int(end_s)
            except ValueError:
                result.append(part)
                continue
            if start > end:
                start, end = end, start
            result.extend(str(i) for i in range(start, end + 1))
        else:
            result.append(part)
    return result


def decode_utf(text: str):
    """Decode escaped UTF-8 descriptions."""
    if "\\x" in text:
        desc = text.strip('"')
        decoded = (
            desc.encode("utf-8")
            .decode("unicode_escape")
            .encode("latin1")
            .decode("utf-8")
        )
        return decoded
    return text
