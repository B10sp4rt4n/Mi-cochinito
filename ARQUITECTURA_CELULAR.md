# 🔬 Arquitectura Celular del Sistema SIDEPE

## Visión General

El sistema de ahorro colectivo SIDEPE ha evolucionado hacia una **arquitectura celular fractal** que permite:

- 🔬 **Células autorreguladas**: Cada nodo de ahorro puede autorregularse
- 🎯 **Detección de riesgo**: Sistema multinivel de análisis de riesgo
- 🏢 **Nodos consolidadores**: Estructura jerárquica que encapsula células
- 💎 **Múltiples fuentes de valor**: Intercambio flexible de valores
- 🌐 **Sistema cerrado o abierto**: Configuración adaptable

---

## 📐 Arquitectura del Sistema

### Estructura Fractal Jerárquica

```
┌─────────────────────────────────────────────────────────┐
│                    NODO MAESTRO                          │
│              (MasterNode - Sistema Completo)             │
│                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │  NODO CONSOLIDADOR 1 │  │  NODO CONSOLIDADOR 2 │   │
│  │   (Región/Grupo)     │  │   (Región/Grupo)     │   │
│  │                      │  │                      │   │
│  │  ┌────────┐         │  │  ┌────────┐         │   │
│  │  │CÉLULA 1│         │  │  │CÉLULA 3│         │   │
│  │  │ ┌───┐  │         │  │  │ ┌───┐  │         │   │
│  │  │ │Src│  │         │  │  │ │Src│  │         │   │
│  │  │ │Src│  │         │  │  │ │Src│  │         │   │
│  │  │ │Src│  │         │  │  │ │Src│  │         │   │
│  │  │ └───┘  │         │  │  │ └───┘  │         │   │
│  │  └────────┘         │  │  └────────┘         │   │
│  │                     │  │                     │   │
│  │  ┌────────┐        │  │  ┌────────┐        │   │
│  │  │CÉLULA 2│        │  │  │CÉLULA 4│        │   │
│  │  └────────┘        │  │  └────────┘        │   │
│  └──────────────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🧬 Componentes del Sistema

### 1. ValueSource (Fuente de Valor)

**Descripción**: Representa una fuente individual de aportación/inversión dentro de una célula.

**Atributos Principales**:
- `source_id`: Identificador único
- `initial_capital`: Capital inicial
- `monthly_contribution`: Aportación mensual
- `gpm_rate`: Tasa de crecimiento mensual (%)
- `utilization_rate`: Porcentaje de capital utilizado
- `risk_factor`: Factor de riesgo (0.5 - 1.5)

**Capacidades**:
- ✅ Cálculo automático de crecimiento
- ✅ Gestión de contribuciones
- ✅ Tracking de ganancias

**Ejemplo**:
```python
fuente_nucleo = ValueSource(
    source_id="SRC-NUCLEUS",
    name="Núcleo Productivo",
    initial_capital=0,
    monthly_contribution=42500,  # 50 usuarios * $850
    gpm_rate=2.5,  # 2.5% mensual
    utilization_rate=85.0,  # 85% del capital se utiliza
    risk_factor=0.95  # 5% de riesgo de default
)
```

---

### 2. SavingsCell (Célula de Ahorro)

**Descripción**: Unidad básica autorregulada del sistema. Contiene múltiples fuentes de valor y se autorregula según métricas de riesgo.

**Características**:

#### Estados Posibles:
- `ACTIVE`: Operando normalmente
- `RECOVERING`: En proceso de recuperación
- `SUSPENDED`: Suspendida temporalmente
- `INACTIVE`: Inactiva
- `CLOSED`: Cerrada permanentemente

#### Sistema de Autorregulación:
La célula monitorea constantemente:
- **Default Rate**: Tasa de morosidad
- **Utilization**: Nivel de utilización del capital
- **Concentration**: Concentración de riesgo
- **Volatility**: Volatilidad de rendimientos
- **Liquidity**: Riesgo de liquidez

#### Reglas de Regulación (RegulationRules):
```python
max_default_rate: 5.0%
min_utilization: 70.0%
max_utilization: 95.0%
min_liquidity_ratio: 10.0%
max_concentration_single_source: 40.0%
emergency_stop_threshold: 85.0%  # Score de riesgo
```

#### Acciones Automáticas:

| Nivel de Riesgo | Acción Automática |
|-----------------|-------------------|
| VERY_LOW / LOW  | Operación normal |
| MEDIUM         | Reducción moderada de utilización |
| HIGH           | Estado RECOVERING + Reducción 20% utilización |
| CRITICAL       | Estado SUSPENDED + Reducción 50% utilización |

**Ejemplo de Uso**:
```python
# Crear célula
cell = SavingsCell(
    cell_id="CELL-001",
    name="Grupo Norte A",
    num_members=50
)

