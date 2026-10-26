# Guión de presentación — Proyecto de Título (15 minutos)
**Heuristic Approaches for the k-Traveling Salesman Problem: A Reproducible Comparison**
Autor: Nicolás Barrientos · Profesor guía: Dr. Gustavo Gatica · Universidad Andrés Bello

> Diapositivas en inglés · guión hablado en español. Total ≈ 15 min.
> El tiempo sugerido de cada diapositiva va entre paréntesis. No leas la diapositiva
> palabra por palabra; usa estas notas como apoyo. El PPT tiene 17 diapositivas
> (portada + 16). Resultados bajo el protocolo de Pandiri & Singh (OPSEARCH 2020).

---

## Portada (0:20)
"Buenos días. Soy Nicolás Barrientos y presento mi proyecto de título,
*Heuristic Approaches for the k-Traveling Salesman Problem: a Reproducible
Comparison*, guiado por el Dr. Gustavo Gatica."

## 1 — Contexto y motivación (0:55)
"La optimización de rutas está en todas partes: logística, transporte, vigilancia.
El modelo clásico es el TSP, que busca la ruta cerrada más corta que visita todas
las ciudades. Pero muchos casos reales visitan solo un **subconjunto** de
ubicaciones, por un presupuesto de paradas. Ese es el **k-TSP**: elegir k de n
ciudades —con un depósito— y ordenarlas en un recorrido cerrado mínimo."

## 2 — Objetivos (0:50)
"El objetivo general: un repositorio reproducible que modela, resuelve y compara el
k-TSP contra la referencia LKH-3. Como específicos: formular el problema; implementar
**diez** métodos; evaluar la calidad con el GAP sobre las **76 instancias de Pandiri
& Singh** y tres valores de k; **comparar estadísticamente** contra sus métodos
publicados con el test de Wilcoxon; y liberar todo para regenerarlo con un comando."

## 3 — Metodología de trabajo (0:55)
"Cuatro etapas: diseño de datos, modelo matemático, resolución heurística —con los
diez métodos sobre un núcleo común de 2-opt, intercambio e inserción, lo que hace la
comparación justa— y evaluación experimental. Todo en Python, en VS Code, versionado
en un GitHub privado, con LKH-3 local. La evaluación sigue el protocolo de Pandiri &
Singh: límites de tiempo por reloj y el test de Wilcoxon."

## 4 — El problema de investigación (1:00)
"Formalmente: dadas n ciudades con depósito y un k fijo, buscar el recorrido cerrado
más corto que visita exactamente k ciudades. La dificultad está en **dos decisiones
acopladas**: *cuáles* k nodos y *en qué orden*. El número de combinaciones crece
combinatorialmente, así que se necesitan heurísticas. A la derecha, la representación
genotipo–fenotipo: subconjunto más orden que se decodifica en un recorrido."

## 5 — Modelo matemático (0:50)
"Este es el modelo formal. Las variables: x indica si un arco está en el tour, y si un
nodo se selecciona, y u son las variables de orden de Miller–Tucker–Zemlin. La función
objetivo minimiza la longitud total. Las restricciones fuerzan que el depósito esté,
que se visiten exactamente k nodos, el grado de cada nodo, y las MTZ eliminan
subtours. Deja explícitas las dos decisiones: selección (y) y orden (x)."

## 6 — Benchmark y protocolo (0:55)
"Para que la comparación sea directa con el estado del arte, sigo **el mismo protocolo
de Pandiri & Singh**, publicado en OPSEARCH. Son **76 instancias de TSPLIB**, de 14 a
783 ciudades. Cada una se prueba en **tres valores de k**: Small (un cuarto, donde
manda la selección), Medium (la mitad) y Large (tres cuartos, casi un TSP normal). Dos
límites de tiempo de reloj: **short run 0,05·n segundos** y **long run 0,2·n segundos**,
con 10 ejecuciones cada uno. En total, 76 × 3 = 228 casos, todos comparados contra LKH-3."

## 7 — Resultados: GAP por escenario (1:10)
"Este gráfico resume el resultado central: el GAP promedio frente a LKH-3 por escenario,
a la izquierda el short run y a la derecha el long run; menor es mejor. Las barras claras
son mis métodos; las rayadas, GVNS y las hiper-heurísticas de Pandiri & Singh. Lo clave:
**Greedy y Tabu Search son los más robustos** y **le ganan claramente a su GVNS**. El
genético mejora bastante con más tiempo, sobre todo para k grande. Farthest Insertion
es el peor, porque insertar los nodos más lejanos choca con el objetivo de seleccionar
nodos baratos."

## 8 — Comparación con el estado del arte (1:15)
"Aquí ordeno todos los métodos por GAP promedio global, sobre las 76 instancias, los
tres k y ambos tiempos. Las dos hiper-heurísticas de Pandiri —HH\_RAND y HH\_GREEDY—
quedan primeras, pero **mi Greedy (8,1%) y mi Tabu Search (8,8%) quedan justo detrás**,
y ambos **superan a su GVNS (16,2%)**. Contando caso por caso, mi mejor método **iguala
o supera al mejor de Pandiri en 103 de 228 casos** en el short run, y a HH\_GREEDY en
123 de 228. O sea: heurísticas simples y reproducibles, competitivas con metaheurísticas
dedicadas en su propio benchmark."

## 9 — Significancia estadística (Wilcoxon) (1:10)
"Para no quedarnos en promedios, apliqué el **test de Wilcoxon** de rangos con signo,
pareado por instancia —el mismo que usa Pandiri—. El resultado: **Greedy y Tabu Search
son significativamente mejores que GVNS** (p < 0,05), en short y long run. En el short
run, mi Greedy incluso **le gana a HH\_GREEDY**, y Tabu Search lo empata. HH\_RAND se
mantiene como el más fuerte, sobre todo en long run. El boxplot muestra la distribución
del GAP por instancia: Greedy y TS tienen las cajas más compactas entre mis métodos."

