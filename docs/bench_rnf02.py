import sys, time, statistics
sys.path.insert(0, "src")
from inventario import ServicioInventario
s = ServicioInventario()
cats = ["Herramientas", "Plomería", "Electricidad", "Pintura", "Fijación"]
for i in range(5000):
    s.registrar_producto(f"P-{i:05d}", f"Tubería producto número {i}", cats[i % 5], "1.25", 3)
t = []
for _ in range(20):
    a = time.perf_counter(); r = s.buscar("NUMERO 49"); t.append(time.perf_counter() - a)
print(f"resultados={len(r)} mediana_ms={statistics.median(t)*1000:.1f} max_ms={max(t)*1000:.1f}")