# Agregar fuentes de valor
cell.add_value_source(fuente_fee)
cell.add_value_source(fuente_nucleo)
cell.add_value_source(fuente_fic)

# Simular un mes
resultado = cell.simulate_month(month=1)

# Consultar salud
health_score = cell.get_health_score()  # 0-100
```

---

### 3. ConsolidatorNode (Nodo Consolidador)

**Descripción**: Agrupa múltiples células y consolida sus métricas. Representa una región, grupo o división.

**Capacidades**:
- 📊 Consolidación de métricas de todas las células
- 🎯 Monitoreo de distribución de riesgo
- 📈 Análisis agregado de performance
- 🔍 Identificación de células problemáticas

**Métricas Consolidadas**:
- Balance total agregado
- Ganancia total consolidada
- Health score promedio
- Riesgo compuesto ponderado
- Distribución de células por nivel de riesgo

**Ejemplo**:
```python
consolidator = ConsolidatorNode(
    node_id="CON-NORTE",
    name="Región Norte"
)

# Agregar células
consolidator.add_cell(cell1)
consolidator.add_cell(cell2)
consolidator.add_cell(cell3)

# Simular mes para todo el grupo
resultado = consolidator.simulate_month(month=1)

# Obtener células agrupadas por riesgo
risk_distribution = consolidator.get_cells_by_risk()
# Resultado: {'VERY_LOW': ['CELL-001'], 'MEDIUM': ['CELL-002'], ...}
```

---

### 4. MasterNode (Nodo Maestro)

**Descripción**: Nivel superior del sistema. Encapsula todos los consolidadores y proporciona vista global.

**Capacidades**:
- 🌐 Vista global de todo el sistema
- 📊 Consolidación de métricas multinivel
- 🎛️ Simulación de múltiples períodos
- 💾 Exportación de datos y reportes
- 🔬 Análisis de riesgo sistémico

**Métricas Globales**:
- Balance total del sistema
- Ganancia total
- Health score del sistema
- Riesgo global compuesto
- Número total de células y consolidadores

**Ejemplo Completo**:
```python
# Crear sistema maestro
master = MasterNode("Sistema SIDEPE Nacional")

# Agregar consolidadores
master.add_consolidator(consolidator_norte)
master.add_consolidator(consolidator_sur)
master.add_consolidator(consolidator_centro)

# Simular 12 meses
resultados = master.simulate_multiple_months(12)

# Obtener reporte completo
reporte = master.get_system_report()

# Exportar a DataFrame
df = master.export_to_dataframe()
```

---

## 📊 Sistema de Detección de Riesgo

### Niveles de Riesgo

| Nivel | Score | Descripción | Color |
|-------|-------|-------------|-------|
| VERY_LOW | 0-20% | Riesgo mínimo, operación óptima | 🟢 |
| LOW | 20-40% | Riesgo bajo, monitoreo normal | 🟡 |
| MEDIUM | 40-60% | Riesgo moderado, precaución | 🟠 |
| HIGH | 60-80% | Riesgo alto, acciones correctivas | 🔴 |
| CRITICAL | 80-100% | Riesgo crítico, suspensión | ⚫ |

### Cálculo de Riesgo Compuesto

```python
Riesgo Compuesto = (
    default_rate * 35% +
    volatility * 20% +
    concentration_risk * 20% +
    liquidity_risk * 15% +
    operational_risk * 10%
)
```

### Indicadores de Riesgo

#### 1. Default Rate (Tasa de Morosidad)
- **Qué mide**: Porcentaje de préstamos en default
- **Rango óptimo**: < 5%
- **Peso**: 35%

#### 2. Volatility (Volatilidad)
- **Qué mide**: Variación en rendimientos mensuales
- **Cálculo**: Desviación estándar de últimos 3 meses
- **Peso**: 20%

#### 3. Concentration Risk (Riesgo de Concentración)
- **Qué mide**: % del balance en una sola fuente
- **Rango óptimo**: < 40%
- **Peso**: 20%

#### 4. Liquidity Risk (Riesgo de Liquidez)
- **Qué mide**: Capital no utilizado disponible
- **Rango óptimo**: > 10%
- **Peso**: 15%

#### 5. Operational Risk (Riesgo Operacional)
- **Qué mide**: Eficiencia operativa
- **Peso**: 10%

---

## 🎯 Health Score (Puntuación de Salud)

### Cálculo a Nivel de Célula

```python
Health Score = Base Risk Score * State Multiplier

