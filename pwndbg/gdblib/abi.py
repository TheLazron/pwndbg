from __future__ import annotations

import functools
from typing import Any
from typing import Callable
from typing import Optional
from typing import TypeVar

import gdb

import pwndbg.color.message as M

T = TypeVar("T")

abi = None
linux = False


def update() -> None:
    global abi
    global linux

    # Detect current ABI of client side by 'show osabi'
    #
    # Examples of strings returned by `show osabi`:
    # 'The current OS ABI is "auto" (currently "GNU/Linux").\nThe default OS ABI is "GNU/Linux".\n'
    # 'The current OS ABI is "GNU/Linux".\nThe default OS ABI is "GNU/Linux".\n'
    # 'El actual SO ABI es «auto» (actualmente «GNU/Linux»).\nEl SO ABI predeterminado es «GNU/Linux».\n'
    # 'The current OS ABI is "auto" (currently "none")'
    #
    # As you can see, there might be GDBs with different language versions
    # and so we have to support it there too.
    # Lets assume and hope that `current osabi` is returned in first line in all languages...
    abi = gdb.execute("show osabi", to_string=True).split("\n")[0]

    # Currently we support those osabis:
    # 'GNU/Linux': linux
    # 'none': bare metal

    linux = "GNU/Linux" in abi

    if not linux:
        msg = M.warn(
            "The bare metal debugging is enabled since gdb's osabi is '%s' which is not 'GNU/Linux'.\n"
            "Ex. the page resolving and memory de-referencing ONLY works on known pages.\n"
            "This option is based on GDB client compile arguments (by default) and will be corrected if you load an ELF with a '.note.ABI-tag' section.\n"
            "If you are debugging a program that runs on the Linux ABI, please select the correct GDB client."
            % abi
        )
        print(msg)


def LinuxOnly(
    default: Optional[Any] = None,
) -> Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
    """Create a decorator that the function will be called when ABI is Linux.
    Otherwise, return `default`.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def caller(*args: Any, **kwargs: Any) -> Optional[T]:
            if linux:
                return func(*args, **kwargs)
            else:
                return default

        return caller

    return decorator
