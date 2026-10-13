"""Ejemplo académico de ETL por lotes para Yachay-Shop.

Lee ventas ficticias, valida registros, resume por canal y exporta CSV.
Solo utiliza la biblioteca estándar de Python.
"""
import csv
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "datos" / "ventas_ejemplo.csv"
SALIDA = RAIZ / "resultados" / "resumen_por_canal.csv"
COLUMNAS = {"id_venta", "fecha", "canal", "producto", "cantidad", "precio_unitario"}


def procesar_ventas():
    resumen = defaultdict(lambda: {"unidades": 0, "ingresos": Decimal("0")})
    ids = set()
    validas = 0
    omitidas = 0

    with ENTRADA.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if not lector.fieldnames or not COLUMNAS.issubset(set(lector.fieldnames)):
            raise ValueError("El archivo CSV no contiene todas las columnas requeridas")

        for numero, fila in enumerate(lector, start=2):
            try:
                identificador = fila["id_venta"].strip()
                fecha = fila["fecha"].strip()
                canal = fila["canal"].strip()
                producto = fila["producto"].strip()
                cantidad = int(fila["cantidad"])
                precio = Decimal(fila["precio_unitario"].strip())
                datetime.strptime(fecha, "%Y-%m-%d")
                if not identificador or not canal or not producto or cantidad <= 0 or not precio.is_finite() or precio < 0:
                    raise ValueError("Campos vacíos o valores no válidos")
                if identificador in ids:
                    raise ValueError("ID de venta duplicado")
                ids.add(identificador)
                resumen[canal]["unidades"] += cantidad
                resumen[canal]["ingresos"] += cantidad * precio
                validas += 1
            except (ValueError, TypeError, InvalidOperation, AttributeError) as error:
                omitidas += 1
                print(f"Fila {numero} omitida: {error}")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["canal", "unidades_vendidas", "ingresos_usd"])
        for canal in sorted(resumen):
            datos = resumen[canal]
            escritor.writerow([canal, datos["unidades"], f'{datos["ingresos"]:.2f}'])

    print("\nRESUMEN DE VENTAS POR CANAL")
    print("--------------------------")
    for canal in sorted(resumen):
        datos = resumen[canal]
        print(f'{canal}: {datos["unidades"]} unidades | USD {datos["ingresos"]:.2f}')
    total_unidades = sum(d["unidades"] for d in resumen.values())
    total_ingresos = sum((d["ingresos"] for d in resumen.values()), Decimal("0"))
    print(f"TOTAL: {total_unidades} unidades | USD {total_ingresos:.2f}")
    print(f"Registros válidos: {validas} | Omitidos: {omitidas}")
    print(f"Archivo generado: {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    procesar_ventas()
