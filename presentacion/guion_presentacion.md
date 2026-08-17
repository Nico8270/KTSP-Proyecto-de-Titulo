# Guión de presentación — Proyecto de Título (15 minutos)
**Heuristic Approaches for the k-Traveling Salesman Problem: A Reproducible Comparison**
Autor: Nicolás Barrientos · Profesor guía: Dr. Gustavo Gatica · Universidad Andrés Bello

> Diapositivas en inglés · guión hablado en español.
> Tiempo total ≈ 15 min. El tiempo sugerido de cada diapositiva va entre paréntesis.
> Consejo: no leas la diapositiva palabra por palabra; usa estas notas como apoyo.

---

## Diapositiva 1 — Portada (0:20)
"Buenos días. Mi nombre es Nicolás Barrientos y presentaré mi proyecto de título,
titulado *Heuristic Approaches for the k-Traveling Salesman Problem: a Reproducible
Comparison*, desarrollado bajo la guía del Dr. Gustavo Gatica. El trabajo, además,
fue enviado como paper al congreso Optima 2025."

## Diapositiva 2 — Contexto y motivación (1:00)
"La optimización de rutas está en todas partes: logística, transporte, vigilancia,
planificación de recursos. El modelo clásico es el *Traveling Salesman Problem*, que
busca la ruta cerrada más corta que visita todas las ciudades.
Pero en muchos casos reales no se visitan **todas** las ubicaciones, sino solo un
**subconjunto**, por un presupuesto de paradas. Ese es el **k-TSP**: elegir k de n
ciudades —incluyendo un depósito— y ordenarlas en un único recorrido cerrado de
longitud mínima. Aparece en muestreo selectivo, ruteo con recompensas, vigilancia
con visitas limitadas y logística con recursos acotados."

## Diapositiva 3 — Objetivos (1:00)
"El **objetivo general** fue desarrollar un repositorio reproducible que modela,
resuelve y compara instancias del k-TSP, evaluando heurísticas y metaheurísticas
contra los valores de referencia de LKH-3.
Como **objetivos específicos**: formular el problema matemáticamente; implementar
**diez** técnicas; evaluar la calidad con el GAP relativo sobre 38 instancias TSPLIB
y tres valores de k; complementar con un análisis *anytime*; y liberar todo de forma
que cada tabla y figura se regenere con un solo comando."

## Diapositiva 4 — Metodología de trabajo (1:00)
"El trabajo se organizó en cuatro etapas: (a) diseño de datos, con estructuras
uniformes para instancias reales y sintéticas; (b) el modelo matemático; (c) la
resolución heurística, con los diez métodos sobre un **núcleo común** de primitivas
—2-opt, intercambio dentro/fuera e inserción más barata—, lo que hace la comparación
justa; y (d) la evaluación experimental.
Todo en Python, versionado en un repositorio privado de GitHub, usando Visual Studio
Code, y con el binario oficial de LKH-3 compilado localmente. Como medida de tiempo
usamos las **evaluaciones de distancia**, independiente de la máquina."

## Diapositiva 5 — Asistencia a evento: Optima 2025 (0:30)
"El núcleo de la tesis se escribió como un paper científico y se **envió a Optima
2025**, congreso organizado por la Universidad Católica del Norte, el 30 de noviembre
de 2025. Actualmente está en revisión. Ese paper es la contribución central del
trabajo y se incluye como capítulo de la tesis."

## Diapositiva 6 — El problema de investigación (1:15)
"Formalmente: dadas n ciudades con un depósito y un k fijo, buscamos un recorrido
cerrado de longitud mínima que visite exactamente k ciudades. La dificultad está en
que hay **dos decisiones acopladas**: *cuáles* k nodos visitar y *en qué orden*.
El número de subconjuntos posibles crece de forma combinatoria —C(n-1, k-1), cada
uno con (k-1)!/2 recorridos— así que la enumeración exhaustiva es inviable y se
necesitan heurísticas.
A la derecha ven la representación que usamos: un *genotipo* —subconjunto más orden—
que se decodifica en un único recorrido cerrado, el *fenotipo*. Como referencia
cercana al óptimo usamos los valores BKS de LKH-3 sobre el benchmark de Pandiri y
Singh."

## Diapositiva 7 — Tabla de referencia: GAP promedio (1:15)
"Esta tabla resume el resultado central: el **GAP promedio** de cada método frente a
LKH-3, para los tres valores de k, sobre las 38 instancias. Recuerden: menor es
mejor.
Lo más importante: **Greedy** y **Tabu Search** logran el menor GAP promedio —del
orden del 12–13%—. El algoritmo genético mejora cuando k es grande (Q3). Y
**Farthest Insertion** es claramente el peor, con GAPs enormes, porque insertar los
nodos más lejanos choca con el objetivo de seleccionar nodos baratos de incluir."

## Diapositiva 8 — Heurísticas (1/3): construcción (1:15)
"Los métodos de **construcción**. El **Greedy** inserta el nodo de menor costo
marginal hasta llegar a k y refina con 2-opt. **Nearest Neighbor** avanza siempre al
nodo más cercano. **Nearest y Farthest Insertion** insertan el nodo más cercano o más
lejano al recorrido, en su mejor posición. Y **Random Insertion** elige el siguiente
nodo al azar, con múltiples arranques.
Todos comparten el mismo núcleo de búsqueda local, así que la comparación es justa."

