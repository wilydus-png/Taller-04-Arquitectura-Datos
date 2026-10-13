"""Demostración mínima de procesamiento por lotes para Yachay-Shop.

Lee ventas ficticias y calcula ingresos y unidades por canal.
No requiere dependencias externas ni conexión a internet.
"""
import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

ARCHIVO = Path(__file__).resolve().parent.parent / "datos" / "ventas_ejemplo.csv"


def main():
    resumen = defaultdict(lambda: {"unidades": 0, "ventas": Decimal("0")})
    ids = set()
    with ARCHIVO.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for numero, fila in enumerate(lector, start=2):
            try:
                identificador = fila["id_venta"].strip()
                canal = fila["canal"].strip()
                cantidad = int(fila["cantidad"])
                precio = Decimal(fila["precio_unitario"])
                if not identificador or not canal or cantidad <= 0 or precio < 0:
                    raise ValueError("campos vacíos o valores no válidos")
                if identificador in ids:
                    print(f"Se omite fila {numero}: id de venta duplicado")
                    continue
                ids.add(identificador)
                resumen[canal]["unidades"] += cantidad
                resumen[canal]["ventas"] += cantidad * precio
            except (KeyError, ValueError, InvalidOperation, AttributeError) as error:
                print(f"Se omite fila {numero}: {error}")

    print("RESUMEN DE VENTAS POR CANAL")
    for canal in sorted(resumen):
        datos = resumen[canal]
        print(f"{canal}: {datos['unidades']} unidades | USD {datos['ventas']:.2f}")
    print(f"TOTAL: {sum(x['unidades'] for x in resumen.values())} unidades | "
          f"USD {sum((x['ventas'] for x in resumen.values()), Decimal('0')):.2f}")


if __name__ == "__main__":
    main()
