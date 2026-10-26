# Preparación para la reunión / defensa — k-TSP
**Nicolás Barrientos · Prof. guía: Dr. Gustavo Gatica · UNAB**
_Guía rápida: resumen de lo que tengo + banco de preguntas probables (incluidas las difíciles) con respuestas sugeridas._

---

## 0. Resumen de lo que tengo (elevator pitch, ~1 min)
"Mi proyecto es una **comparación reproducible de diez métodos** para el *k*-TSP —el TSP donde se visitan solo *k* de *n* ciudades—. Implementé desde heurísticas de construcción (Greedy, Nearest Neighbor, inserciones) hasta metaheurísticas (GRASP, genético, Simulated Annealing, Tabu Search) y una propuesta propia, **DCIH**, una heurística determinista. Los evalué siguiendo **el mismo protocolo de Pandiri & Singh (OPSEARCH 2020)**: sus **76 instancias TSPLIB**, tres valores de *k*, límites de tiempo de reloj (short run 0,05·n s y long run 0,2·n s), 10 corridas, y el **test de Wilcoxon**; la referencia de calidad es **LKH-3**. Además comparo contra sus métodos publicados (GVNS y dos hiper-heurísticas). Todo es reproducible: cada tabla y figura se regenera con un comando, versionado en GitHub."

**Estado de entregables:** paper (Springer/OPSEARCH, inglés) ✓ · tesis por compendio (31 pág.) ✓ · presentación (16 diapositivas) + guión ✓ · código reproducible en GitHub ✓.

**Hallazgos clave (ten a mano los números):**
- Mejor GAP promedio global de mis métodos: **Greedy ≈8,1%** y **Tabu Search ≈8,8%**.
- **Greedy y TS son significativamente mejores que el GVNS de Pandiri (16,2%)** por Wilcoxon; en short run, Greedy incluso iguala/supera a HH\_GREEDY.
- Las hiper-heurísticas **HH\_RAND (6,2%) y HH\_GREEDY (7,3%)** siguen siendo lo más fuerte.
- Mi mejor método **iguala o supera al mejor de Pandiri en 103/228 casos** (short run) y a HH\_GREEDY en 123/228.
- **GA** mejora para *k* grande, sobre todo en long run; **Farthest Insertion** es el peor.
- **DCIH**: calidad comparable a las inserciones, con la ventaja de ser 100% determinista y reproducible.

---

## 1. Problema y motivación
**P: ¿Por qué es relevante el k-TSP y no el TSP clásico?**
Porque muchas aplicaciones reales no visitan *todas* las ubicaciones, sino un subconjunto bajo un presupuesto de paradas: muestreo selectivo, ruteo con recompensas, vigilancia con visitas limitadas, logística con recursos acotados.

**P: ¿Es una variante o una generalización del TSP?**
Una **generalización**: el TSP es el caso particular *k = n*. (Ya lo corregí en abstract.)

**P: ¿Por qué es difícil (NP-hard)?**
Acopla dos decisiones: *cuáles k* nodos y *en qué orden*. Hay C(n−1, k−1) subconjuntos, cada uno con (k−1)!/2 recorridos → la enumeración es inviable ya en tamaños medianos.

**P: ¿Qué lo diferencia de Orienteering o Prize-Collecting TSP?**
El k-TSP es el caso de "premio unitario" del Quota TSP: se fija el *número* de nodos a visitar (k), no un premio/beneficio a maximizar ni una penalización por no visitar. Pertenece a la familia *TSP with profits*.

---

## 2. Modelo matemático
**P: Explica el modelo.**
Variables binarias *x_ij* (arco en el tour) e *y_i* (nodo seleccionado), más variables continuas *u_i* de orden (MTZ). Minimizo Σ d_ij x_ij sujeto a: depósito siempre incluido (y₀=1); exactamente k nodos (Σ y_i = k); grado (un arco de entrada y uno de salida sii el nodo está seleccionado); y las desigualdades MTZ para eliminar subtours.

**P: ¿Por qué MTZ y no cortes DFJ?**
MTZ usa un número **polinomial** de restricciones y es fácil de escribir; DFJ es más fuerte pero tiene un número exponencial de cortes que requieren separación dinámica. Como el modelo solo se usa para **definir** el problema (no lo resuelvo con un solver exacto), MTZ es suficiente y claro.

**P: ¿Por qué no resolver el MIP directamente?**
Porque escala muy mal; por eso el foco son heurísticas. Las decenas/cientos de nodos del benchmark ya son intratables para enumeración/branch-and-cut casero.

---

