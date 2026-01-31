# 🔮 Guía de Integración con OpenAI

## ¿Qué agrega la integración con OpenAI?

La integración con OpenAI GPT añade capacidades avanzadas de análisis que van más allá del sistema de reglas:

### 🎯 Funcionalidades Nuevas

#### 1. **Análisis Profundo con GPT**
- Análisis contextual considerando factores cualitativos
- Diagnóstico detallado del modelo
- Identificación de factores críticos
- Análisis de riesgo profundo
- Plan de acción priorizado con timeline

#### 2. **Generador de Reportes Profesionales**
Tres tipos de reportes automáticos:
- **Ejecutivo**: Para CEO y directores
- **Técnico**: Para equipo de operaciones
- **Inversionista**: Para presentar en pitch

Cada reporte incluye formato profesional en Markdown, listo para descargar.

#### 3. **Chat Asistente Inteligente**
- Responde preguntas en lenguaje natural
- Analiza escenarios what-if
- Explica métricas de forma educativa
- Contextual a tu simulación actual

#### 4. **Optimización Personalizada**
- Considera restricciones reales de tu negocio
- Optimización multi-objetivo
- Respeta limitaciones operativas
- Sugiere cambios implementables

---

## 📋 Requisitos

### Software
```bash
pip install openai>=1.12.0 python-dotenv>=1.0.0
```

### API Key de OpenAI
1. Regístrate en: https://platform.openai.com
2. Ve a: https://platform.openai.com/api-keys
3. Crea una nueva API key
4. Obtienes $5 USD gratis de crédito

---

## 🚀 Instalación y Configuración

### Opción 1: Variable de Entorno (Recomendado)

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Edita `.env` y agrega tu API key:
```
OPENAI_API_KEY=sk-proj-tu_api_key_real_aqui
```

3. El simulador detectará automáticamente la key

### Opción 2: Configuración en la UI

1. Ejecuta el simulador:
```bash
streamlit run app_cochino.py
```

2. En la barra lateral, expande "🔮 IA Avanzada (OpenAI)"

3. Pega tu API key en el campo

4. Click en "🔌 Conectar"

5. Verás "✅ Conectado" cuando esté listo

---

## 💰 Costos

### Modelo Usado: GPT-4o-mini
El más económico y potente de OpenAI.

### Precios por Uso
- **Análisis profundo**: ~$0.01-0.02 USD
- **Reporte profesional**: ~$0.02-0.03 USD  
- **Pregunta en chat**: ~$0.005-0.01 USD
- **Optimización**: ~$0.01-0.02 USD

### Estimado Mensual
| Uso | Análisis/mes | Costo Aprox |
|-----|--------------|-------------|
| **Ligero** | 10 análisis | $0.50 USD |
| **Moderado** | 50 análisis | $2-3 USD |
| **Intensivo** | 200 análisis | $10-15 USD |

**Nota**: Con $5 USD de crédito gratis puedes hacer ~250-500 análisis.

---

## 📖 Cómo Usar

### 1. Análisis Profundo

**Cuándo usar:**
- Quieres entender profundamente tus resultados
- Necesitas identificar factores no obvios
- Buscas un plan de acción detallado

**Pasos:**
1. Ejecuta tu simulación normalmente
2. Baja hasta "🔮 Análisis Avanzado con IA"
3. Tab "📊 Análisis Profundo"
4. Click en "🔍 Analizar con GPT"
5. Espera 5-10 segundos
6. Lee el análisis detallado

**Ejemplo de output:**
```
DIAGNÓSTICO:
Tu modelo SIDEPE presenta viabilidad moderada-alta con un ROI
del 15.2%. El principal cuello de botella es la utilización
de capital del 60%, dejando $160,000 ociosos...

FACTORES CRÍTICOS:
1. Utilización (60% vs 85% óptimo): Impacto -6% en ROI
2. Morosidad (8% vs 5% target): Impacto -3% en ROI
3. Distribución subóptima: Impacto -2% en ROI

PLAN DE ACCIÓN:
Mes 1: Implementar scoring crediticio...
```

### 2. Generar Reportes

**Cuándo usar:**
- Necesitas presentar a inversionistas
- Quieres documentación profesional
- Reunión con directivos

**Pasos:**
1. Tab "📄 Generar Reporte"
2. Selecciona tipo: Ejecutivo / Técnico / Inversionista
3. Click en "📄 Generar Reporte"
4. Espera 10-15 segundos
5. Descarga con "💾 Descargar Reporte"

**Tip**: Los reportes están en Markdown, puedes:
- Importar a Word/Google Docs
- Convertir a PDF con Pandoc
- Usar en presentaciones

### 3. Chat Asistente

**Cuándo usar:**
- Tienes preguntas específicas
- Quieres explorar escenarios
- Necesitas aclaraciones

