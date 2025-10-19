Laboratorio - Algoritmos para Coordinación de Drones
Descripción General
Este proyecto implementa tres algoritmos para resolver problemas de coordinación y optimización con drones. Cada punto utiliza una técnica diferente inspirada en comportamientos naturales.

Punto 1: Show de Drones con Algoritmo PSO
Objetivo
Coordinar un enjambre de drones para formar figuras aéreas dinámicas (estrella, dragón, robot) reemplazando fuegos artificiales tradicionales.

Características Principales
25 drones en formación 3D

4 obstáculos esféricos para evitar

Tolerancia a fallos - el sistema se adapta si drones dejan de funcionar

Formaciones predefinidas:

Estrella: Figura geométrica de 8 puntas

Dragón: Forma sinuosa en espiral 3D

Robot: Figura humanoide con cabeza, cuerpo y extremidades

Implementación PSO
python
# Ecuaciones de movimiento PSO
velocidad = inercia * velocidad_actual + 
            componente_cognitivo + 
            componente_social
Inercia (w=0.7): Mantiene dirección actual

Componente cognitivo (c1=1.5): Atracción a mejor posición personal

Componente social (c2=1.5): Atracción a mejor posición global

Función de Fitness Multi-objetivo
python
fitness = distancia_al_objetivo + 
          penalización_por_colisiones + 
          penalización_por_obstáculos + 
          penalización_por_consumo_energético
Mecanismos de Seguridad
Evitación de colisiones: Fuerzas repulsivas entre drones

Evitación de obstáculos: Detección y desvío de esferas de colisión

Límites de velocidad: Máximo 0.5 unidades por iteración

Tolerancia a Fallos
Detección aleatoria: 2% de probabilidad por iteración

Adaptación automática: Reasignación de posiciones objetivo

Límite máximo: No más del 33% de drones pueden fallar

Punto 2: Rescate con Algoritmo ACO
Objetivo
Coordinar drones-hormiga para buscar supervivientes y recursos en zona de desastre post-terremoto.

Características Principales
8 drones exploradores

5 supervivientes y 5 recursos por rescatar

Obstáculos estáticos y dinámicos

Sistema de feromonas para optimización colectiva

Implementación ACO
python
atractividad = (1/distancia_al_objetivo) + 
               (feromona * 2.0) + 
               bonus_exploración
Comportamiento de los Drones-Hormiga
Exploración inicial: Movimiento aleatorio con bias hacia áreas no exploradas

Detección de objetivos: Supervivientes (prioridad alta) y recursos (prioridad media)

Regreso a base: Entrega de objetivos y recarga energética

Seguimiento de feromonas: Rutas exitosas atraen más drones

Sistema de Feromonas
Depósito: Drones dejan feromona en caminos recorridos

Evaporación: 5% de reducción por iteración

Intensidad: Inversamente proporcional a longitud del camino

Límite máximo: 50 unidades de feromona por celda

Obstáculos Dinámicos
Aparición: Cada 50 iteraciones (máximo 3 obstáculos)

Desaparición: Cada 80 iteraciones

Efecto: Bloquean completamente el paso

Función de Fitness
python
fitness = (cobertura_terreno * 0.4) + 
          (supervivientes_rescatados * 0.4) + 
          (recursos_recolectados * 0.2)
Punto 3: Polinización con Algoritmo ABC
Objetivo
Optimizar polinización en invernadero usando drones-abeja con roles especializados.

Características Principales
15 drones especializados:

8 obreras: Polinización directa

4 observadoras: Seguimiento de obreras exitosas

3 exploradoras: Búsqueda de nuevas flores

30 flores con madurez progresiva

5 estaciones de carga automática

Gestión inteligente de batería

Implementación ABC
Fase de Abejas Obreras
python
fitness_flor = (madurez * 30) + 
               (necesidad_polinización * 0.5) - 
               (distancia * 2)
Fase de Abejas Observadoras
Seguimiento de obreras más exitosas

Enfoque en flores maduras (madurez > 0.7)

Fase de Abejas Exploradoras
Búsqueda de flores no visitadas

Atención a flores con baja polinización

Sistema de Energía
Consumo: 0.8% por iteración en movimiento

Recarga automática: Al bajar del 20%

Estaciones: 5 puntos fijos de recarga

Bonus energético: +30% al recolectar recursos

Progresión de Flores
Madurez: Incremento de 1-3% por iteración

Polinización: +15% por visita exitosa

Estados:

Inmadura (madurez < 0.5): Verde

Madura (madurez > 0.8): Naranja

Completamente polinizada: Púrpura

Función de Fitness
python
fitness = (tasa_polinización * 0.5) + 
          (eficiencia * 0.2) + 
          (polinización_flores_maduras * 0.3)
Arquitectura Común
Estructura de Clases
text
Sistema Base
├── Entorno (Terreno/Invernadero)
├── Agentes (Drones)
├── Algoritmo Bioinspirado (PSO/ACO/ABC)
└── Visualización
Características Compartidas
Visualización en Tiempo Real

Gráficos 2D/3D actualizados dinámicamente

Métricas de performance en tiempo real

Leyendas y información de estado

Métricas de Evaluación

Fitness por iteración

Cobertura del área

Eficiencia operativa

Tiempo de convergencia

Parámetros Configurables

Número de agentes

Tamaño del entorno

Ratas de aprendizaje/exploración

Condiciones de terminación