Base Risk Score = 100 - Composite Risk

State Multipliers:
- ACTIVE: 1.0
- RECOVERING: 0.8
- SUSPENDED: 0.5
- INACTIVE: 0.3
- CLOSED: 0.0
```

### Interpretación

| Score | Categoría | Interpretación |
|-------|-----------|----------------|
| 90-100 | Excelente | Operación óptima |
| 75-89 | Bueno | Operación saludable |
| 60-74 | Aceptable | Requiere atención |
| 40-59 | Preocupante | Acciones correctivas necesarias |
| 0-39 | Crítico | Intervención inmediata |

---

## 🔄 Flujo de Simulación

### Por Mes

```
1. Agregar Contribuciones
   ↓
2. Calcular Crecimiento (cada fuente)
   ↓
3. Aplicar Factor de Riesgo
   ↓
4. Actualizar Métricas de Riesgo
   ↓
5. Verificar Violaciones de Reglas
   ↓
6. [SI HAY VIOLACIONES] → Autorregular
   ↓
7. Registrar en Historial
```

### Autorregulación

```
DETECTAR: Violación de reglas
   ↓
EVALUAR: Nivel de riesgo compuesto
   ↓
DECIDIR: Acción apropiada
   ├─ Riesgo CRITICAL → SUSPENDER + Reducir util. 50%
   ├─ Riesgo HIGH → RECOVERING + Reducir util. 20%
   └─ Riesgo MEDIUM → Ajustar moderadamente
   ↓
EJECUTAR: Aplicar cambios
   ↓
REGISTRAR: Log de violaciones
```

---

## 💡 Casos de Uso

### Caso 1: Sistema Regional con Múltiples Grupos

```python
# Sistema para 3 regiones, cada una con 5 grupos
master = MasterNode("SIDEPE Nacional")

for region in ["Norte", "Centro", "Sur"]:
    consolidator = ConsolidatorNode(f"CON-{region}", f"Región {region}")
    
    for i in range(5):
        cell = SavingsCell(f"CELL-{region}-{i}", f"Grupo {i}", 40)
        
        # 3 fuentes por célula
        cell.add_value_source(ValueSource("FEE", "Emergencia", 0, 2000, 0.5, 30))
        cell.add_value_source(ValueSource("NUC", "Núcleo", 0, 34000, 2.5, 85, 0.95))
        cell.add_value_source(ValueSource("FIC", "Inversión", 0, 2000, 1.8, 90))
        
        consolidator.add_cell(cell)
    
    master.add_consolidator(consolidator)

# Simular 2 años
resultados = master.simulate_multiple_months(24)
```

### Caso 2: Sistema Cerrado con Intercambio de Valores

```python
# Célula con múltiples fuentes intercambiables
cell = SavingsCell("CELL-001", "Grupo Multi-fuente", 50)

# Diferentes tipos de aportes
cell.add_value_source(ValueSource("CASH", "Efectivo", 50000, 25000, 1.5, 70))
cell.add_value_source(ValueSource("CRYPTO", "Cripto", 30000, 10000, 5.0, 80, 0.85))
cell.add_value_source(ValueSource("BONDS", "Bonos", 100000, 5000, 1.2, 95, 1.0))
cell.add_value_source(ValueSource("STOCKS", "Acciones", 20000, 8000, 3.5, 75, 0.90))

# El sistema auto-balancea según riesgo
for month in range(12):
    cell.simulate_month(month + 1)