## 3. Métodos
**P: ¿Por qué estos diez métodos?**
Cubren el espectro: las cuatro heurísticas de construcción clásicas (NN e inserciones nearest/farthest/random, de Rosenkrantz et al.), el greedy cheapest-insertion como baseline, tres metaheurísticas de familias distintas (GRASP, poblacional=GA, trayectoria=SA y memoria=TS) y mi propuesta DCIH. Da una comparación representativa.

**P: Todos comparten un "núcleo común" (2-opt, intercambio dentro/fuera). ¿Eso no sesga la comparación?**
Al contrario: compartir la misma búsqueda local hace la comparación **más justa**, porque las diferencias se deben a cómo cada método construye/explora, no a implementaciones de 2-opt mejores o peores.

**P: ¿Cómo elegiste los parámetros de las metaheurísticas (tenure, enfriamiento, población)?**
Los fijé iguales para todas las instancias, por equidad. **No** hice tuning por instancia; es una limitación deliberada y afinarlos probablemente mejoraría los resultados de las metaheurísticas (está en trabajo futuro).

---

## 4. DCIH (tu propuesta — la más cuestionada)
**P: ¿Qué tiene de nuevo DCIH frente al Greedy cheapest-insertion?**
Dos cosas: (i) una **única** construcción determinista con **desempate por índice de nodo** (en vez de varios reinicios con semilla), y (ii) un refinamiento que **itera** 2-opt junto con el intercambio dentro/fuera —que cambia el subconjunto seleccionado— hasta no mejorar. El Greedy solo aplica 2-opt sobre un subconjunto fijo.

**P: DCIH NO es el mejor método. ¿Por qué lo propones?**
Porque su aporte no es ganar en GAP, sino ser **totalmente determinista y reproducible**: con los mismos datos devuelve exactamente el mismo tour, sin azar ni semilla. Eso es valioso cuando la **reproducibilidad y la explicabilidad** importan más que ganar por suerte, y aun así su calidad es comparable a GRASP y a las inserciones.

**P: ¿"Determinista/reproducible" es aporte suficiente para una tesis?**
El aporte de la tesis no es solo DCIH: es la **comparación reproducible de 10 métodos** sobre el benchmark estándar de Pandiri & Singh, con referencia LKH-3 y una **comparación estadística (Wilcoxon) contra el estado del arte** (GVNS y las hiper-heurísticas). DCIH es un componente dentro de ese marco.

**P: ¿DCIH tiene garantías teóricas de aproximación?**
No; es una heurística evaluada **empíricamente**. Las garantías teóricas de inserción (Rosenkrantz et al.) son para TSP; extenderlas al k-TSP sería trabajo futuro.

---

## 5. Diseño experimental
**P: ¿Por qué 76 instancias y por qué esos valores de k?**
Sigo **exactamente el protocolo de Pandiri & Singh**: sus 76 instancias TSPLIB (de n=14 a n=783) y tres valores de k por instancia —Small ⌊n/4⌋, Medium ⌊n/2⌋, Large ⌊3n/4⌋—. Usar su mismo benchmark hace la comparación directa con su GVNS y sus hiper-heurísticas.

**P: ¿Por qué LKH-3 como referencia y no el óptimo?**
LKH-3 es uno de los mejores solvers para TSP y variantes; da los mejores valores conocidos (BKS) del benchmark, **cercanos al óptimo**. Es la referencia más fuerte disponible.

**P: ¿Cuál es el límite de cómputo?**
Los **mismos límites de tiempo de reloj de Pandiri**: short run = 0,05·n segundos y long run = 0,2·n segundos, con 10 corridas por método estocástico. El tiempo escala con el tamaño de la instancia, igual que en su trabajo.

**P: 10 corridas por método estocástico, ¿hiciste tests de significancia?**
Sí. Apliqué el **test de Wilcoxon de rangos con signo** (dos colas), pareado por instancia —el mismo que usa Pandiri—. Confirma que Greedy y TS son significativamente mejores que GVNS (p<0,05).

**P: ¿Usaste instancias sintéticas en los resultados finales?**
No. Los resultados reportados son sobre **TSPLIB real** con BKS de LKH-3. Las sintéticas solo sirven como respaldo cuando no hay red.

---

## 6. Resultados y análisis
**P: Los GAP son del 10–20% o más. Eso está lejos del óptimo. ¿Comentario?**
Son heurísticas, no métodos exactos, y la referencia (LKH-3) es extremadamente fuerte. El objetivo no es batir a LKH-3 sino **comparar métodos entre sí** de forma justa y reproducible; el GAP mide qué tan cerca llega cada uno.

**P: Farthest Insertion da ~100% de GAP en el escenario Small. ¿No es un bug?**
No. FI inserta deliberadamente el nodo **más lejano** al tour; en el k-TSP eso **choca** con el objetivo de *seleccionar* nodos baratos de incluir, así que elige nodos caros y produce tours largos. Es un resultado coherente, no un error (lo validé).

