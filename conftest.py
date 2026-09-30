import os
import sys

# Ustawienie ścieżek TCL/TK dla środowiska testowego (zapobiega błędowi tcl_findLibrary w systemie Windows)
base_prefix = getattr(sys, "base_prefix", sys.prefix)
tcl_dir = os.path.join(base_prefix, "tcl", "tcl8.6")
tk_dir = os.path.join(base_prefix, "tcl", "tk8.6")
if os.path.exists(tcl_dir) and "TCL_LIBRARY" not in os.environ:
    os.environ["TCL_LIBRARY"] = tcl_dir
if os.path.exists(tk_dir) and "TK_LIBRARY" not in os.environ:
    os.environ["TK_LIBRARY"] = tk_dir

# Upewnienie się, że katalog główny projektu jest w sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
