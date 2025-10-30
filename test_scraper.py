"""
Script de prueba para verificar el scraper localmente
"""
from config import CREDENTIALS
from scraper import ejecutar_extraccion
from transformer import transformar_ordenes

def test_shine():
    print("=" * 50)
    print("Probando extracción de ShineAndBright...")
    print("=" * 50)

    try:
        creds = CREDENTIALS['ShineAndBright']
        print(f"Usuario: {creds['username']}")
        print("Extrayendo órdenes...")

        df_raw = ejecutar_extraccion(creds['username'], creds['password'])
        print(f"✅ Órdenes extraídas: {len(df_raw)} filas")

        print("Transformando datos...")
        df_final = transformar_ordenes(df_raw, 'ShineAndBright')
        print(f"✅ Órdenes procesadas: {len(df_final)} filas")

        print("\nPrimeras 5 órdenes:")
        print(df_final.head())

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_apex():
    print("\n" + "=" * 50)
    print("Probando extracción de Apex...")
    print("=" * 50)

    try:
        creds = CREDENTIALS['Apex']
        print(f"Usuario: {creds['username']}")
        print("Extrayendo órdenes...")

        df_raw = ejecutar_extraccion(creds['username'], creds['password'])
        print(f"✅ Órdenes extraídas: {len(df_raw)} filas")

        print("Transformando datos...")
        df_final = transformar_ordenes(df_raw, 'Apex')
        print(f"✅ Órdenes procesadas: {len(df_final)} filas")

        print("\nPrimeras 5 órdenes:")
        print(df_final.head())

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == '__main__':
    print("\n🧪 Test del scraper de SupplyPro\n")

    # Probar ShineAndBright
    shine_ok = test_shine()

    # Probar Apex
    apex_ok = test_apex()

    # Resumen
    print("\n" + "=" * 50)
    print("RESUMEN")
    print("=" * 50)
    print(f"ShineAndBright: {'✅ OK' if shine_ok else '❌ FALLO'}")
    print(f"Apex: {'✅ OK' if apex_ok else '❌ FALLO'}")
    print("=" * 50)
