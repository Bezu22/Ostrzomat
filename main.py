import sys
import os
from pathlib import Path

# Jeśli program jest uruchomiony jako skompilowany plik .exe (PyInstaller),
# ustawiamy bieżący katalog roboczy na lokalizację pliku .exe.
# Zapobiega to błędom braku folderu 'data/' przy uruchamianiu ze skrótu na Pulpicie.
if getattr(sys, 'frozen', False):
    os.chdir(Path(sys.executable).resolve().parent)

# Nadanie procesowi unikalnego AppUserModelID w systemie Windows,
# dzięki czemu pasek zadań Windows przypisuje ikonie dedykowaną tożsamość aplikacji
# i nie zastępuje jej domyślną ikoną procesu hosta przy minimalizacji.
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('ostrzomat.cad.v02')
    except Exception:
        pass

from ui.main_window import OstrzomatApp

if __name__ == "__main__":
    app = OstrzomatApp()
    app.mainloop()