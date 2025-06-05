"""
Extractor de datos adaptado para la estructura de BD actual del proyecto
Mapea los nombres de tablas y campos para compatibilidad con el sistema ML
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
from datetime import datetime

class DataExtractorAdaptado:
    def __init__(self):
        # Usar la URL de tu base de datos actual
        self.db_url = 'postgresql://escuela_8lcq_user:kpuXPA7k4xYFmTNQqBIeW8tQmg1wgzBc@dpg-d0uqvbeuk2gs739bo2ng-a.oregon-postgres.render.com/escuela_8lcq'
        self.engine = create_engine(self.db_url)
        
        # Mapeo de nombres de tablas (BD actual -> Esperado por ML)
        self.tabla_mapping = {
            'estudiante': 'estudiantes',
            'evaluacion': 'evaluaciones', 
            'materia': 'materias',
            'gestion': 'periodos',
            'tipo_evaluacion': 'tipoevaluaciones'
        }
        
        # Mapeo de campos
        self.campo_mapping = {
            'estudiante': {
                'ci': 'id',
                'nombreCompleto': 'nombre',
                'fechaNacimiento': 'fecha_nacimiento'
            },
            'evaluacion': {
                'estudiante_ci': 'estudiante_id',
                'nota': 'valor',
                'gestion_id': 'periodo_id'
            }
        }
    
    def verificar_estado_actual(self):
        """Verifica el estado actual de los datos en tu BD"""
        print("🔍 VERIFICANDO ESTADO ACTUAL DE LA BASE DE DATOS")
        print("=" * 50)
        
        try:
            # Estadísticas de tu estructura actual
            queries = {
                'estudiantes': "SELECT COUNT(*) as total FROM estudiante",
                'evaluaciones': "SELECT COUNT(*) as total FROM evaluacion", 
                'estudiantes_con_eval': "SELECT COUNT(DISTINCT estudiante_ci) as total FROM evaluacion",
                'materias': "SELECT COUNT(*) as total FROM materia",
                'gestiones': "SELECT COUNT(*) as total FROM gestion",
                'tipos_evaluacion': "SELECT COUNT(*) as total FROM tipo_evaluacion"
            }
            
            for descripcion, query in queries.items():
                try:
                    result = pd.read_sql_query(query, self.engine)
                    print(f"   📊 {descripcion}: {result['total'].iloc[0]:,}")
                except Exception as e:
                    print(f"   ❌ Error en {descripcion}: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando estado: {e}")
            return False
    
    def extraer_estudiantes_adaptado(self):
        """Extrae estudiantes adaptando los nombres de campos"""
        print("📊 Extrayendo datos de estudiantes...")
        
        try:
            # Query adaptada a tu estructura
            query_estudiantes = """
            SELECT 
                e.ci as estudiante_id,
                e."nombreCompleto" as nombre,
                '' as apellido,  -- Campo faltante, usar vacío
                'N/A' as genero,  -- Campo faltante, usar N/A
                CASE 
                    WHEN e."fechaNacimiento" IS NOT NULL 
                    THEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM e."fechaNacimiento")
                    ELSE 18 
                END as edad
            FROM estudiante e
            WHERE e.ci IN (
                SELECT DISTINCT estudiante_ci 
                FROM evaluacion 
                WHERE nota IS NOT NULL
            )
            ORDER BY e.ci
            """
            
            df_estudiantes = pd.read_sql_query(query_estudiantes, self.engine)
            print(f"   ✅ {len(df_estudiantes)} estudiantes con evaluaciones")
            
            return df_estudiantes
            
        except Exception as e:
            print(f"❌ Error extrayendo estudiantes: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extraer_evaluaciones_adaptado(self):
        """Extrae evaluaciones adaptando los nombres de campos"""
        print("📊 Extrayendo datos de evaluaciones...")
        
        try:
            # Query adaptada a tu estructura
            query_evaluaciones = """
            SELECT 
                ev.estudiante_ci as estudiante_id,
                ev.materia_id,
                ev.gestion_id as periodo_id,
                te.nombre as tipo_evaluacion,
                AVG(ev.nota) as promedio_valor,
                COUNT(ev.id) as cantidad_evaluaciones,
                MIN(ev.nota) as valor_minimo,
                MAX(ev.nota) as valor_maximo,
                STDDEV(ev.nota) as desviacion_estandar
            FROM evaluacion ev
            INNER JOIN tipo_evaluacion te ON ev.tipo_evaluacion_id = te.id
            WHERE ev.nota IS NOT NULL
            GROUP BY ev.estudiante_ci, ev.materia_id, ev.gestion_id, te.id, te.nombre
            ORDER BY ev.estudiante_ci, ev.materia_id, ev.gestion_id
            """
            
            df_evaluaciones = pd.read_sql_query(query_evaluaciones, self.engine)
            print(f"   ✅ {len(df_evaluaciones)} registros de evaluaciones agrupadas")
            
            return df_evaluaciones
            
        except Exception as e:
            print(f"❌ Error extrayendo evaluaciones: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extraer_metadatos_adaptado(self):
        """Extrae metadatos adaptando los nombres"""
        print("📊 Extrayendo metadatos...")
        
        try:
            # Materias
            query_materias = "SELECT id, nombre FROM materia ORDER BY id"
            df_materias = pd.read_sql_query(query_materias, self.engine)
            
            # Gestiones (periodos)
            query_periodos = """
            SELECT 
                id, 
                CONCAT(anio, ' - ', periodo) as nombre,
                anio,
                periodo
            FROM gestion 
            ORDER BY id
            """
            df_periodos = pd.read_sql_query(query_periodos, self.engine)
            
            # Tipos de evaluación
            query_tipos = "SELECT id, nombre FROM tipo_evaluacion ORDER BY id"
            df_tipos = pd.read_sql_query(query_tipos, self.engine)
            
            print(f"   ✅ {len(df_materias)} materias, {len(df_periodos)} períodos, {len(df_tipos)} tipos evaluación")
            
            return df_materias, df_periodos, df_tipos
            
        except Exception as e:
            print(f"❌ Error extrayendo metadatos: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None
    
    def crear_dataset_completo_adaptado(self):
        """Crea el dataset completo adaptado a tu estructura"""
        print("\n🚀 CREANDO DATASET COMPLETO ADAPTADO")
        print("=" * 60)
        
        # Verificar estado
        if not self.verificar_estado_actual():
            return False
        
        # Extraer datos
        df_estudiantes = self.extraer_estudiantes_adaptado()
        df_evaluaciones = self.extraer_evaluaciones_adaptado()
        df_materias, df_periodos, df_tipos = self.extraer_metadatos_adaptado()
        
        if any(df is None for df in [df_estudiantes, df_evaluaciones, df_materias, df_periodos]):
            print("❌ Error en extracción de datos")
            return False
        
        try:
            print("🔄 Procesando y combinando datos...")
            
            # Crear tabla pivot para tipos de evaluación
            df_pivot = df_evaluaciones.pivot_table(
                index=['estudiante_id', 'materia_id', 'periodo_id'],
                columns='tipo_evaluacion',
                values='promedio_valor',
                fill_value=0,
                aggfunc='mean'
            ).reset_index()
            
            # Aplanar nombres de columnas
            df_pivot.columns.name = None
            
            # Renombrar columnas de tipos de evaluación
            tipo_cols = [col for col in df_pivot.columns if col not in ['estudiante_id', 'materia_id', 'periodo_id']]
            for col in tipo_cols:
                new_name = f"promedio_{col.lower().replace(' ', '_').replace('-', '_')}"
                df_pivot.rename(columns={col: new_name}, inplace=True)
            
            # Combinar con estudiantes
            df_final = df_pivot.merge(df_estudiantes, on='estudiante_id', how='left')
            
            # Combinar con materias
            df_final = df_final.merge(df_materias, left_on='materia_id', right_on='id', how='left')
            df_final.rename(columns={'nombre': 'materia_nombre'}, inplace=True)
            df_final.drop('id', axis=1, inplace=True)
            
            # Combinar con períodos
            df_final = df_final.merge(df_periodos, left_on='periodo_id', right_on='id', how='left')
            df_final.rename(columns={'nombre': 'periodo_nombre'}, inplace=True)
            df_final.drop('id', axis=1, inplace=True)
            
            # Crear características derivadas
            print("🧮 Creando características derivadas...")
            
            # Características básicas
            tipo_columns = [col for col in df_final.columns if col.startswith('promedio_')]
            
            if len(tipo_columns) > 0:
                df_final['promedio_notas_anterior'] = df_final[tipo_columns].mean(axis=1)
                df_final['variabilidad_notas'] = df_final[tipo_columns].std(axis=1).fillna(0)
                df_final['nota_maxima'] = df_final[tipo_columns].max(axis=1)
                df_final['nota_minima'] = df_final[tipo_columns].min(axis=1)
            else:
                df_final['promedio_notas_anterior'] = 70.0  # Valor por defecto
                df_final['variabilidad_notas'] = 0.0
                df_final['nota_maxima'] = 70.0
                df_final['nota_minima'] = 70.0
            
            # Características de asistencia (simuladas si no tienes datos reales)
            df_final['porcentaje_asistencia'] = np.random.normal(85, 10, len(df_final))
            df_final['porcentaje_asistencia'] = np.clip(df_final['porcentaje_asistencia'], 0, 100)
            
            # Características de participación (basadas en notas si no tienes datos)
            df_final['promedio_participacion'] = df_final['promedio_notas_anterior'] + np.random.normal(0, 5, len(df_final))
            df_final['promedio_participacion'] = np.clip(df_final['promedio_participacion'], 0, 100)
            
            # Variables categóricas
            df_final['genero_masculino'] = (df_final['genero'] == 'M').astype(int)
            df_final['turno_mañana'] = 1  # Valor por defecto
            df_final['nivel_secundaria'] = 1  # Valor por defecto
            
            # Variable objetivo
            df_final['nota_final_real'] = df_final['promedio_notas_anterior']
            
            # Categorización del rendimiento
            df_final['rendimiento_categoria'] = pd.cut(
                df_final['nota_final_real'],
                bins=[0, 60, 80, 100],
                labels=['Bajo', 'Medio', 'Alto'],
                include_lowest=True
            )
            
            # Limpiar datos
            df_final = df_final.dropna(subset=['nota_final_real', 'rendimiento_categoria'])
            
            # Guardar dataset
            output_path = 'dataset_estudiantes_adaptado.csv'
            df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"✅ Dataset creado: {output_path}")
            print(f"   📊 Registros totales: {len(df_final):,}")
            print(f"   👥 Estudiantes únicos: {df_final['estudiante_id'].nunique():,}")
            print(f"   📚 Materias únicas: {df_final['materia_id'].nunique():,}")
            print(f"   📅 Períodos únicos: {df_final['periodo_id'].nunique():,}")
            
            # Mostrar distribución de categorías
            print("\n📈 Distribución de rendimiento:")
            distribucion = df_final['rendimiento_categoria'].value_counts()
            for categoria, cantidad in distribucion.items():
                porcentaje = (cantidad / len(df_final)) * 100
                print(f"   {categoria}: {cantidad:,} ({porcentaje:.1f}%)")
            
            # Mostrar estadísticas básicas
            print(f"\n📊 Estadísticas de notas:")
            print(f"   Promedio: {df_final['nota_final_real'].mean():.2f}")
            print(f"   Mediana: {df_final['nota_final_real'].median():.2f}")
            print(f"   Desv. Est.: {df_final['nota_final_real'].std():.2f}")
            print(f"   Rango: {df_final['nota_final_real'].min():.1f} - {df_final['nota_final_real'].max():.1f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando dataset: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generar_reporte_extraccion(self):
        """Genera un reporte de la extracción"""
        print("\n📋 GENERANDO REPORTE DE EXTRACCIÓN...")
        
        reporte = f"""