**P: ¿Los deterministas no cambian entre short y long run?**
Correcto: NN, NI, FI y DCIH construyen **una sola** solución, así que más tiempo no la cambia. Solo las metaheurísticas (y Greedy, con reinicios) aprovechan el presupuesto extra; el que más gana es el genético, que pasa a ser el mejor de mis métodos en el escenario Large bajo long run.

---

## 7. Comparación estadística (Wilcoxon)
**P: ¿Qué es el test de Wilcoxon y por qué lo usas?**
Es una prueba **no paramétrica pareada** que compara dos métodos sobre muchas instancias sin suponer normalidad de los datos. La uso porque es la que usa Pandiri & Singh y porque en la versión anterior faltaba un análisis estadístico. Comparo el GAP por instancia de cada par de métodos.

**P: ¿Qué concluye el test en tu caso?**
Que **Greedy y Tabu Search son significativamente mejores que GVNS** (p<0,05) en short y long run; que en el short run Greedy supera a HH\_GREEDY y TS lo empata; y que HH\_RAND se mantiene como el más fuerte, sobre todo en long run.

**P: ¿Le ganas al estado del arte, entonces?**
En parte: no gano a las hiper-heurísticas en promedio global, pero **sí supero a su GVNS de forma significativa** y soy competitivo con HH\_GREEDY. Mi aporte es una comparación reproducible de diez métodos sobre su propio benchmark, no necesariamente batir a su mejor método.

---

## 8. Reproducibilidad e ingeniería
**P: ¿Cómo garantizas la reproducibilidad?**
Semillas fijas en los métodos estocásticos; los deterministas (NN, NI, FI, DCIH) dan siempre el mismo resultado; todo el pipeline regenera tablas y figuras con **un comando**; y cada experimento corresponde a un **commit** en un repositorio privado de GitHub.

**P: ¿Dónde corriste los experimentos?**
Localmente en Visual Studio Code, Python 3.10 (numpy/pandas/scipy/matplotlib), con el binario oficial de LKH-3 compilado. Como el protocolo usa límites de tiempo de reloj, las corridas corresponden a una máquina fija y los presupuestos escalan con el tamaño de la instancia, igual que en Pandiri & Singh.

---

## 9. Limitaciones y trabajo futuro (adelántate tú)
- **Sin tuning de parámetros** de las metaheurísticas (fijos por equidad) → afinarlos mejoraría resultados.
- **Brecha a las hiper-heurísticas** de Pandiri → metaheurísticas más potentes o **híbridas** (memético TS+GA, ACO, VNS).
- Reglas de **selección de nodos** dedicadas (hoy la selección se apoya solo en el costo de inserción).
- Extender a **instancias más grandes** y a problemas de ruteo selectivo relacionados.

---

## 10. Preguntas "meta" / trampa
**P: ¿Cuál es TU aporte concreto?**
(1) Una comparación reproducible y documentada de 10 métodos para el k-TSP sobre el benchmark de Pandiri & Singh; (2) la heurística determinista **DCIH**; (3) una **comparación estadística (Wilcoxon)** frente al estado del arte (GVNS y las hiper-heurísticas) y a LKH-3; (4) un repositorio que cualquiera puede re-ejecutar.

**P: ¿Usaste IA? ¿Cómo lo declaras?**
Sí, como apoyo (redacción/estilo en inglés, organización, depuración/documentación de código y generación de figuras **a partir de mis propios datos**). Todo el contenido científico —modelo, algoritmos, protocolo, datos, resultados y conclusiones— es mío. Está declarado explícitamente en la tesis.

**P: ¿Por qué esto amerita una tesis/paper?**
Porque aporta evidencia empírica reproducible sobre un problema poco comparado de forma sistemática, siguiendo el protocolo y el benchmark de Pandiri & Singh con una comparación estadística frente al estado del arte y una propuesta propia, y está preparado para ser enviado a una revista (OPSEARCH) cuando se finalicen las revisiones.

---

## 11. Gráficos y tablas (cómo explicarlos)

**P: Explique la Figura 1 (barras de GAP por escenario).**
Es el GAP promedio frente a LKH-3 por escenario de k (Small/Medium/Large); el panel izquierdo es el short run y el derecho el long run. Las barras claras son mis métodos y las rayadas (con *) son el GVNS y las hiper-heurísticas de Pandiri & Singh. Menor es mejor. Lo que se ve: Greedy y Tabu Search son barras bajas y estables en los tres escenarios, siempre por debajo de GVNS; el genético baja bastante del short al long run, sobre todo en Large; y Farthest Insertion es la barra más alta.

