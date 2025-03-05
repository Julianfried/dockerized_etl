"""
load.py - Modulo de Carga de Datos
Este módulo simula la carga de datos procesados en un sistema destino.
"""

import pandas as pd


def load_data(df: pd.DataFrame):
    """
    Simula la carga de datos mostrando el DataFrame en consola.

    Args:
        df (pd.DataFrame): DataFrame transformado.
    """
    print("✅ Cargando datos al destino...")
    print(df)
    print("✅ Carga completada.")