=== REPORTE DE EXTRACCIÓN ADAPTADA ===
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ADAPTACIONES REALIZADAS:
- Mapeo de tabla 'estudiante' -> 'estudiantes'
- Mapeo de tabla 'evaluacion' -> 'evaluaciones'  
- Mapeo de tabla 'gestion' -> 'periodos'
- Mapeo de campo 'ci' -> 'estudiante_id'
- Mapeo de campo 'nota' -> 'valor'
- Mapeo de campo 'gestion_id' -> 'periodo_id'

CARACTERÍSTICAS GENERADAS:
- promedio_notas_anterior: Basado en evaluaciones reales
- porcentaje_asistencia: Simulado (85% ± 10%)
- promedio_participacion: Derivado de notas
- Variables demográficas: Edad calculada, género simulado
- Variable objetivo: nota_final_real

ESTRUCTURA DE SALIDA:
- Archivo: dataset_estudiantes_adaptado.csv
- Compatible con entrenador ML existente
- Mismas características esperadas por prediction_service

PRÓXIMOS PASOS:
1. Ejecutar model_trainer.py con el nuevo dataset
2. Verificar que los modelos se entrenan correctamente
3. Integrar con el servicio de predicción
4. Probar endpoints de ML

=== FIN DEL REPORTE ===
"""
        
        try:
            with open('reporte_extraccion_adaptada.txt', 'w', encoding='utf-8') as f:
                f.write(reporte)
            
            print("✅ Reporte guardado: reporte_extraccion_adaptada.txt")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
            return False


def main():
    """Función principal"""
    print("🔄 INICIANDO EXTRACCIÓN ADAPTADA DE DATOS")
    print("=" * 60)
    
    extractor = DataExtractorAdaptado()
    
    if extractor.crear_dataset_completo_adaptado():
        extractor.generar_reporte_extraccion()
        print("\n🎉 EXTRACCIÓN COMPLETADA EXITOSAMENTE")
        print("📁 Archivos generados:")
        print("   - dataset_estudiantes_adaptado.csv")
        print("   - reporte_extraccion_adaptada.txt")
        print("\n📋 Siguiente paso: Ejecutar entrenamiento con:")
        print("   python model_trainer_adaptado.py")
        return True
    else:
        print("\n❌ ERROR EN LA EXTRACCIÓN")
        print("🔧 Revisar logs y conexión a base de datos")
        return False


if __name__ == "__main__":
    main()
