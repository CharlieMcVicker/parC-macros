"""
DEPRECATED: parse_chr_dict/dict_structure.py
This module has been replaced by parse_chr_dict/meta_label_compiler.py which implements
the Meta-Label FST acceptor and 4-step derivation engine.
"""

import warnings
warnings.warn(
    "dict_structure.py is deprecated and replaced by parse_chr_dict.meta_label_compiler",
    DeprecationWarning,
    stacklevel=2,
)

from parse_chr_dict.meta_label_compiler import (
    FormParsingSpec as FormParsing,
    EntryTypeSpec as EntryType,
    FORMS_TO_PARSE,
    PRIMARY_ENTRY_TYPES,
    SHIM_ENTRY_TYPES,
)
