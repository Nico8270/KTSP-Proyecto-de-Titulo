# Guión cronometrado — Defensa k-TSP (15:00)
**Nicolás Barrientos · Prof. guía: Dr. Gustavo Gatica · UNAB**

> Para el deck institucional UNAB (`presentacion_ktsp_UNAB.pptx`): portada + 17
> diapositivas de contenido. Las diapositivas de respaldo del final NO se presentan
> (son para preguntas). Diapositivas en inglés · guión hablado en español.
> Cada bloque trae su duración y el **acumulado** (en qué minuto deberías ir al
> terminar esa diapositiva).

| # | Diapositiva | Dura | Acum. |
|---|---|---|---|
| — | Portada | 0:15 | 0:15 |
| 1 | Contexto y motivación | 0:50 | 1:05 |
| 2 | Objetivos | 0:45 | 1:50 |
| 3 | Metodología | 0:45 | 2:35 |
| 4 | Problema | 0:55 | 3:30 |
| 5 | Modelo | 0:45 | 4:15 |
| 6 | Benchmark y cuartiles | 1:00 | 5:15 |
| 7 | Resultados por escenario (Fig.) | 1:00 | 6:15 |
| 8 | Tabla de resultados | 0:35 | 6:50 |
| 9 | Comparación (ranking) | 1:10 | 8:00 |
| 10 | Significancia (Wilcoxon) | 1:05 | 9:05 |
| 11 | Heurísticas: construcción | 0:50 | 9:55 |
| 12 | Heurísticas: metaheurísticas | 0:50 | 10:45 |
| 13 | DCIH (propuesta) | 1:00 | 11:45 |
| 14 | Resultados: global | 0:50 | 12:35 |
| 15 | Efecto del tiempo (SR/LR) | 0:55 | 13:30 |
| 16 | Conclusiones | 0:55 | 14:25 |
| 17 | Referencias y cierre | 0:15 | 14:40 |
| — | Colchón | 0:20 | 15:00 |

---

## Portada — 0:15 · (→0:15)
"Buenos días. Soy Nicolás Barrientos y presento mi proyecto de título,
*Heuristic Approaches for the k-TSP: a Reproducible Comparison*, guiado por el
Dr. Gustavo Gatica."

## 1 — Contexto y motivación — 0:50 · (→1:05)
"La optimización de rutas está en todas partes: logística, transporte, vigilancia.
El TSP clásico busca la ruta cerrada más corta que visita todas las ciudades. Pero
muchos casos reales visitan solo un **subconjunto**, por un presupuesto de paradas.
Ese es el **k-TSP**: elegir k de n ciudades —con un depósito— y ordenarlas en un
recorrido cerrado mínimo."

## 2 — Objetivos — 0:45 · (→1:50)
"Objetivo general: un repositorio reproducible que modela, resuelve y compara el
k-TSP contra LKH-3. Específicos: formular el problema, implementar **diez** métodos,
evaluarlos sobre las **76 instancias de Pandiri & Singh**, **compararlos
estadísticamente con Wilcoxon** contra sus métodos, y liberar todo para
regenerarlo con un comando."

## 3 — Metodología — 0:45 · (→2:35)
"Cuatro etapas: datos, modelo, resolución heurística —los diez métodos sobre un
núcleo común de 2-opt, intercambio e inserción, lo que hace la comparación justa—
y evaluación. Todo en Python, en VS Code, en GitHub privado, con LKH-3 local, bajo
el protocolo de tiempo de Pandiri y el test de Wilcoxon."

## 4 — El problema de investigación — 0:55 · (→3:30)
"Formalmente: dadas n ciudades con depósito y un k fijo, el recorrido cerrado más
corto que visita exactamente k ciudades. La dificultad son **dos decisiones
acopladas**: *cuáles* k nodos y *en qué orden*. El número de combinaciones crece
combinatorialmente, así que se necesitan heurísticas. A la derecha, un ejemplo real
sobre eil51: el tour pasa solo por los nodos elegidos."

## 5 — Modelo matemático — 0:45 · (→4:15)
"El modelo formal. Variables: x si un arco está en el tour, y si un nodo se
selecciona, y u el orden (Miller–Tucker–Zemlin). La objetivo minimiza la longitud
total. Las restricciones fuerzan el depósito, exactamente k nodos, el grado de cada
nodo, y las MTZ eliminan subtours. Deja explícitas las dos decisiones: selección y
orden."

## 6 — Benchmark y cuartiles — 1:00 · (→5:15)
"Para comparar directo con el estado del arte, sigo **el mismo protocolo de Pandiri
& Singh**, de OPSEARCH: **76 instancias** de TSPLIB, de 14 a 783 ciudades. Los tres
valores de k son los **cuartiles del tamaño n**: Small, un cuarto de las ciudades,
donde manda la selección; Medium, la mitad; y Large, tres cuartos, donde ya se
parece a un TSP normal. Dos límites de tiempo de reloj, **short run 0,05·n s** y
**long run 0,2·n s**, con 10 corridas. En total, 228 casos contra LKH-3."

## 7 — Resultados por escenario — 1:00 · (→6:15)
"Este gráfico es el resultado central: GAP promedio frente a LKH-3 por escenario;
izquierda short run, derecha long run; menor es mejor. Barras claras son mis
métodos, rayadas son GVNS y las hiper-heurísticas de Pandiri. Lo clave: **Greedy y
Tabu Search son los más robustos** y **le ganan claramente a su GVNS**; el genético
mejora con más tiempo; y Farthest Insertion es el peor, porque insertar los nodos
lejanos choca con seleccionar nodos baratos."

