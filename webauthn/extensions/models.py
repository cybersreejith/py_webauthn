from dataclasses import dataclass
from typing import Optional

from .cred_props import CredPropsOutput


@dataclass
class ClientExtensionResults:
    cred_props: Optional[CredPropsOutput] = None
    
    # Future fields go here, e.g.:
    # uvm: Optional[List[UvmOutput]] = None
    # large_blob: Optional[LargeBlobOutput] = None

