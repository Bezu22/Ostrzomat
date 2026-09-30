import sys
import os
from pathlib import Path

# Jeśli program jest uruchomiony jako skompilowany plik .exe (PyInstaller),
# ustawiamy bieżący katalog roboczy na lokalizację pliku .exe.
# Zapobiega to błędom braku folderu 'data/' przy uruchamianiu ze skrótu na Pulpicie.
if getattr(sys, 'frozen', False):
    os.chdir(Path(sys.executable).resolve().parent)

from ui.main_window import OstrzomatApp

if __name__ == "__main__":
    app = OstrzomatApp()
    app.mainloop()