```

### Caso 3: Simulación con Shocks Externos

```python
# Definir shocks para mes 6
shocks = {
    6: {
        "CON-NORTE": {
            "CELL-N1": {
                "SRC-NUCLEUS": {
                    "risk_factor_change": 0.8,  # Aumenta riesgo 20%
                    "gpm_change": 0.9  # Reduce rendimiento 10%
                }
            }
        }
    }
}

# Simular con shocks
resultados = master.simulate_multiple_months(12, shocks)
```

---

## 📈 Análisis y Reportes

### Exportación de Datos

```python
# 1. DataFrame con historial completo
df = master.export_to_dataframe()
df.to_csv("sistema_historial.csv")

# 2. Reporte JSON completo
reporte = master.get_system_report()
with open("reporte.json", "w") as f:
    json.dump(reporte, f, indent=2)

# 3. Estado de célula específica
cell_state = cell.export_state()
```

### Métricas Clave para Análisis

```python
# Balance y Ganancias
total_balance = master.get_total_balance()
total_profit = master.get_total_profit()

# Salud del Sistema
system_health = master.get_system_health()

# Distribución de Riesgo
for consolidator in master.consolidator_nodes.values():
    distribution = consolidator.get_cells_by_risk()
    print(f"{consolidator.name}: {distribution}")

# Historial de Violaciones
for cell in consolidator.cells.values():
    if cell.violations_log:
        print(f"Célula {cell.name} tuvo {len(cell.violations_log)} violaciones")
```

---

## 🚀 Ejecutar el Sistema

### Opción 1: Interfaz Streamlit

```bash
# Ejecutar aplicación web
streamlit run app_cellular.py
```

Características de la interfaz:
- ✅ Crear sistema personalizado
- ✅ Visualizar consolidadores y células
- ✅ Ejecutar simulaciones
- ✅ Gráficos interactivos
- ✅ Exportar reportes

### Opción 2: Script Python

```python
from cellular_architecture import create_example_system

# Cargar sistema pre-configurado
system = create_example_system()

# Simular
resultados = system.simulate_multiple_months(12)

# Analizar
reporte = system.get_system_report()
print(f"Balance: ${reporte['summary']['total_balance']:,.2f}")
print(f"Health: {reporte['summary']['system_health']:.1f}/100")
```

### Opción 3: Demo Automático

```bash
python cellular_architecture.py
```

---

## 🔧 Configuración Avanzada

### Reglas de Regulación Personalizadas

```python
custom_rules = RegulationRules(
    max_default_rate=3.0,  # Más estricto
    min_utilization=80.0,
    max_utilization=90.0,
    min_liquidity_ratio=15.0,
    max_concentration_single_source=30.0,
    emergency_stop_threshold=75.0
)

cell = SavingsCell(
    "CELL-001",
    "Grupo Conservador",
    50,
    regulation_rules=custom_rules
)
```

### Fuentes de Valor Dinámicas

```python
# Fuente con riesgo variable
class DynamicValueSource(ValueSource):
    def calculate_growth(self):
        # Ajustar GPM según condiciones externas
        adjusted_gpm = self.gpm_rate * market_conditions_factor
        utilized = self.current_balance * (self.utilization_rate / 100)
        return utilized * (adjusted_gpm / 100) * self.risk_factor
```

---

## 📚 Próximas Mejoras

### En Desarrollo
- [ ] Integración con OpenAI para predicciones de riesgo
- [ ] Sistema de alertas en tiempo real
- [ ] Dashboard en tiempo real con WebSockets
- [ ] API REST para integración externa
- [ ] Machine Learning para detección de anomalías

### Planeado
- [ ] Blockchain para trazabilidad
- [ ] Multi-moneda y conversión automática
- [ ] Simulaciones Monte Carlo
- [ ] Optimización automática de parámetros
- [ ] Análisis de escenarios "what-if"

---

## 🤝 Contribuir

Para agregar nuevas fuentes de valor, nodos o métricas:

1. Extender clases base en `cellular_architecture.py`
2. Implementar métodos requeridos
3. Agregar visualizaciones en `app_cellular.py`
4. Documentar en este archivo

---

## 📞 Soporte

Para preguntas o issues:
- GitHub: [B10sp4rt4n/Mi-cochinito](https://github.com/B10sp4rt4n/Mi-cochinito)
- Documentación: Ver archivos `GUIA_*.md`

---

**Versión**: 1.0  
**Última Actualización**: Febrero 2026  
**Autor**: Sistema SIDEPE
