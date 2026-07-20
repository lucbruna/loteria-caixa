"""
Loteria Federal - Launcher do Servidor (versao empacotada / .exe)

Inicia o servidor Flask e abre o dashboard no navegador padrao.
Usado tanto em desenvolvimento quanto no executavel gerado pelo PyInstaller.
"""
import os
import sys
import threading
import webbrowser
import time

from config import FLASK_HOST, FLASK_PORT

import app


def _abrir_navegador():
    """Abre o dashboard alguns segundos apos o servidor subir."""
    time.sleep(2.5)
    try:
        webbrowser.open(f"http://{FLASK_HOST}:{FLASK_PORT}")
    except Exception:
        pass


def main():
    url = f"http://{FLASK_HOST}:{FLASK_PORT}"

    banner = (
        "\n"
        "==============================================================\n"
        "  LOTERIA FEDERAL - Sistema de Analise com IA\n"
        "==============================================================\n"
        f"  Dashboard: {url}\n"
        "  (o navegador sera aberto automaticamente)\n"
        "  Para encerrar, feche esta janela ou pressione Ctrl+C\n"
        "==============================================================\n"
    )
    print(banner)

    threading.Thread(target=_abrir_navegador, daemon=True).start()

    # use_reloader=False eh obrigatorio em ambiente congelado (PyInstaller)
    app.app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrando...")
        sys.exit(0)
