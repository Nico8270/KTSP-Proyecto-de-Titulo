#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico de carga de instancias.

Carga las 76 instancias e informa cuáles se obtienen reales (TSPLIB) y cuáles
caen en coordenadas sintéticas. Las instancias con EDGE_WEIGHT_TYPE = EXPLICIT
(matriz de distancias) eran las que antes fallaban; con instances.py corregido
deberían cargarse reales. Úsalo para saber exactamente qué instancias volver a
correr tras el arreglo:

    python check_instances.py
"""
import instances as inst

names = list(inst.OFFICIAL_KTSP.keys())
specs = [(m, inst.OFFICIAL_KTSP[m]["n"]) for m in names]
iset, any_real = inst.build_instance_set(specs)

synth, explicit, real = [], [], []
print(f"{'instancia':12} {'n':>4}  {'ewtype':14} fuente")
print("-" * 44)
for it in iset:
    src = "SINTÉTICA" if it.synthetic else "real"
    if it.synthetic:
        synth.append(it.name)
    else:
        real.append(it.name)
    if (it.ewtype or "").upper() == "EXPLICIT":
        explicit.append(it.name)
    print(f"{it.name:12} {it.n:>4}  {it.ewtype:14} {src}")

print("-" * 44)
print(f"reales: {len(real)} | sintéticas: {len(synth)} | EXPLICIT: {len(explicit)}")
if synth:
    print("\nSINTÉTICAS (sin coordenadas/‌matriz reales) -> re-ejecutar:")
    print("  " + " ".join(synth))
if explicit:
    print("\nEXPLICIT (matriz de distancias; eran las que fallaban antes):")
    print("  " + " ".join(explicit))
    print("\nPara re-correr SÓLO estas y fundirlas en el CSV existente:")
    print("  python run_opsearch_protocol.py --criteria SR --merge --names \\\n    "
          + " ".join(explicit))
