import platform
from pathlib import Path


_SYSTEM_TO_OS = {
    "Linux": "Linux",
    "Darwin": "MacOS",
}

_system = platform.system()
if _system not in _SYSTEM_TO_OS:
    raise RuntimeError(f"Unsupported OS: {_system}")

OS = _SYSTEM_TO_OS[_system]

path2qpoases = "../"
_qpoases_root = Path(path2qpoases)

library_dirs = [str(_qpoases_root / "bin")]

# Path to Apple's Accelerate, only needed on MacOS.
_apple_sdk = Path("/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk")
apple_accelerate_path = str(_apple_sdk / "usr/lib/System") if OS == "MacOS" else None

extra_link_args = []
extra_compile_args = [
    "-Wall",
    "-pedantic",
    "-Wshadow",
    "-Wfloat-equal",
    "-Wconversion",
    "-Wsign-conversion",
    "-fPIC",
    "-D__NO_COPYRIGHT__0",
    "-O3",
    "-std=c++20",
]

if OS == "MacOS":
    library_dirs.append(apple_accelerate_path)
    extra_link_args += ["-framework", "Accelerate"]
    extra_compile_args = ["-isysroot", str(_apple_sdk)] + extra_compile_args
