# Preparación para la reunión / defensa — k-TSP
**Nicolás Barrientos · Prof. guía: Dr. Gustavo Gatica · UNAB**
_Guía rápida: resumen de lo que tengo + banco de preguntas probables (incluidas las difíciles) con respuestas sugeridas._

---

## 0. Resumen de lo que tengo (elevator pitch, ~1 min)
"Mi proyecto es una **comparación reproducible de diez métodos** para el *k*-TSP —el TSP donde se visitan solo *k* de *n* ciudades—. Implementé desde heurísticas de construcción (Greedy, Nearest Neighbor, inserciones) hasta metaheurísticas (GRASP, genético, Simulated Annealing, Tabu Search) y una propuesta propia, **DCIH**, una heurística determinista. Los evalué sobre **38 instancias TSPLIB** en tres valores de *k*, usando como referencia los mejores valores conocidos de **LKH-3**. Además del resultado final (GAP), hice un análisis **anytime** estilo Weise, midiendo el tiempo en evaluaciones de distancia (independiente de la máquina). Todo es reproducible: cada tabla y figura se regenera con un comando, versionado en GitHub."

**Estado de entregables:** paper (IEEE, inglés) ✓ · tesis por compendio (31 pág.) ✓ · presentación (18 diapositivas) + guión ✓ · código reproducible en GitHub ✓.

**Hallazgos clave (ten a mano los números):**
- Mejor GAP promedio: **Greedy ≈12,6%** y **Tabu Search ≈12,5%** (TS = mejor metaheurística).
- **GA** gana en más instancias cuando *k* es grande (Q3).
- **Farthest Insertion** es el peor (GAP enorme, ~98% en Q1).
- En el ranking **anytime**, **NN queda 1º** por ser el más rápido, aunque en calidad final es mediocre.
- **DCIH**: calidad comparable a GRASP/inserciones, con la ventaja de ser 100% determinista y reproducible.

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
El aporte de la tesis no es solo DCIH: es la **comparación reproducible de 10 métodos** sobre un benchmark estándar con referencia LKH-3 y un **análisis anytime** del k-TSP, que es escaso en la literatura. DCIH es un componente dentro de ese marco.

**P: ¿DCIH tiene garantías teóricas de aproximación?**
No; es una heurística evaluada **empíricamente**. Las garantías teóricas de inserción (Rosenkrantz et al.) son para TSP; extenderlas al k-TSP sería trabajo futuro.

---

## 5. Diseño experimental
**P: ¿Por qué 38 instancias y por qué esos cuartiles?**
Sigo el benchmark de **Pandiri & Singh**, que define tres valores de k por instancia (Q1≈n/4, Q2≈n/2, Q3≈3n/4). Las 38 instancias TSPLIB van de n=48 a n=442, cubriendo tamaños chicos a medianos.

**P: ¿Por qué LKH-3 como referencia y no el óptimo?**
LKH-3 es uno de los mejores solvers para TSP y variantes; da los mejores valores conocidos (BKS) del benchmark, **cercanos al óptimo**. Es la referencia más fuerte disponible.

**P: Presupuesto de 15·n² evaluaciones de distancia. ¿Por qué?**
Es un presupuesto fijo y **escalado por el tamaño** para que todos los métodos compitan con el mismo "tiempo" independiente de la máquina, y comparable entre instancias de distinto n.

**P: 10 corridas por método estocástico, ¿alcanza? ¿Hiciste tests de significancia?**
Reporto mediana/promedio sobre 10 corridas, suficiente para la tendencia. **No** apliqué tests estadísticos formales (Wilcoxon/Friedman); reconozco que sería una mejora y lo dejo como trabajo futuro.

**P: ¿Usaste instancias sintéticas en los resultados finales?**
No. Los resultados reportados son sobre **TSPLIB real** con BKS de LKH-3. Las sintéticas solo sirven como respaldo cuando no hay red.

---

## 6. Resultados y análisis
**P: Los GAP son del 10–20% o más. Eso está lejos del óptimo. ¿Comentario?**
Son heurísticas, no métodos exactos, y la referencia (LKH-3) es extremadamente fuerte. El objetivo no es batir a LKH-3 sino **comparar métodos entre sí** de forma justa y reproducible; el GAP mide qué tan cerca llega cada uno.