**P: Explique la Figura 2 (boxplot).**
Muestra la distribución del GAP por instancia bajo long run, un método por caja. La línea central es la mediana, la caja es el 50% central (cuartiles) y los bigotes el rango sin atípicos; recorté en 80% para que se lea. Greedy y Tabu Search tienen cajas compactas y bajas, parecidas a las de las hiper-heurísticas; Farthest y Random Insertion tienen cajas altas y colas largas, o sea mucha más dispersión. Sirve para mostrar no solo el promedio sino la **consistencia** de cada método.

**P: ¿Por qué recortaste el boxplot en 80%?**
Solo por legibilidad: unas pocas instancias difíciles (p. ej. Farthest Insertion) tienen GAP muy altos que aplastarían el resto del gráfico. El recorte es visual; los promedios y el test de Wilcoxon usan todos los datos sin recortar.

**P: Explique la Tabla 1 (GAP promedio por método).**
Filas = los diez métodos más GVNS/HH_RAND/HH_GREEDY de Pandiri (con *); columnas = los tres escenarios de k, para short run y long run. Cada celda es el GAP promedio sobre las 76 instancias; el mejor de cada columna va en negrita, y menor es mejor. Es la tabla "madre": de ahí sale el ranking global (Greedy 8.1%, TS 8.8%, GVNS 16.2%, etc.).

**P: Explique la Tabla 2 (Wilcoxon).**
Compara mis dos mejores métodos (Greedy y TS) contra cada método de Pandiri, pareando el GAP instancia por instancia. La columna Δ es la diferencia de GAP promedio (negativo = yo mejor) y el p-valor dice si la diferencia es significativa (p<0.05). Conclusión: Greedy y TS son significativamente mejores que GVNS; en short run Greedy supera a HH_GREEDY; frente a HH_RAND quedo por debajo.

**P: ¿Por qué comparas con el "mejor valor conocido" y no con el óptimo exacto?**
Porque el óptimo exacto no se conoce para la mayoría de estas instancias: calcularlo es intratable. LKH-3 da el mejor valor conocido (BKS), muy cercano al óptimo, y es la referencia estándar del benchmark.

**P: ¿Qué representan las figuras conceptuales (genotipo–fenotipo y el tour del k-TSP)?**
La del tour muestra una solución real sobre eil51: el recorrido cerrado (azul) pasa por el depósito (estrella) y los k nodos elegidos; los n−k restantes quedan fuera. La de genotipo→fenotipo ilustra la codificación: el genotipo guarda qué nodos se eligen y en qué orden, y al decodificarlo se cierra en un único tour que luego se evalúa por su longitud.

**P: En Fig 1, ¿por qué algunas barras (NN, NI, FI, DCIH) son iguales en short y long run?**
Porque son métodos deterministas de construcción: arman una sola solución y no usan el tiempo extra. Solo Greedy (con reinicios) y las metaheurísticas aprovechan el presupuesto mayor del long run.

**P: Explique la "Tabla de resultados" agregada (la del PPT).**
Es el GAP promedio de cada método (mis diez más GVNS/HH de Pandiri) por escenario de k —Small, Medium, Large— y por criterio de tiempo —short y long run—, sobre las 76 instancias. En negrita, el mejor de cada columna. Es la fuente del ranking global.

**P: ¿Tiene los resultados por instancia, o solo promedios?**
Sí, tengo el detalle **por instancia**: en el apéndice de la tesis y como diapositivas de respaldo hay tablas, separadas por cuartil (Small/Medium/Large) y por criterio (SR y LR), con la longitud de tour de cada método y la columna LKH-3. En negrita, los casos donde un método **iguala el mejor valor conocido** de LKH-3.

**P: En las tablas por instancia, ¿qué valor reporta por método?**
La **mejor** de las diez corridas para los métodos estocásticos (igual que reporta Pandiri); los deterministas (NN, NI, FI, DCIH) tienen una sola corrida. La columna LKH-3 es el BKS de referencia.

**P: ¿Por qué separa las tablas por cuartil?**
Porque el comportamiento cambia con k: con k chico (Q1) domina la **selección** de nodos y Greedy/TS brillan; con k grande (Q3) el problema se parece a un TSP y el genético cierra la brecha. Separar por cuartil deja ver esa transición.

---

### Consejo final
Si no sabes una respuesta, no inventes: reconoce la limitación y conéctala con el **trabajo futuro**. Muestra que entiendes *por qué* cada decisión se tomó así. Ten a la vista: los números clave (sección 0), la diferencia DCIH vs Greedy (sección 4) y el argumento "significativamente mejores que GVNS, competitivos con las hiper-heurísticas" (secciones 6–7).
