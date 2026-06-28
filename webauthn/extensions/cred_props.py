from dataclasses import dataclass
from typing import Optional

class CredPropsExtension:

    @property
    def extension_id(self) -> str:
        return "credProps"

    def input_value(self) -> bool:
        """Per spec, the client extension input is simply ``True``."""
        return True


@dataclass
class CredPropsOutput:
    rk: Optional[bool] = None