**P: Farthest Insertion da ~98% de GAP en Q1. ¿No es un bug?**
No. FI inserta deliberadamente el nodo **más lejano** al tour; en el k-TSP eso **choca** con el objetivo de *seleccionar* nodos baratos de incluir, así que elige nodos caros y produce tours largos. Es un resultado coherente, no un error (lo validé).

**P: ¿No es contradictorio que NN "gane" en anytime pero no en calidad?**
No es contradicción: son **dos preguntas distintas**. El ranking anytime premia la **velocidad** (ERT/ECDF): NN llega a algo decente con muy pocas evaluaciones. La calidad final (GAP) premia **qué tan lejos llega**: ahí mandan Greedy y TS. Separar "rápido" de "mejor" es justamente el aporte de la metodología anytime.

---

## 7. Metodología anytime (Weise)
**P: ¿Por qué medir en evaluaciones de distancia y no en segundos?**
Para que la comparación **no dependa del hardware, el lenguaje ni la carga de la máquina**. Es una medida reproducible entre equipos (propuesta de Weise et al.).

**P: ¿Por qué escalar por n²?**
Para poder **agregar** curvas de instancias de distinto tamaño en un mismo eje.

**P: ¿Qué son ERT y ECDF?**
ERT = evaluaciones esperadas para alcanzar un error meta (con reinicios, las fallidas aportan el presupuesto completo). ECDF = fracción de corridas que alcanzan ese error meta a lo largo del tiempo.

---

## 8. Reproducibilidad e ingeniería
**P: ¿Cómo garantizas la reproducibilidad?**
Semillas fijas en los métodos estocásticos; los deterministas (NN, NI, FI, DCIH) dan siempre el mismo resultado; todo el pipeline regenera tablas y figuras con **un comando**; y cada experimento corresponde a un **commit** en un repositorio privado de GitHub.

**P: ¿Dónde corriste los experimentos?**
Localmente en Visual Studio Code, Python 3.10 (numpy/pandas/matplotlib), con el binario oficial de LKH-3 compilado. Como el tiempo es independiente de máquina, el hardware no afecta la comparación.

---

## 9. Limitaciones y trabajo futuro (adelántate tú)
- **Sin tuning de parámetros** de las metaheurísticas (fijos por equidad) → afinarlos mejoraría resultados.
- **Sin tests estadísticos** formales de significancia.
- **Brecha a LKH-3** aún grande → metaheurísticas más potentes o **híbridas** (memético TS+GA, ACO, VNS).
- Reglas de **selección de nodos** dedicadas (hoy la selección se apoya solo en el costo de inserción).
- Extender a **instancias más grandes** y a problemas de ruteo selectivo relacionados.

---

## 10. Preguntas "meta" / trampa
**P: ¿Cuál es TU aporte concreto?**
(1) Una comparación reproducible y documentada de 10 métodos para el k-TSP; (2) la heurística determinista **DCIH**; (3) una evaluación **anytime** (independiente de máquina) frente a LKH-3, que escaseaba para el k-TSP; (4) un repositorio que cualquiera puede re-ejecutar.

**P: ¿Usaste IA? ¿Cómo lo declaras?**
Sí, como apoyo (redacción/estilo en inglés, organización, depuración/documentación de código y generación de figuras **a partir de mis propios datos**). Todo el contenido científico —modelo, algoritmos, protocolo, datos, resultados y conclusiones— es mío. Está declarado explícitamente en la tesis.

**P: ¿Por qué esto amerita una tesis/paper?**
Porque aporta evidencia empírica reproducible sobre un problema poco comparado de forma sistemática, con una metodología de evaluación moderna (anytime) y una propuesta propia, y está preparado para ser enviado a un congreso cuando se finalicen las revisiones.

---

### Consejo final
Si no sabes una respuesta, no inventes: reconoce la limitación y conéctala con el **trabajo futuro**. Muestra que entiendes *por qué* cada decisión se tomó así. Ten a la vista: los números clave (sección 0), la diferencia DCIH vs Greedy (sección 4) y el argumento "rápido ≠ mejor" (sección 6).
