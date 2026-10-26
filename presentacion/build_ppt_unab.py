#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construye la presentación k-TSP sobre la plantilla institucional UNAB
(Anexo12_-Formato-PPT.pptx): portada roja + banda roja con logo en cada
diapositiva de contenido, más pie de página y número de página.
Todo el contenido está adaptado al protocolo de Pandiri & Singh.
"""
import copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

TEMPLATE = "/tmp/tmpl/t.pptx"
BAND = "/tmp/tmpl/x/ppt/media/image2.jpg"     # banda roja superior
LOGO = "/tmp/tmpl/x/ppt/media/image4.png"     # logo UNAB
OUT = "presentacion_ktsp_UNAB.pptx"

NAVY = RGBColor(0x1F, 0x2A, 0x44)
MAROON = RGBColor(0x9B, 0x1B, 0x30)
DARK = RGBColor(0x20, 0x24, 0x2E)
MUTED = RGBColor(0x5B, 0x64, 0x72)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
NAVYFILL = RGBColor(0x1F, 0x2A, 0x44)
ROWALT = RGBColor(0xF4, 0xF5, 0xF7)
HLFILL = RGBColor(0xF3, 0xE1, 0xE4)
BODY = "Calibri"

prs = Presentation(TEMPLATE)
EMU_W = prs.slide_width
EMU_H = prs.slide_height

# ---- blank layout ("En blanco") ----
blank = None
for lay in prs.slide_layouts:
    if lay.name.strip().lower() in ("en blanco", "blank"):
        blank = lay
if blank is None:
    blank = prs.slide_layouts[6]

PAGE = [0]

def set_cover():
    s = prs.slides[0]
    repl = {
        "TÍTULO DEL PROYECTO":
            "Heuristic Approaches for the k-Traveling Salesman Problem",
        "EQUIPO DE INVESTIGADORES E INVESTIGADORAS":
            "Nicolás Barrientos   ·   Prof. guía: Dr. Gustavo Gatica",
        "FECHA DE POSTULACIÓN":
            "Proyecto de título · Ingeniería Civil Informática · UNAB · 2026",
    }
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            full = "".join(r.text for r in p.runs)
            if full in repl:
                # keep first run's formatting, set its text, clear the rest
                p.runs[0].text = repl[full]
                for r in p.runs[1:]:
                    r.text = ""

def delete_slides_from(idx):
    """Delete slides with position >= idx (keep slide 0 = cover)."""
    sldIdLst = prs.slides._sldIdLst
    ids = list(sldIdLst)
    for sid in ids[idx:]:
        rId = sid.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        prs.part.drop_rel(rId)
        sldIdLst.remove(sid)

def content_slide(title):
    s = prs.slides.add_slide(blank)
    # red band + logo
    s.shapes.add_picture(BAND, Emu(-18288), Emu(0), Inches(10.03), Inches(0.88))
    s.shapes.add_picture(LOGO, Inches(9.09), Inches(0.1), Inches(0.79), Inches(0.66))
    # title (white, bold)
    tb = s.shapes.add_textbox(Inches(0.3), Inches(0.14), Inches(8.5), Inches(0.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; r = p.add_run(); r.text = title
    r.font.size = Pt(26); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = BODY
    # footer + page number
    PAGE[0] += 1
    fb = s.shapes.add_textbox(Inches(0.3), Inches(7.12), Inches(8.0), Inches(0.3))
    fr = fb.text_frame.paragraphs[0].add_run()
    fr.text = "Proyecto de título · Nicolás Barrientos"
    fr.font.size = Pt(9); fr.font.color.rgb = MUTED; fr.font.name = BODY
    nb = s.shapes.add_textbox(Inches(9.1), Inches(7.12), Inches(0.6), Inches(0.3))
    np_ = nb.text_frame.paragraphs[0]; np_.alignment = PP_ALIGN.RIGHT
    nr = np_.add_run(); nr.text = str(PAGE[0])
    nr.font.size = Pt(10); nr.font.color.rgb = MUTED; nr.font.name = BODY
    return s

def add_bullets(s, items, x=0.45, y=1.15, w=9.1, h=5.6, size=16, gap=8):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for it in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(gap); p.line_spacing = 1.05
        r = p.add_run(); r.text = "•  " + it
        r.font.size = Pt(size); r.font.color.rgb = DARK; r.font.name = BODY
    return tb

def add_para(s, text, x=0.45, y=1.15, w=9.1, h=1.0, size=16, bold=False, color=DARK):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    r = tf.paragraphs[0].add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = BODY
    return tb

def add_image(s, path, x, y, w=None, h=None):
    kw = {}
    if w: kw["width"] = Inches(w)
    if h: kw["height"] = Inches(h)
    return s.shapes.add_picture(path, Inches(x), Inches(y), **kw)

def add_table(s, data, x, y, w, colw, fontsize=11, highlight=None, header=True):
    rows = len(data); cols = len(data[0])
    gt = s.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w),
                            Inches(0.33*rows)).table
    for ci, cwi in enumerate(colw):
        gt.columns[ci].width = Inches(cwi)
    for ri, row in enumerate(data):
        for ci, val in enumerate(row):
            c = gt.cell(ri, ci); c.margin_top = Pt(1); c.margin_bottom = Pt(1)
            c.margin_left = Pt(5); c.margin_right = Pt(5)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            para = c.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
            rn = para.add_run(); rn.text = str(val); rn.font.name = BODY
            rn.font.size = Pt(fontsize)
            if header and ri == 0:
                c.fill.solid(); c.fill.fore_color.rgb = NAVYFILL
                rn.font.color.rgb = WHITE; rn.font.bold = True
            else:
                hl = highlight and (row[0] in highlight)
                c.fill.solid()
                c.fill.fore_color.rgb = HLFILL if hl else (ROWALT if ri % 2 else WHITE)
                rn.font.color.rgb = MAROON if hl else DARK
                rn.font.bold = bool(hl)
    return gt

# ============================================================
set_cover()
delete_slides_from(1)   # remove template content slides, keep cover

# 1 Contexto
s = content_slide("Contexto y motivación")
add_bullets(s, [
 "La optimización de rutas está en todas partes: logística, transporte, vigilancia.",
 "El TSP clásico busca la ruta cerrada más corta que visita TODAS las ciudades.",
 "Muchos casos reales visitan solo un subconjunto, por un presupuesto de paradas.",
 "k-TSP: elegir k de n ciudades (con un depósito) y ordenarlas en un recorrido cerrado mínimo.",
])

# 2 Objetivos
s = content_slide("Objetivos")
add_para(s, "Objetivo general", y=1.1, size=15, bold=True, color=MAROON, h=0.4)
add_bullets(s, [
 "Un repositorio reproducible que modela, resuelve y compara el k-TSP contra LKH-3.",
], y=1.5, size=15, h=0.8)
add_para(s, "Objetivos específicos", y=2.2, size=15, bold=True, color=MAROON, h=0.4)
add_bullets(s, [
 "Formular el problema (selección de nodos, grado, eliminación de subtours — MTZ).",
 "Implementar diez métodos sobre un núcleo común de búsqueda local.",
 "Evaluar la calidad (GAP vs LKH-3) sobre las 76 instancias de Pandiri & Singh × tres k.",
 "Comparar estadísticamente (Wilcoxon) contra el GVNS y las hiper-heurísticas de ese trabajo.",
 "Liberar todo para regenerarlo con un comando.",
], y=2.6, size=15)

# 3 Metodología
s = content_slide("Metodología de trabajo")
add_bullets(s, [
 "Diseño de datos: ADTs uniformes para instancias TSPLIB; codificación por subconjunto + orden.",
 "Modelo matemático: formulación de un solo tour con selección de nodos y MTZ.",
 "Resolución heurística: diez métodos sobre un núcleo común (2-opt, intercambio, inserción).",
 "Evaluación experimental: protocolo de Pandiri & Singh — límites de tiempo, 10 corridas, Wilcoxon.",
], size=16)
add_para(s, "Todo en Python, en VS Code, versionado en GitHub privado, con LKH-3 local.",
         y=5.4, size=13, color=MUTED, h=0.4)

# 4 Problema
s = content_slide("El problema de investigación")
add_bullets(s, [
 "Dadas n ciudades con depósito y un k fijo: el recorrido cerrado más corto que visita exactamente k ciudades.",
 "Dos decisiones acopladas: CUÁLES k nodos y EN QUÉ orden.",
 "El número de combinaciones crece combinatorialmente → se necesitan heurísticas.",
 "El TSP es el caso particular k = n, así que el k-TSP es NP-hard.",
], w=5.6)
add_image(s, "ktsp_plot.png", x=6.2, y=1.4, w=3.4)

# 5 Modelo
s = content_slide("Modelo matemático")
add_bullets(s, [
 "Variables: x (arco en el tour), y (nodo seleccionado), u (orden, Miller–Tucker–Zemlin).",
 "Objetivo: minimizar la longitud total del tour, Σ c·x.",
 "Restricciones: el depósito siempre está; se visitan exactamente k nodos (Σy = k).",
 "Grado: cada nodo seleccionado tiene un arco de entrada y uno de salida.",
 "MTZ: eliminan subtours entre los nodos seleccionados.",
 "Deja explícitas las dos decisiones: selección (y) y orden (x).",
], size=16)

# 6 Benchmark
s = content_slide("Benchmark y protocolo (Pandiri & Singh)")
add_bullets(s, [
 "76 instancias estándar de TSPLIB (n de 14 a 783 ciudades).",
 "Tres valores de k, definidos como los CUARTILES del tamaño n:",
 "    · Small = ⌊n/4⌋ (Q1, un cuarto de las ciudades — domina la selección),",
 "    · Medium = ⌊n/2⌋ (Q2, la mitad), · Large = ⌊3n/4⌋ (Q3, tres cuartos — casi un TSP).",
 "Dos límites de tiempo de reloj: short run 0.05·n s y long run 0.2·n s; 10 corridas cada uno.",
 "76 × 3 = 228 casos de prueba, todos comparados contra el BKS de LKH-3.",
], size=15, gap=6)

# 7 Resultados por escenario (Fig1)
s = content_slide("Resultados: GAP medio vs LKH-3, por escenario")
add_image(s, "Fig1_gap_scenario.png", x=0.5, y=1.25, w=9.0)
add_para(s, "Barras claras: mis métodos. Barras rayadas (*): GVNS y hiper-heurísticas de Pandiri & Singh. Menor es mejor.",
         y=5.9, size=12, color=MUTED, h=0.5)

# 7b Tabla completa de resultados (GAP medio por método x escenario x criterio)
s = content_slide("Tabla de resultados — GAP medio (%)")
restab = [
 ["Método","Small","Medium","Large","Small","Medium","Large"],
 ["Greedy","4.73","9.11","11.59","4.46","8.43","10.41"],
 ["GRASP","14.26","14.72","13.34","13.12","13.80","12.43"],
 ["GA","18.46","14.42","11.05","13.82","10.49","8.70"],
 ["NN","19.48","20.54","15.46","19.48","20.54","15.46"],
 ["NI","16.82","19.38","18.78","16.82","19.38","18.78"],
 ["FI","102.34","57.52","34.05","102.34","57.52","34.05"],
 ["RI","42.57","23.26","13.47","38.48","21.94","12.25"],
 ["SA","10.06","12.80","13.19","9.79","12.42","12.86"],
 ["TS","7.04","10.13","11.00","6.23","9.08","9.42"],
 ["DCIH","15.45","20.11","17.06","15.45","20.11","17.06"],
 ["GVNS*","12.97","24.96","23.03","6.51","14.07","15.71"],
 ["HH_RAND*","3.09","9.56","11.55","2.42","4.50","6.22"],
 ["HH_GREEDY*","3.87","11.29","13.21","2.97","5.22","7.07"],
]
# column minima (bold best per data column)
bestcells = set()
for c in range(1, 7):
    vals = [(float(restab[r][c]), r) for r in range(1, len(restab))]
    bestcells.add((min(vals)[1], c))
# super-header (SR / LR spans)
sh = s.shapes.add_textbox(Inches(2.35), Inches(1.18), Inches(3.2), Inches(0.3))
shr = sh.text_frame.paragraphs[0]; shr.alignment = PP_ALIGN.CENTER
rr = shr.add_run(); rr.text = "Short run (0.05n s)"; rr.font.size = Pt(11); rr.font.bold = True; rr.font.color.rgb = MAROON; rr.font.name = BODY
sh2 = s.shapes.add_textbox(Inches(5.95), Inches(1.18), Inches(3.2), Inches(0.3))
shr2 = sh2.text_frame.paragraphs[0]; shr2.alignment = PP_ALIGN.CENTER
rr2 = shr2.add_run(); rr2.text = "Long run (0.2n s)"; rr2.font.size = Pt(11); rr2.font.bold = True; rr2.font.color.rgb = MAROON; rr2.font.name = BODY
# table
from pptx.util import Inches as _In
gt = s.shapes.add_table(len(restab), 7, Inches(0.45), Inches(1.5), Inches(9.1), Inches(0.3*len(restab))).table
for ci, cwi in enumerate([1.9,1.2,1.2,1.2,1.2,1.2,1.2]):
    gt.columns[ci].width = Inches(cwi)
for ri, row in enumerate(restab):
    for ci, val in enumerate(row):
        c = gt.cell(ri, ci); c.margin_top = Pt(0); c.margin_bottom = Pt(0)
        c.margin_left = Pt(4); c.margin_right = Pt(4); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        para = c.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        rn = para.add_run(); rn.text = val; rn.font.name = BODY; rn.font.size = Pt(10.5)
        if ri == 0:
            c.fill.solid(); c.fill.fore_color.rgb = NAVYFILL
            rn.font.color.rgb = WHITE; rn.font.bold = True
        else:
            isbest = (ri, ci) in bestcells
            c.fill.solid(); c.fill.fore_color.rgb = ROWALT if ri % 2 else WHITE
            rn.font.color.rgb = MAROON if isbest else DARK
            rn.font.bold = bool(isbest)
add_para(s, "GAP medio sobre las 76 instancias, por escenario de k (cuartiles) y criterio de tiempo. "
            "En negrita el mejor de cada columna. * = Pandiri & Singh (2020). Menor es mejor.",
         y=6.35, size=10.5, color=MUTED, h=0.6)

# 8 Comparación
s = content_slide("Comparación con el estado del arte")
rank = [["Método","GAP% medio"],
 ["HH_RAND*","6.2"],["HH_GREEDY*","7.3"],["Greedy","8.1"],["TS","8.8"],["SA","11.9"],
 ["GA","12.8"],["GRASP","13.6"],["GVNS*","16.2"],["DCIH","17.5"],["NI","18.3"],
 ["NN","18.5"],["RI","25.3"],["FI","64.6"]]
add_table(s, rank, x=0.45, y=1.15, w=3.9, colw=[2.5,1.4], fontsize=10.5,
          highlight={"Greedy","TS"})
add_bullets(s, [
 "GAP medio global (76 instancias × 3 k × SR/LR).",
 "Mi Greedy (8.1%) y Tabu Search (8.8%) quedan justo detrás de las hiper-heurísticas.",
 "Ambos superan claramente al GVNS (16.2%).",
 "Mi mejor método iguala o supera al mejor de Pandiri en 103/228 casos (SR) y a HH_GREEDY en 123/228.",
], x=4.7, y=1.3, w=5.0, size=13)
add_para(s, "* Resultados publicados de Pandiri & Singh (2020).", y=6.6, size=10.5, color=MUTED, h=0.3)

# 9 Wilcoxon (Fig2)
s = content_slide("Significancia estadística (Wilcoxon)")
add_image(s, "Fig2_boxplot_gap.png", x=0.4, y=1.2, w=6.1)
add_bullets(s, [
 "Test de Wilcoxon de rangos con signo, pareado por instancia.",
 "Greedy y TS son significativamente mejores que GVNS (p<0.05), SR y LR.",
 "En short run, Greedy incluso supera a HH_GREEDY; TS lo empata.",
 "HH_RAND se mantiene como el más fuerte, sobre todo en long run.",
], x=6.7, y=1.3, w=3.0, size=12)

# 10 Construcción
s = content_slide("Heurísticas (1/3): construcción")
add_bullets(s, [
 "Greedy: inserta el nodo más barato hasta k y refina (varios reinicios).",
 "Nearest Neighbor: avanza siempre al nodo más cercano.",
 "Nearest / Farthest Insertion: insertan el nodo más cercano o más lejano al tour.",
 "Random Insertion: inserta un nodo al azar, con reinicios.",
 "Todas comparten el mismo núcleo de búsqueda local.",
])

# 11 Metaheurísticas
s = content_slide("Heurísticas (2/3): metaheurísticas")
add_bullets(s, [
 "GRASP: construcción aleatorizada + búsqueda local, multi-arranque.",
 "Genético (GA): evoluciona el subconjunto y el orden (selección, cruce, mutación).",
 "Simulated Annealing: acepta empeoramientos con probabilidad exp(-Δ/T), enfriando.",
 "Tabu Search: búsqueda con memoria; toma el mejor movimiento no prohibido.",
 "Tabu Search es la mejor de mis metaheurísticas.",
])

# 12 DCIH
s = content_slide("Heurísticas (3/3): DCIH — la propuesta")
add_bullets(s, [
 "Fase 1: selecciona y ordena por costo marginal mínimo, con desempate por índice.",
 "Fase 2: refina con 2-opt e intercambio dentro/fuera hasta no mejorar.",
 "Totalmente determinista: mismos datos → mismo recorrido, sin azar ni semilla.",
 "Prioriza correctitud y reproducibilidad, con calidad comparable a las inserciones.",
])

# 13 Resultados global
s = content_slide("Resultados: comparación global")
add_bullets(s, [
 "Greedy (~8%) y Tabu Search son los más robustos de mis métodos.",
 "Ambos significativamente mejores que GVNS; competitivos con las hiper-heurísticas de Pandiri.",
 "El genético cierra la brecha para k grande, sobre todo en long run.",
 "Farthest Insertion es el más débil; DCIH es la opción determinista y reproducible.",
 "Diez métodos, comparados contra LKH-3 y contra el estado del arte.",
])

# 14 Efecto del tiempo
s = content_slide("Efecto del presupuesto de tiempo (SR vs LR)")
srlr = [["Método","SR (0.05n s)","LR (0.2n s)"],
 ["Greedy","8.5","7.8"],["TS","9.4","8.2"],["SA","12.0","11.7"],["GA","14.6","11.0"],
 ["GRASP","14.1","13.1"],["GVNS*","20.3","12.1"],["HH_RAND*","8.1","4.4"],["HH_GREEDY*","9.5","5.1"]]
add_table(s, srlr, x=0.45, y=1.2, w=4.6, colw=[1.9,1.35,1.35], fontsize=11)
add_bullets(s, [
 "GAP medio por método (promedio de los tres escenarios); menor es mejor.",
 "Los deterministas (NN, NI, FI, DCIH) no cambian: construyen una sola vez.",
 "El genético es el que más gana y es el mejor de mis métodos en Large bajo LR.",
 "Greedy y Tabu Search se mantienen robustos en ambos presupuestos.",
], x=5.3, y=1.3, w=4.4, size=13)

# 15 Conclusiones
s = content_slide("Conclusiones y trabajo futuro")
add_para(s, "Conclusiones", y=1.1, size=15, bold=True, color=MAROON, h=0.4)
add_bullets(s, [
 "Greedy y Tabu Search, los más robustos; ambos significativamente mejores que GVNS.",
 "Competitivo con las hiper-heurísticas de Pandiri en su propio benchmark y protocolo.",
 "GA destaca para k grande; Farthest Insertion es el más débil; DCIH, determinista y reproducible.",
], y=1.5, size=14)
add_para(s, "Trabajo futuro", y=4.1, size=15, bold=True, color=MAROON, h=0.4)
add_bullets(s, [
 "Metaheurísticas híbridas (memético TS+GA, ACO, VNS).",
 "Ajuste de parámetros por instancia; reglas de selección de nodos dedicadas.",
 "Instancias más grandes y problemas de ruteo selectivo relacionados.",
], y=4.5, size=14)

# 16 Referencias
s = content_slide("Referencias principales")
add_bullets(s, [
 "Pandiri & Singh (2020). Two multi-start heuristics for the k-TSP. OPSEARCH.",
 "Helsgaun (2017). LKH-3: extensión del solver Lin–Kernighan–Helsgaun.",
 "Knox (1994). Tabu search performance on the symmetric TSP (test de Wilcoxon). Computers & OR.",
 "Rosenkrantz, Stearns & Lewis (1977). Heuristics for the TSP. SIAM J. Computing.",
 "Feo & Resende (1995). GRASP. · Kirkpatrick et al. (1983). Simulated Annealing.",
 "Glover (1986); Glover & Laguna (1997). Tabu Search.",
 "Bibliografía completa (50 referencias) en la tesis y el paper.",
], size=14)

# ============================================================
#  BACKUP: per-instance tables by quartile (SR and LR)
# ============================================================
import pandas as pd
_df = pd.read_csv("../benchmark_weise/resultados_opsearch.csv")
_methods = ["Greedy","GRASP","GA","NN","NI","FI","RI","SA","TS","DCIH"]
_short = ["Grd","GRA","GA","NN","NI","FI","RI","SA","TS","DCIH"]

def divider(title, subtitle):
    s = content_slide(title)
    add_para(s, subtitle, y=3.0, size=18, bold=True, color=MAROON, w=9.1, h=1.0)

def bk_table(part, title):
    s = content_slide(title)
    head = ["Inst.","n","k"] + _short + ["LKH-3"]
    rows = [head]
    bold = set()
    for i, r in enumerate(part, start=1):
        rows.append(r)
        bks = r[-1]
        for ci in range(3, 3+len(_methods)):
            if r[ci] == bks:
                bold.add((i, ci))
    nrow = len(rows); ncol = len(head)
    gt = s.shapes.add_table(nrow, ncol, Inches(0.3), Inches(1.05),
                            Inches(9.4), Inches(0.155*nrow)).table
    widths = [0.95,0.42,0.42] + [0.63]*10 + [0.72]
    for ci, wv in enumerate(widths):
        gt.columns[ci].width = Inches(wv)
    for ri in range(nrow):
        gt.rows[ri].height = Inches(0.15)
        for ci in range(ncol):
            c = gt.cell(ri, ci)
            c.margin_top = Pt(0); c.margin_bottom = Pt(0)
            c.margin_left = Pt(2); c.margin_right = Pt(2)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            para = c.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
            rn = para.add_run(); rn.text = str(rows[ri][ci]); rn.font.name = BODY
            rn.font.size = Pt(8)
            if ri == 0:
                c.fill.solid(); c.fill.fore_color.rgb = NAVYFILL
                rn.font.color.rgb = WHITE; rn.font.bold = True
            else:
                c.fill.solid(); c.fill.fore_color.rgb = ROWALT if ri % 2 else WHITE
                if (ri, ci) in bold:
                    rn.font.color.rgb = MAROON; rn.font.bold = True
                else:
                    rn.font.color.rgb = DARK

divider("Material de respaldo", "Tablas por instancia y cuartil (longitud de tour por método)")

_scen = [("Small","Q1 · k=⌊n/4⌋"),("Medium","Q2 · k=⌊n/2⌋"),("Large","Q3 · k=⌊3n/4⌋")]
for crit, cname in [("SR","Short run 0.05n s"), ("LR","Long run 0.2n s")]:
    for scen, slabel in _scen:
        sub = _df[(_df.Criterion==crit)&(_df.Scenario==scen)].sort_values("Instance")
        data = []
        for _, r in sub.iterrows():
            row = [r["Instance"], int(r["n"]), int(r["k"])]
            row += [int(round(r[f"{m}_best"])) for m in _methods]
            row += [int(round(r["LKH3_BKS"]))]
            data.append(row)
        half = (len(data)+1)//2
        for pi, chunk in enumerate([data[:half], data[half:]], start=1):
            bk_table(chunk, f"Respaldo — {slabel} · {cname}  ({pi}/2)")

prs.save(OUT)
print("OK:", OUT, "| slides:", len(prs.slides._sldIdLst))
