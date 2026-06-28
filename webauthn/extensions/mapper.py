from typing import Any, Dict, List, Optional, Union


def build_extension_inputs(
    extensions: Optional[Union[List[Any], Dict[str, Any]]],
) -> Optional[Dict[str, Any]]:
    if extensions is None:
        return None

    if isinstance(extensions, list):
        if not extensions:
            return None
        return {ext.extension_id: ext.input_value() for ext in extensions}

    if isinstance(extensions, dict):
        return dict(extensions) if extensions else None

    raise TypeError("extensions must be a list of extension objects or a dict")