## Diapositiva 9 — Heurísticas (2/3): metaheurísticas (1:15)
"Las **metaheurísticas**. **GRASP** combina construcción aleatorizada con búsqueda
local y muchos reinicios. El **algoritmo genético** codifica subconjunto y orden, con
torneo, cruzamiento consciente del subconjunto, mutación y elitismo. **Simulated
Annealing** acepta empeoramientos con probabilidad exp(-Δ/T), enfriando la
temperatura, para escapar de óptimos locales. Y **Tabu Search** es una búsqueda con
**memoria**: toma el mejor movimiento no prohibido, guarda los movimientos recientes
en una lista tabú, y permite excepciones si mejora el mejor global. Tabu Search
resultó ser la mejor de las metaheurísticas."

## Diapositiva 10 — Heurísticas (3/3): DCIH, la propuesta (1:30)
"Y esta es mi propuesta: **DCIH**, *Deterministic Cheapest-Insertion Heuristic*.
Tiene dos fases: en la primera selecciona y ordena los k nodos por costo marginal de
inserción mínimo, rompiendo empates por índice de nodo; en la segunda refina con
2-opt e intercambio dentro/fuera hasta que no mejora.
Su gracia es que es **totalmente determinista**: con los mismos datos siempre devuelve
exactamente el mismo recorrido, sin azar. Prioriza la correctitud y la
reproducibilidad por sobre ganar por suerte, y logra una calidad comparable a GRASP y
a las heurísticas de inserción."

## Diapositiva 11 — Análisis de resultados (1/2): fin de corrida (1:30)
"Al comparar el **resultado final**: Greedy y Tabu Search dan el mejor GAP promedio,
del orden del 12,5%. El algoritmo genético cierra la brecha cuando k es grande y gana
en muchas instancias individuales. Farthest Insertion es el más débil, por lo que ya
expliqué. Y DCIH es una alternativa determinista y reproducible de calidad
comparable. En total comparamos **diez** métodos contra los valores BKS de LKH-3."

## Diapositiva 12 — Análisis de resultados (2/2): anytime (1:30)
"Pero el resultado final no lo dice todo. Siguiendo la metodología de Weise,
analizamos el comportamiento **anytime**: la calidad a lo largo del tiempo, medido en
evaluaciones de distancia, independiente de la máquina.
En la curva de progreso, todos los métodos se dibujan sobre el mismo presupuesto. El
ranking global, que combina cuatro criterios, pone a **Nearest Neighbor primero**,
porque llega muy rápido a una buena solución con pocas evaluaciones. Pero ojo: NN es
el más **rápido**, no el de mejor calidad final. Esa distinción entre 'rápido' y
'mejor' es justamente lo que esta metodología permite ver."

## Diapositiva 13 — Conclusiones y mejoras futuras (1:15)
"En conclusión: Greedy y Tabu Search son los más robustos, con Tabu Search como la
mejor metaheurística; el genético destaca para k grande; Farthest Insertion es el más
débil; y DCIH aporta una opción determinista y reproducible. El análisis anytime
separó lo 'rápido' de lo 'mejor'.
Como **trabajo futuro**: metaheurísticas más potentes o híbridas —colonia de hormigas,
VNS, o un memético que combine Tabu Search con el genético—; ajuste de parámetros por
instancia; reglas de selección de nodos dedicadas; e instancias más grandes y
problemas de ruteo selectivo relacionados."

## Diapositiva 14 — Referencias (0:20)
"Estas son algunas de las referencias principales; la bibliografía completa, con 50
referencias, está en la tesis y en el paper. Muchas gracias, quedo atento a sus
preguntas."

---

## Preguntas probables (preparación)
- **¿Por qué NN queda primero en el ranking anytime pero no en calidad?**
  Porque el ranking anytime premia la *velocidad de convergencia* (ERT, ECDF), y NN
  llega a una solución decente con muy pocas evaluaciones; en calidad final, sin
  embargo, queda a mitad de tabla. Son dos preguntas distintas: "¿quién es más rápido?"
  vs "¿quién llega más lejos?".
- **¿Por qué Farthest Insertion es tan malo aquí?**
  Porque en el k-TSP hay que *seleccionar* nodos baratos de incluir; insertar los más
  lejanos va en contra de ese objetivo.
- **¿Qué aporta DCIH frente a Greedy?**
  Determinismo y reproducibilidad total (mismo tour siempre), con una construcción
  única con desempate por índice y un refinamiento que también cambia el subconjunto.
- **¿Por qué usar evaluaciones de distancia y no segundos?**
  Para que la comparación no dependa del hardware ni del lenguaje: es una medida
  reproducible entre máquinas (metodología de Weise).
- **¿Por qué LKH-3 como referencia?**
  Es uno de los mejores solvers para TSP y variantes; da los mejores valores conocidos
  (BKS) del benchmark, así que sirve como referencia cercana al óptimo.
