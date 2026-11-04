"""Scarica i file master xlsx da Dropbox direttamente nella root del repo.

Da eseguire all'inizio di ogni workflow GitHub Actions che ha bisogno di
leggere i file master aggiornati (verifica, mappa). I file vengono scaricati
sempre nella root del repo, esattamente dove li mette sync_github.ps1 e
dove li cerca verifica_v5.py (DATA_DIR = SCRIPT_DIR).

Uso:
    python mappa/fetch_masters.py

Per aggiungere/cambiare i link:
1. Su dropbox.com -> cartella PNE Simone/Guide -> click destro sul file
   -> Condividi -> Crea link -> Copia link
2. Nel link sostituisci  ?dl=0  con  ?dl=1   (forza il download diretto)
3. Aggiorna il dict MASTERS qui sotto

Lascia "TODO" nei link che non vuoi (ancora) auto-sincronizzare: lo script
li salta e stampa un avviso, senza fallire.
"""
from __future__ import annotations
import sys
import urllib.request
from pathlib import Path

# Mapping nome_file -> URL Dropbox (con ?dl=1 a fine URL).
MASTERS = {
    'Roma_2028.xlsx':   'https://www.dropbox.com/scl/fi/qjc214jsrc16qg0splxby/Roma_2028.xlsx?rlkey=qxmy4cz41lgdax3uvyd8omdy1&dl=1',
    'Milano_2028.xlsx': 'https://www.dropbox.com/scl/fi/ylgl7jutj1og2rb4abq9u/Milano_2028.xlsx?rlkey=ym8pfrmo9eqef2xtr3tsrk85s&dl=1',
    'Torino_2028.xlsx': 'https://www.dropbox.com/scl/fi/2ed10dmbejs2cruw2hud2/Torino_2028.xlsx?rlkey=qxqdiyaj5u1awp3tpbtp4nj7b&dl=1',
}

# Timeout download (Dropbox puo' essere lento la prima volta)
TIMEOUT = 60


def scarica(nome: str, url: str, dest: Path) -> bool:
    """Scarica un singolo file. Ritorna True se ok, False se errore."""
    print(f"  {nome} ...", end=' ', flush=True)
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'PNE-fetch-masters/1.0',
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

    # Sanity check: Dropbox a volte restituisce una pagina HTML invece del file
    # se il link non e' valido. I file xlsx iniziano con la signature ZIP (PK).
    if not data[:2] == b'PK':
        print(f"NON e' un file xlsx (forse il link e' scaduto o errato)")
        return False

    dest.write_bytes(data)
    print(f"OK ({len(data):,} bytes)")
    return True


def main() -> int:
    base = Path(__file__).resolve().parent.parent  # root del repo
    print(f"Scarico master da Dropbox in: {base}")

    n_ok, n_skip, n_err = 0, 0, 0
    for nome, url in MASTERS.items():
        if url.startswith('TODO'):
            print(f"  {nome} ... SALTATO (link non configurato)")
            n_skip += 1
            continue
        if scarica(nome, url, base / nome):
            n_ok += 1
        else:
            n_err += 1

    print(f"\nRisultato: {n_ok} scaricati, {n_skip} saltati, {n_err} errori")

    return 1 if n_err else 0


if __name__ == '__main__':
    raise SystemExit(main())
