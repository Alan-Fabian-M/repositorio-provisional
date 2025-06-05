# Sistema de Predicción Académica ML

Este sistema de Machine Learning está integrado con la API Flask para proporcionar predicciones y recomendaciones académicas.

## Estructura del Sistema

```
ml_system/
├── data/                  # Datos extraídos de la base de datos
├── modelos/               # Modelos entrenados (.pkl)
├── scripts/               # Scripts de extracción y entrenamiento
│   ├── standalone_data_extractor.py  # Extractor de datos PostgreSQL
│   └── train_models_fixed.py         # Entrenamiento de modelos
├── tests/                 # Tests de integración
├── docs/                  # Documentación
├── setup_ml.py            # Script de configuración original
├── setup_ml_new.py        # Script de configuración mejorado
└── test_ml_pipeline.py    # Test completo del pipeline
```

## Modelos ML Implementados

1. **Predicción de Inscripción**: Predice la probabilidad de que un estudiante se inscriba basado en su edad y datos demográficos.
   - Algoritmo: Random Forest Classifier
   - Precisión: ~64%

2. **Recomendación de Cursos**: Recomienda cursos apropiados basados en la edad y preferencias del estudiante.
   - Algoritmo: Random Forest Classifier
   - Precisión: ~100%

3. **Predicción de Rendimiento**: Predice el rendimiento académico del estudiante.
   - Algoritmo: Random Forest Regressor
   - MSE: ~82.25
   - R²: ~0.051

## Configuración del Sistema

Para configurar el sistema completo, ejecute:

```bash
python ml_system/setup_ml_new.py
```

Esto realizará:
1. Instalación de dependencias
2. Extracción de datos
3. Entrenamiento de modelos
4. Pruebas de integración

## Uso de la API

### Predicción de Inscripción

```
POST /ml/predict/enrollment
{
    "edad": 16
}
```

### Recomendación de Cursos

```
POST /ml/recommend/courses
{
    "edad": 16,
    "turno_preferencia": "Mañana"
}
```

### Predicción de Rendimiento

```
POST /ml/predict/performance
{
    "edad": 16
}
```

### Estado del Sistema

```
GET /ml/health
```

### Información de Modelos

```
GET /ml/models/status
```

## Testing

Para ejecutar una prueba completa del pipeline ML:

```bash
python ml_system/test_ml_pipeline.py
```

## Integración con la Aplicación Flask

El sistema ML está integrado con la aplicación Flask a través del blueprint `ml_bp`, que se registra en la aplicación principal.

## Mantenimiento

- **Reentrenamiento de modelos**: `python ml_system/scripts/train_models_fixed.py`
- **Extracción de datos**: `python ml_system/scripts/standalone_data_extractor.py`

---

© 2025 Sistema de Aula Inteligente