## 10 — Heurísticas (1/3): construcción (1:00)
"Los métodos de construcción: **Greedy** inserta el nodo más barato hasta k y refina.
**Nearest Neighbor** avanza al más cercano. **Nearest y Farthest Insertion** insertan
el más cercano o más lejano al tour. **Random Insertion** elige al azar con reinicios.
Todos comparten el mismo núcleo de búsqueda local."

## 11 — Heurísticas (2/3): metaheurísticas (1:00)
"Las metaheurísticas: **GRASP**, construcción aleatorizada más búsqueda local;
**genético**, evoluciona subconjunto y orden; **Simulated Annealing**, acepta
empeoramientos con probabilidad exp(-Δ/T) enfriando; y **Tabu Search**, búsqueda con
**memoria** que toma el mejor movimiento no prohibido. Tabu Search es la mejor de mis
metaheurísticas."

## 12 — Heurísticas (3/3): DCIH, la propuesta (1:10)
"Mi propuesta: **DCIH**. Fase 1: selecciona y ordena por costo marginal mínimo,
rompiendo empates por índice. Fase 2: refina con 2-opt e intercambio. Es **totalmente
determinista**: mismos datos, mismo recorrido, sin azar. Prioriza correctitud y
reproducibilidad, con calidad comparable a GRASP y a las inserciones."

## 13 — Resultados (1/2): comparación global (1:00)
"En resumen: Greedy (~8%) y Tabu Search son los más robustos; ambos **significativamente
mejores que GVNS** por Wilcoxon, y competitivos con las hiper-heurísticas de Pandiri en
su mismo benchmark y protocolo. El genético cierra la brecha para k grande; Farthest
Insertion es el más débil; DCIH es la opción determinista y reproducible. En total, diez
métodos contra LKH-3 y contra el estado del arte."

## 14 — Resultados (2/2): efecto del presupuesto de tiempo (1:10)
"Aquí se ve el efecto de dar más tiempo: el GAP promedio por método en short versus long
run. Los métodos **deterministas (NN, NI, FI, DCIH) no cambian**, porque construyen una
sola vez. Los que usan el tiempo sí mejoran: el **genético es el que más gana** y pasa a
ser el mejor de mis métodos en el escenario Large bajo long run. Greedy y Tabu Search se
mantienen robustos en ambos presupuestos."

## 15 — Conclusiones y mejoras futuras (1:05)
"En conclusión: Greedy y Tabu Search, los más robustos, y ambos le ganan a GVNS de forma
significativa; mi trabajo es competitivo con las hiper-heurísticas de Pandiri en su
propio benchmark; el genético destaca para k grande; Farthest Insertion es el más débil;
y DCIH es una opción determinista y reproducible. Como futuro: metaheurísticas híbridas,
ajuste de parámetros por instancia, reglas de selección dedicadas e instancias más grandes."

## 16 — Referencias (0:15)
"Estas son las referencias principales; la bibliografía completa, 50 referencias, está
en la tesis y el paper. Muchas gracias, quedo atento a sus preguntas."

---

## Preguntas probables (preparación)
- **¿Por qué adoptaste el protocolo de Pandiri & Singh?**
  Porque publicaron el k-TSP en OPSEARCH con ese benchmark de 76 instancias y ese
  protocolo de tiempo (0,05n / 0,2n s, 10 corridas, Wilcoxon). Usar lo mismo hace la
  comparación directa y justa, y es a dónde apunto el paper.
- **¿Le ganas al estado del arte?**
  No en todo: las hiper-heurísticas HH\_RAND/HH\_GREEDY siguen siendo las más fuertes.
  Pero mi Greedy y mi Tabu Search **superan significativamente a su GVNS** y, en el short
  run, igualan o superan a HH\_GREEDY. El aporte es una comparación reproducible de diez
  métodos, competitiva con metaheurísticas dedicadas.
- **¿Por qué Greedy, tan simple, va tan bien?**
  Porque en el k-TSP elegir nodos baratos de incluir y refinar localmente es muy efectivo,
  sobre todo con k pequeño donde domina la selección.
- **¿Qué significa el test de Wilcoxon y por qué lo usas?**
  Es una prueba no paramétrica pareada que compara dos métodos sobre muchas instancias sin
  suponer normalidad. La usé porque es la que usa Pandiri y porque antes faltaba un análisis
  estadístico; confirma que mis diferencias con GVNS son significativas.
- **¿Por qué los deterministas no cambian entre short y long run?**
  Porque NN, NI, FI y DCIH construyen una sola solución; darles más tiempo no la cambia.
  Solo las metaheurísticas y Greedy (con reinicios) aprovechan el tiempo extra.
- **¿Por qué Farthest Insertion es tan malo aquí?**
  En el k-TSP hay que *seleccionar* nodos baratos de incluir; insertar los más lejanos va
  en contra de ese objetivo.
- **¿Qué aporta DCIH frente a Greedy?**
  Determinismo y reproducibilidad total: construcción única con desempate por índice y un
  refinamiento que también cambia el subconjunto.
- **¿Por qué LKH-3 como referencia?**
  Es uno de los mejores solvers para TSP; da los mejores valores conocidos del benchmark,
  cercanos al óptimo.
- **¿Qué representa el modelo matemático (variables x, y, u)?**
  x = arcos del tour, y = nodos seleccionados, u = orden (MTZ para evitar subtours).