**Ejemplos de preguntas:**
```
"¿Por qué mi ROI es bajo?"
"¿Qué pasa si duplico usuarios pero morosidad sube 2%?"
"Explica el impacto de cambiar distribución a 90% núcleo"
"¿Es viable crecer de 100 a 500 usuarios en 6 meses?"
"Compara mi modelo con una cooperativa tradicional"
```

**Pasos:**
1. Tab "💬 Chat Asistente"
2. Escribe tu pregunta
3. Click "💬 Enviar"
4. GPT responde en contexto
5. Puedes hacer seguimiento conversacional

### 4. Optimización Personalizada

**Cuándo usar:**
- Tienes restricciones específicas
- Necesitas plan realista
- Quieres optimización multi-objetivo

**Ejemplo de restricciones:**
```
- Solo puedo tener máximo 150 usuarios (capacidad)
- Capital inicial: $80,000
- Equipo de 2 personas
- No puedo aprobar más de 30 préstamos/mes
- Clientes: micro-empresarios zona rural
- Necesito mantener liquidez del 20%
```

**Pasos:**
1. Tab "🎯 Optimización Personalizada"
2. Describe tus restricciones
3. Click "🚀 Optimizar con GPT"
4. GPT sugiere parámetros optimizados
5. Ajusta en sidebar y simula de nuevo

---

## 🔒 Seguridad

### Tu API Key
- **Nunca** la compartas públicamente
- **Nunca** la incluyas en git (está en .gitignore)
- Usa variables de entorno o configuración UI
- Rótala periódicamente

### Datos de la Simulación
- Los datos se envían a OpenAI para análisis
- OpenAI **NO** entrena modelos con tus datos (por defecto)
- Conexión encriptada (HTTPS)
- Si manejas datos sensibles, revisa políticas de OpenAI

---

## 🐛 Solución de Problemas

### Error: "OpenAI no está instalado"
```bash
pip install openai python-dotenv
```

### Error: "API key no proporcionada"
- Verifica que copiaste la key completa
- Revisa archivo .env o configura en UI
- La key debe empezar con `sk-`

### Error: "No se pudo conectar"
- Verifica conexión a internet
- Revisa que la key sea válida
- Checa saldo en: https://platform.openai.com/usage

### Análisis muy lento
- Normal: 5-15 segundos
- Si toma >30s, verifica conexión
- Modelo gpt-4o-mini es el más rápido

### Costos inesperados
- Revisa uso en: https://platform.openai.com/usage
- Cada análisis muestra costo aproximado
- Desactiva cuando no uses

---

## 📊 Comparación: Reglas vs OpenAI

| Aspecto | Sistema de Reglas | Con OpenAI |
|---------|-------------------|------------|
| **Costo** | Gratis | ~$0.01-0.03/análisis |
| **Velocidad** | Instantáneo | 5-15 segundos |
| **Análisis** | Básico | Profundo |
| **Contexto** | Limitado | Comprende matices |
| **Reportes** | No | Sí, profesionales |
| **Chat** | No | Sí, conversacional |
| **Restricciones** | No considera | Sí, las respeta |
| **Educativo** | Limitado | Muy explicativo |

---

## 💡 Mejores Prácticas

### 1. Usa Sistema de Reglas Primero
- Haz análisis rápido con reglas (gratis)
- Usa OpenAI solo para análisis profundo
- Ahorra en costos

### 2. Sé Específico en Chat
❌ "¿Es bueno mi modelo?"
✅ "¿Es viable crecer de 100 a 300 usuarios con $50K de capital?"

### 3. Aprovecha Reportes
- Genera reporte antes de reuniones
- Personaliza con tus datos
- Descarga y edita si necesitas

### 4. Optimización con Contexto Real
- Describe restricciones reales
- Incluye contexto de mercado
- Sé honesto con limitaciones

---

## 🚀 Roadmap Futuro

### v2.1 (Próximo)
- [ ] Análisis de sentimiento en comentarios
- [ ] Comparación con benchmarks de industria
- [ ] Alertas proactivas por email

### v2.2
- [ ] Fine-tuning con datos históricos
- [ ] Predicciones con ML real
- [ ] Simulación de Monte Carlo

### v3.0
- [ ] Asistente de voz
- [ ] Generación de presentaciones (PPTX)
- [ ] Dashboard predictivo en tiempo real

---

## 📞 Soporte

**Problemas con OpenAI:**
- Documentación: https://platform.openai.com/docs
- Status: https://status.openai.com
- Soporte: https://help.openai.com

**Problemas con el Simulador:**
- Revisa GUIA_USO.md
- Consulta EJEMPLOS_IA.md
- Abre un issue en GitHub

---

## 🎓 Recursos Adicionales

- [OpenAI API Docs](https://platform.openai.com/docs)
- [GPT Best Practices](https://platform.openai.com/docs/guides/gpt-best-practices)
- [Pricing Calculator](https://openai.com/pricing)
- [Rate Limits](https://platform.openai.com/docs/guides/rate-limits)

---

**¡La integración con OpenAI eleva tu simulador a un consultor financiero 24/7!** 🚀