## 8 — Tabla de resultados — 0:35 · (→6:50)
"Aquí está la tabla completa: el GAP promedio de cada método, por escenario de k y
por criterio de tiempo. En negrita el mejor de cada columna. De aquí sale el
ranking que viene ahora; lo importante es que Greedy y Tabu Search son bajos y
estables en todas las columnas."

## 9 — Comparación con el estado del arte — 1:10 · (→8:00)
"Ordenando por GAP promedio global: las hiper-heurísticas de Pandiri quedan
primeras, pero **mi Greedy con 8,1% y mi Tabu Search con 8,8% quedan justo detrás**,
y ambos **superan a su GVNS, que está en 16,2%**. Caso por caso, mi mejor método
**iguala o supera al mejor de Pandiri en 103 de 228 casos** en short run, y a
HH_GREEDY en 123 de 228. Heurísticas simples y reproducibles, competitivas con
metaheurísticas dedicadas en su propio benchmark."

## 10 — Significancia estadística (Wilcoxon) — 1:05 · (→9:05)
"Para no quedarnos en promedios, apliqué el **test de Wilcoxon** pareado por
instancia, el mismo de Pandiri. Resultado: **Greedy y Tabu Search son
significativamente mejores que GVNS**, p menor a 0,05, en short y long run. En short
run mi Greedy incluso **le gana a HH_GREEDY** y Tabu Search lo empata; HH_RAND sigue
siendo el más fuerte. El boxplot muestra que Greedy y TS tienen las distribuciones
más compactas entre mis métodos."

## 11 — Heurísticas (1/3): construcción — 0:50 · (→9:55)
"Los métodos de construcción: **Greedy** inserta el nodo más barato hasta k y
refina; **Nearest Neighbor** avanza al más cercano; **Nearest y Farthest Insertion**
insertan el más cercano o más lejano al tour; **Random Insertion** elige al azar con
reinicios. Todos comparten el mismo núcleo de búsqueda local."

## 12 — Heurísticas (2/3): metaheurísticas — 0:50 · (→10:45)
"Las metaheurísticas: **GRASP**, construcción aleatorizada más búsqueda local;
**genético**, evoluciona subconjunto y orden; **Simulated Annealing**, acepta
empeoramientos con probabilidad exp(-Δ/T) enfriando; y **Tabu Search**, búsqueda con
memoria que toma el mejor movimiento no prohibido. TS es la mejor de mis
metaheurísticas."

## 13 — Heurísticas (3/3): DCIH, la propuesta — 1:00 · (→11:45)
"Mi propuesta: **DCIH**. Fase 1: selecciona y ordena por costo marginal mínimo,
rompiendo empates por índice. Fase 2: refina con 2-opt e intercambio. Es
**totalmente determinista**: mismos datos, mismo recorrido, sin azar. Prioriza
correctitud y reproducibilidad, con calidad comparable a las inserciones."

## 14 — Resultados: comparación global — 0:50 · (→12:35)
"En resumen: Greedy —cerca de 8%— y Tabu Search son los más robustos; ambos
**significativamente mejores que GVNS** y competitivos con las hiper-heurísticas de
Pandiri en su mismo protocolo. El genético cierra la brecha para k grande; Farthest
Insertion es el más débil; y DCIH es la opción determinista y reproducible."

## 15 — Efecto del presupuesto de tiempo — 0:55 · (→13:30)
"Aquí el efecto de dar más tiempo: GAP promedio en short versus long run. Los
métodos **deterministas no cambian**, porque construyen una sola vez. Los que usan
el tiempo sí mejoran: el **genético es el que más gana** y pasa a ser el mejor de
mis métodos en Large bajo long run. Greedy y Tabu Search se mantienen robustos en
ambos presupuestos."

## 16 — Conclusiones y futuro — 0:55 · (→14:25)
"En conclusión: Greedy y Tabu Search, los más robustos, y ambos le ganan a GVNS de
forma significativa; mi trabajo es competitivo con las hiper-heurísticas de Pandiri
en su propio benchmark; el genético destaca para k grande; Farthest Insertion es el
más débil; y DCIH es determinista y reproducible. Como futuro: metaheurísticas
híbridas, ajuste de parámetros por instancia, reglas de selección dedicadas e
instancias más grandes."

## 17 — Referencias y cierre — 0:15 · (→14:40)
"Estas son las referencias principales; la bibliografía completa está en la tesis y
el paper. Muchas gracias, quedo atento a sus preguntas."

---

## Nota de ritmo (para no pasarte de 15:00)
- **Punto de control: diapositiva 10 (Wilcoxon), deberías ir en ~9:05.** Si pasas de
  9:45, acelera.
- **Las diapositivas 7, 9 y 10 son el corazón** (resultados, comparación, Wilcoxon):
  no las apures. Si vas atrasado, comprime 4 (Problema) y 5 (Modelo) —resume las
  restricciones— y las de métodos 11–12.
- **La tabla (8) es de paso rápido:** no la leas celda por celda; apunta a "mejor por
  columna, Greedy y TS estables".
- **Las tablas por instancia están al final como respaldo.** No las muestres en los
  15 min; úsalas solo si el jurado pide el detalle de una instancia o cuartil.
- No leas las diapositivas palabra por palabra; habla mirando al jurado.
