"""
Cliente da API da Caixa Econômica Federal
"""
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from config import API_BASE_URL, CACHE_DIR, CACHE_TIMEOUT, MIRROR_BASE_URL


def _adaptar_schema_mirror(data: dict) -> dict | None:
    """Converte o schema do mirror (guto-alves/loterias-api) para o schema
    da API da Caixa usado pelo app: concurso->numero, dezenas->listaDezenas,
    data->dataApuracao. Mantem os campos extras do mirror intactos."""
    if not isinstance(data, dict) or data.get("concurso") is None:
        return None
    return {
        "numero": data.get("concurso"),
        "dataApuracao": data.get("data", ""),
        "listaDezenas": data.get("dezenas", []),
        "dezenasSorteadasOrdemSorteio": data.get("dezenasOrdemSorteio", []),
        **{k: v for k, v in data.items() if k not in ("concurso", "data", "dezenas", "dezenasOrdemSorteio")},
    }


class CaixaAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def _get_cache_path(self, lottery: str, concurso: int = None) -> str:
        if concurso:
            return os.path.join(CACHE_DIR, f"{lottery}_{concurso}.json")
        return os.path.join(CACHE_DIR, f"{lottery}_latest.json")

    def _is_cache_valid(self, cache_path: str) -> bool:
        if not os.path.exists(cache_path):
            return False
        mtime = os.path.getmtime(cache_path)
        return (time.time() - mtime) < CACHE_TIMEOUT

    def _load_cache(self, cache_path: str) -> dict | None:
        try:
            with open(cache_path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError):
            return None

    def _save_cache(self, cache_path: str, data: dict):
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (PermissionError, OSError):
            pass

    def _fetch_mirror(self, lottery: str, concurso: int = None) -> dict | None:
        """Busca um resultado no mirror publico (guto-alves/loterias-api).

        Usado como fallback quando a API oficial da Caixa esta bloqueada.
        Retorna o dado ja adaptado para o schema da Caixa, ou None.
        """
        url = f"{MIRROR_BASE_URL}/{lottery}"
        if concurso:
            url += f"/{concurso}"
        else:
            url += "/latest"
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            return _adaptar_schema_mirror(resp.json())
        except Exception as e:
            print(f"Erro ao buscar {lottery} {concurso or 'latest'} via mirror: {e}")
            return None

    def get_latest_result(self, lottery: str) -> dict:
        cache_path = self._get_cache_path(lottery)

        if self._is_cache_valid(cache_path):
            cached = self._load_cache(cache_path)
            if cached:
                return cached

        url = f"{API_BASE_URL}/{lottery}"
        data = None
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Erro ao buscar {lottery} na API oficial: {e}")

        if data is None:
            data = self._fetch_mirror(lottery)

        if data:
            self._save_cache(cache_path, data)
            return data
        return self._load_cache(cache_path)

    def get_concurso(self, lottery: str, concurso: int, max_tentativas: int = 4) -> dict:
        cache_path = self._get_cache_path(lottery, concurso)

        if self._is_cache_valid(cache_path):
            cached = self._load_cache(cache_path)
            if cached:
                return cached

        url = f"{API_BASE_URL}/{lottery}/{concurso}"
        data = None
        for tentativa in range(1, max_tentativas + 1):
            try:
                resp = self.session.get(url, timeout=30)
                if resp.status_code == 429:
                    # Rate limit da API: espera exponencial e tenta de novo
                    time.sleep(2 ** tentativa)
                    continue
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                if tentativa == max_tentativas:
                    print(f"Erro ao buscar {lottery} concurso {concurso}: {e}")
                else:
                    time.sleep(1)

        if data is None:
            data = self._fetch_mirror(lottery, concurso)

        if data:
            self._save_cache(cache_path, data)
            return data
        return self._load_cache(cache_path)

    def _fetch_concursos_paralelo(self, lottery: str, concursos: list, max_workers: int = 3) -> list:
        """Busca multiplos concursos em paralelo (respeitando o cache em disco).

        O numero de workers e limitado para nao sobrecarregar a API da Caixa.
        Mantem a ordem original dos concursos via indice.
        """
        if not concursos:
            return []

        results = [None] * len(concursos)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(self.get_concurso, lottery, num): idx
                for idx, num in enumerate(concursos)
            }
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception:
                    results[idx] = None

        return [r for r in results if r]

    def get_historical_results(self, lottery: str, count: int = 50) -> list:
        latest = self.get_latest_result(lottery)
        if not latest:
            return []

        latest_number = latest.get("numero", 0)
        concursos = []
        for i in range(count):
            concurso_num = latest_number - i
            if concurso_num < 1:
                break
            concursos.append(concurso_num)

        return self._fetch_concursos_paralelo(lottery, concursos)

    def get_all_results_up_to(self, lottery: str, max_concurso: int = None) -> list:
        latest = self.get_latest_result(lottery)
        if not latest:
            return []

        latest_number = latest.get("numero", 0)
        target = max_concurso or latest_number
        concursos = list(range(1, target + 1))

        return self._fetch_concursos_paralelo(lottery, concursos)


# Instância global
api_client = CaixaAPIClient()
