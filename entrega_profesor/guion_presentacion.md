# Guión de presentación — Proyecto de Título (15 minutos)
**Heuristic Approaches for the k-Traveling Salesman Problem: A Reproducible Comparison**
Autor: Nicolás Barrientos · Profesor guía: Dr. Gustavo Gatica · Universidad Andrés Bello

> Diapositivas en inglés · guión hablado en español. Total ≈ 15 min.
> El tiempo sugerido de cada diapositiva va entre paréntesis. No leas la diapositiva
> palabra por palabra; usa estas notas como apoyo. El PPT tiene 18 diapositivas.

---

## 1 — Portada (0:20)
"Buenos días. Soy Nicolás Barrientos y presento mi proyecto de título,
*Heuristic Approaches for the k-Traveling Salesman Problem: a Reproducible
Comparison*, guiado por el Dr. Gustavo Gatica. El trabajo fue enviado como paper al
congreso Optima 2025."

## 2 — Contexto y motivación (0:55)
"La optimización de rutas está en todas partes: logística, transporte, vigilancia.
El modelo clásico es el TSP, que busca la ruta cerrada más corta que visita todas
las ciudades. Pero muchos casos reales visitan solo un **subconjunto** de
ubicaciones, por un presupuesto de paradas. Ese es el **k-TSP**: elegir k de n
ciudades —con un depósito— y ordenarlas en un recorrido cerrado mínimo."

## 3 — Objetivos (0:50)
"El objetivo general: un repositorio reproducible que modela, resuelve y compara el
k-TSP contra la referencia LKH-3. Como específicos: formular el problema; implementar
**diez** métodos; evaluar la calidad con el GAP sobre 38 instancias y tres valores
de k; complementar con análisis anytime; y liberar todo para regenerarlo con un
comando."

## 4 — Metodología de trabajo (0:55)
"Cuatro etapas: diseño de datos, modelo matemático, resolución heurística —con los
diez métodos sobre un núcleo común de 2-opt, intercambio e inserción, lo que hace la
comparación justa— y evaluación experimental. Todo en Python, en VS Code, versionado
en un GitHub privado, con LKH-3 local; el tiempo se mide en evaluaciones de
distancia, independiente de la máquina."

## 5 — Asistencia a evento: Optima 2025 (0:25)
"El núcleo se escribió como paper y se **envió a Optima 2025**, en la Universidad
Católica del Norte, el 30 de noviembre de 2025; está en revisión. Es la contribución
central y se incluye como capítulo de la tesis."

## 6 — El problema de investigación (1:00)
"Formalmente: dadas n ciudades con depósito y un k fijo, buscar el recorrido cerrado
más corto que visita exactamente k ciudades. La dificultad está en **dos decisiones
acopladas**: *cuáles* k nodos y *en qué orden*. El número de combinaciones crece
combinatorialmente, así que se necesitan heurísticas. A la derecha, la representación
genotipo–fenotipo: subconjunto más orden que se decodifica en un recorrido."

## 7 — Modelo matemático (0:45)  [NUEVA]
"Este es el modelo formal. Las variables: x indica si un arco está en el tour, y si un
nodo se selecciona, y u son las variables de orden de Miller–Tucker–Zemlin. La función
objetivo minimiza la longitud total. Las restricciones fuerzan que el depósito esté,
que se visiten exactamente k nodos, el grado de cada nodo, y las MTZ eliminan
subtours. Deja explícitas las dos decisiones: selección (y) y orden (x)."

## 8 — Instancias y cuartiles (0:40)  [NUEVA]
"Usamos 38 instancias TSPLIB, con n de 48 a 442 ciudades. Cada instancia se prueba en
**tres valores de k**, como cuartiles de su tamaño: Q1 visita un cuarto —ahí manda la
selección—, Q2 la mitad, y Q3 tres cuartos —ahí se parece a un TSP normal—. Así son
38 × 3 = 114 casos de prueba, todos comparados contra LKH-3."

## 9 — Tabla de referencia: GAP promedio (1:00)
"Esta tabla resume el resultado central: el GAP promedio de cada método frente a
LKH-3, por cuartil; menor es mejor. **Greedy** y **Tabu Search** logran el menor GAP.
El genético mejora para k grande. Y **Farthest Insertion** es el peor, porque insertar
los nodos más lejanos choca con el objetivo de seleccionar nodos baratos."

