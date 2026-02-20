from models import ArizaSinifi, ArizaTipi

print("🔍 ARIZA SINIFLARI:")
for sinif in ArizaSinifi:
    print(f"  - {sinif.value}")

print("\n🔍 ARIZA TIPLERI:")
for tip in ArizaTipi:
    print(f"  - {tip.value}")
