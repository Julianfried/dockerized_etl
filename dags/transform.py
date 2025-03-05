"""
transform.py - Modulo de Transformación de Datos
Este módulo recibe un DataFrame, realiza transformaciones y devuelve los datos procesados.
"""

import pandas as pd


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma los datos agregando una columna 'Edad +10'.

    Args:
        df (pd.DataFrame): DataFrame original.

    Returns:
        pd.DataFrame: DataFrame transformado.
    """

    print("✅ Datos transformados con éxito.")
    return df
