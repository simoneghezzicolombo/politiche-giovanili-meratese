#!/usr/bin/env python3
"""Probe temporaneo per ricostruire gli endpoint pubblici FET di OpenBDAP.

Non produce dati di analisi. Serve solo a identificare in modo riproducibile
endpoint e parametri usati dalla pagina Finanza degli Enti Territoriali.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://openbdap.rgs.mef.gov.it"
PAGE = f"{BASE}/it/FET/Esplora"
API = f"{BASE}/api/api/fet"
UA = "politiche-giovanili-meratese/0.3 (+https://github.com/simoneghezzicolombo/politiche-giovanili-meratese)"
OUT = Path("data/debug/openbdap_probe.json")


def get(url: str, timeout: int = 30) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json,text/javascript,*/*;q=0.8",
            "Referer": PAGE,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return r.status, raw.decode("utf-8", errors="replace")
    except Exception as exc:  # probe: registriamo anche errori HTTP/rete
        return 0, f"{type(exc).__name__}: {exc}"


def contexts(text: str, needle: str, radius: int = 350, limit: int = 10) -> list[str]:
    out = []
    low = text.lower()
    n = needle.lower()
    start = 0
    while len(out) < limit:
        i = low.find(n, start)
        if i < 0:
            break
        a = max(0, i - radius)
        b = min(len(text), i + len(needle) + radius)
        out.append(text[a:b])
        start = i + len(needle)
    return out


def probe_endpoint(endpoint: str, params: dict[str, str]) -> dict:
    url = f"{API}/{endpoint}?{urllib.parse.urlencode(params)}"
    status, body = get(url)
    parsed = None
    if status:
        try:
            parsed = json.loads(body)
        except Exception:
            pass
    if isinstance(parsed, list):
        sample = parsed[:3]
        shape = f"list[{len(parsed)}]"
    elif isinstance(parsed, dict):
        sample = {k: parsed[k] for k in list(parsed)[:12]}
        shape = "dict"
    else:
        sample = body[:800]
        shape = "text"
    return {
        "endpoint": endpoint,
        "params": params,
        "status": status,
        "shape": shape,
        "sample": sample,
    }


def main() -> None:
    result: dict = {"page": PAGE, "page_status": None, "scripts": [], "contexts": {}, "probes": []}
    status, html = get(PAGE)
    result["page_status"] = status
    result["contexts"]["html_data_FET"] = contexts(html, "data_FET", limit=20)
    result["contexts"]["html_comparti"] = contexts(html, "Regionieprovinceautonome", limit=10)

    srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, flags=re.I)
    seen = set()
    for src in srcs:
        url = urllib.parse.urljoin(PAGE, src)
        if url in seen:
            continue
        seen.add(url)
        js_status, text = get(url)
        item = {"url": url, "status": js_status, "length": len(text)}
        if "data_FET" in text or "data_fet" in text.lower() or "/api/api/fet" in text:
            item["data_FET_contexts"] = contexts(text, "data_FET", limit=30)
            item["codProgramma_contexts"] = contexts(text, "codProgramma", limit=20)
            item["comparto_contexts"] = contexts(text, "Regionieprovinceautonome", limit=20)
            item["comuni_contexts"] = contexts(text, "Comuni", limit=20)
        result["scripts"].append(item)

    # Endpoint già verificato da codice pubblico che usa la stessa pagina FET.
    # Proviamo alcune varianti del comparto/territorio e gli endpoint adiacenti.
    compartment_variants = [
        "Comuni",
        "Comuniitaliani",
        "ComunieUnionidicomuni",
        "Comuniedunionidicomuni",
    ]
    territory_variants = ["Italia", "Lombardia"]
    for endpoint in [f"data_FET_e{i}" for i in range(1, 11)]:
        for comparto in compartment_variants:
            for territorio in territory_variants:
                params = {
                    "fase": "1",
                    "entrateSpese": "1",
                    "territorio": territorio,
                    "comparto": comparto,
                    "anno": "2025",
                    "totale": "1",
                    "codMissione": "06",
                    "codProgramma": "02",
                    "codTitolo": "00",
                    "codTipologia": "00",
                }
                probe = probe_endpoint(endpoint, params)
                result["probes"].append(probe)
                # Se troviamo una risposta JSON non vuota, basta per questo endpoint/comparto.
                sample = probe.get("sample")
                if probe["status"] == 200 and sample not in ([], {}, "", None):
                    break
            else:
                continue
            break

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Pagina FET: HTTP {status}; script trovati: {len(result['scripts'])}")
    interesting = [x for x in result["scripts"] if "data_FET_contexts" in x]
    print(f"Script con riferimenti FET: {len(interesting)}")
    for x in interesting:
        print("JS FET:", x["url"])
        for c in x.get("codProgramma_contexts", [])[:3]:
            print("codProgramma:", re.sub(r"\s+", " ", c)[:700])
        for c in x.get("comuni_contexts", [])[:3]:
            print("Comuni:", re.sub(r"\s+", " ", c)[:700])

    print("\nPROBE JSON NON VUOTI:")
    for p in result["probes"]:
        if p["status"] == 200 and p.get("sample") not in ([], {}, "", None):
            print(json.dumps(p, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