## 10 — Resultados completos, parte 1/2 (0:25)  [NUEVA]
"Para transparencia, aquí están los resultados **por instancia** —la longitud de cada
recorrido por método—. En negrita, los que igualan el óptimo de LKH-3. Esta es la
primera mitad de las instancias."

## 11 — Resultados completos, parte 2/2 (0:20)  [NUEVA]
"Y la segunda mitad, hasta pcb442, la instancia más grande. Las tablas completas de
los tres cuartiles están en la tesis."

## 12 — Heurísticas (1/3): construcción (1:00)
"Los métodos de construcción: **Greedy** inserta el nodo más barato hasta k y refina.
**Nearest Neighbor** avanza al más cercano. **Nearest y Farthest Insertion** insertan
el más cercano o más lejano al tour. **Random Insertion** elige al azar con reinicios.
Todos comparten el mismo núcleo de búsqueda local."

## 13 — Heurísticas (2/3): metaheurísticas (1:00)
"Las metaheurísticas: **GRASP**, construcción aleatorizada más búsqueda local;
**genético**, evoluciona subconjunto y orden; **Simulated Annealing**, acepta
empeoramientos con probabilidad exp(-Δ/T) enfriando; y **Tabu Search**, búsqueda con
**memoria** que toma el mejor movimiento no prohibido. Tabu Search es la mejor de las
metaheurísticas."

## 14 — Heurísticas (3/3): DCIH, la propuesta (1:10)
"Mi propuesta: **DCIH**. Fase 1: selecciona y ordena por costo marginal mínimo,
rompiendo empates por índice. Fase 2: refina con 2-opt e intercambio. Es **totalmente
determinista**: mismos datos, mismo recorrido, sin azar. Prioriza correctitud y
reproducibilidad, con calidad comparable a GRASP y a las inserciones."

## 15 — Análisis de resultados (1/2): fin de corrida (1:10)
"En el resultado final: Greedy y Tabu Search dan el mejor GAP promedio, ~12,5%. El
genético cierra la brecha para k grande y gana en muchas instancias. Farthest
Insertion es el más débil. DCIH, determinista y de calidad comparable. En total,
diez métodos contra LKH-3."

## 16 — Análisis de resultados (2/2): anytime (1:20)
"Pero el final no lo dice todo. Con la metodología de Weise analizamos el
comportamiento **anytime**: la calidad a lo largo del tiempo, medido en evaluaciones
de distancia. El ranking global pone a **Nearest Neighbor primero**, porque llega muy
rápido a una buena solución. Pero NN es el más **rápido**, no el de mejor calidad
final. Esa distinción entre 'rápido' y 'mejor' es lo que permite ver esta metodología."

## 17 — Conclusiones y mejoras futuras (1:05)
"En conclusión: Greedy y Tabu Search, los más robustos, con TS como mejor
metaheurística; el genético destaca para k grande; Farthest Insertion, el más débil;
DCIH, opción determinista y reproducible. Como futuro: metaheurísticas híbridas,
ajuste de parámetros por instancia, reglas de selección dedicadas, e instancias más
grandes."

## 18 — Referencias (0:15)
"Estas son las referencias principales; la bibliografía completa, 50 referencias, está
en la tesis y el paper. Muchas gracias, quedo atento a sus preguntas."

---

## Preguntas probables (preparación)
- **¿Por qué NN queda primero en el ranking anytime pero no en calidad?**
  Porque el ranking anytime premia la *velocidad de convergencia* (ERT, ECDF): NN llega
  a algo decente con muy pocas evaluaciones. En calidad final queda a mitad de tabla.
  Son dos preguntas distintas: "¿quién es más rápido?" vs "¿quién llega más lejos?".
- **¿Por qué Farthest Insertion es tan malo aquí?**
  En el k-TSP hay que *seleccionar* nodos baratos de incluir; insertar los más lejanos
  va en contra de ese objetivo.
- **¿Qué aporta DCIH frente a Greedy?**
  Determinismo y reproducibilidad total; construcción única con desempate por índice y
  un refinamiento que también cambia el subconjunto.
- **¿Por qué evaluaciones de distancia y no segundos?**
  Para que la comparación no dependa del hardware ni del lenguaje (metodología de Weise).
- **¿Por qué LKH-3 como referencia?**
  Es uno de los mejores solvers para TSP; da los mejores valores conocidos del
  benchmark, cercanos al óptimo.
- **¿Qué representa el modelo matemático (variables x, y, u)?**
  x = arcos del tour, y = nodos seleccionados, u = orden (MTZ para evitar subtours).
  Deja explícitas las dos decisiones del k-TSP.
