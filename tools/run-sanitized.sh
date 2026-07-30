#!/bin/sh
# Run a command with AddressSanitizer working, on a machine where Citrix
# Workspace has hijacked the dynamic linker.
#
# THE PROBLEM
#   Citrix installs /usr/local/lib/AppProtection/libAppProtection.so into
#   /etc/ld.so.preload, so it is loaded into every single process before
#   anything else. Among the symbols it exports is its own `dlsym` (the rest
#   are X11 hooks -- XGetImage, XNextEvent, XQueryExtension -- which implement
#   its anti-screenshot and anti-keylogger feature).
#
#   ASan's runtime calls dlsym(RTLD_NEXT, "malloc") during its own start-up,
#   before libc and libstdc++ are initialised. With Citrix's dlsym in the way
#   that crashes, so any ASan binary dies before main with no output at all.
#   -static-libasan does not help: the problem is not the load order of ASan's
#   runtime, it is that dlsym itself has been replaced.
#
# THE WORKAROUND
#   Enter an unprivileged user + mount namespace and bind-mount an empty file
#   over /etc/ld.so.preload. Only this process tree sees the change; nothing on
#   the real system is modified and no root is needed. Citrix App Protection
#   keeps working everywhere else, including in the session you are sitting in.
#
# Usage:
#   tools/run-sanitized.sh ./build-asan/tests/we2002_tests
#   WE2002_TEST_IMAGE=/tmp/copy.bin tools/run-sanitized.sh ./build-asan/tests/we2002_tests

set -eu

if [ $# -eq 0 ]; then
    echo "uso: $0 <comando> [args...]" >&2
    exit 2
fi

if [ ! -e /etc/ld.so.preload ]; then
    # Nothing to work around.
    exec "$@"
fi

if ! command -v unshare >/dev/null 2>&1; then
    echo "$0: unshare nao encontrado; rode UBSan em vez de ASan" >&2
    exit 1
fi

empty=$(mktemp)
trap 'rm -f "$empty"' EXIT

# -U user namespace, -r map to root inside it, -m mount namespace.
unshare -Urm sh -c '
    mount --bind "$1" /etc/ld.so.preload || exit 1
    shift
    exec "$@"
' _ "$empty" "$@"
