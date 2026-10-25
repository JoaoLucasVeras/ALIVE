from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(r"C:\Users\Joaol\Documents\ChatGPT\ALIVE")
ASSETS = ROOT / "assets"
OUT = ROOT / "ALIVE_Project_Proposal.docx"
HERO = ASSETS / "trait-graph-concept.png"
TIMELINE = ASSETS / "world-regime-timeline.png"
TRAIT_GRAPH = ASSETS / "trait-module-graph.png"

NAVY, BLUE, CYAN, AMBER = "102A43", "167D9A", "27B7D6", "E49A27"
INK, MUTED, PALE, LIGHT, WHITE = "243B53", "627D98", "EAF5F7", "F4F6F9", "FFFFFF"


def color(v): return RGBColor.from_string(v)


def set_font(run, size=11, bold=False, italic=False, name="Calibri", hex_color=INK):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.bold, run.italic = bold, italic
    run.font.color.rgb = color(hex_color)


def shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    tag = tcpr.find(qn("w:shd"))
    if tag is None:
        tag = OxmlElement("w:shd")
        tcpr.append(tag)
    tag.set(qn("w:fill"), fill)


def margins(cell, top=90, start=120, bottom=90, end=120):
    tcpr = cell._tc.get_or_add_tcPr()
    mar = tcpr.first_child_found_in("w:tcMar")
    if mar is None:
        mar = OxmlElement("w:tcMar")
        tcpr.append(mar)
    for key, val in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        element = mar.find(qn(f"w:{key}"))
        if element is None:
            element = OxmlElement(f"w:{key}")
            mar.append(element)
        element.set(qn("w:w"), str(val)); element.set(qn("w:type"), "dxa")


def geometry(table, widths, indent=120):
    table.autofit = False
    pr = table._tbl.tblPr
    for name, value in (("tblW", sum(widths)), ("tblInd", indent)):
        el = pr.find(qn(f"w:{name}"))
        if el is None:
            el = OxmlElement(f"w:{name}"); pr.append(el)
        el.set(qn("w:w"), str(value)); el.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid): grid.remove(child)
    for width in widths:
        el = OxmlElement("w:gridCol"); el.set(qn("w:w"), str(width)); grid.append(el)
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            tcpr = cell._tc.get_or_add_tcPr(); tcw = tcpr.find(qn("w:tcW"))
            if tcw is None: tcw = OxmlElement("w:tcW"); tcpr.append(tcw)
            tcw.set(qn("w:w"), str(widths[i])); tcw.set(qn("w:type"), "dxa")
            margins(cell)


def repeat_header(row):
    pr = row._tr.get_or_add_trPr(); el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true"); pr.append(el)


def add_page_number(p):
    r = p.add_run(); begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    inst = OxmlElement("w:instrText"); inst.set(qn("xml:space"), "preserve"); inst.text = " PAGE "
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t"); txt.text = "1"
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    for el in (begin, inst, sep, txt, end): r._r.append(el)
    set_font(r, size=9, hex_color=MUTED)


def alt(shape, title, description):
    shape._inline.docPr.set("title", title); shape._inline.docPr.set("descr", description)


def p(doc, text="", size=11, bold=False, italic=False, color_value=INK, align=None, after=6):
    para = doc.add_paragraph(); para.paragraph_format.space_after = Pt(after)
    if align is not None: para.alignment = align
    set_font(para.add_run(text), size, bold, italic, hex_color=color_value)
    return para


def heading(doc, text, level=1):
    para = doc.add_paragraph(style=f"Heading {level}")
    para.add_run(text); para.paragraph_format.keep_with_next = True
    return para


def bullet(doc, text, lead=None):
    para = doc.add_paragraph(style="List Bullet")
    if lead and text.startswith(lead):
        set_font(para.add_run(lead), bold=True)
        set_font(para.add_run(text[len(lead):]))
    else: set_font(para.add_run(text))
    return para


def callout(doc, label, text, fill=PALE, accent=BLUE):
    table = doc.add_table(rows=1, cols=1); table.alignment = WD_TABLE_ALIGNMENT.LEFT
    cell = table.cell(0, 0); shade(cell, fill); margins(cell, 150, 180, 150, 180)
    para = cell.paragraphs[0]; para.paragraph_format.space_after = Pt(0)
    set_font(para.add_run(label.upper() + "  "), size=9.5, bold=True, hex_color=accent)
    set_font(para.add_run(text), size=10.7, bold=True, hex_color=NAVY)
    geometry(table, [9360])
    spacer = doc.add_paragraph(); spacer.paragraph_format.space_after = Pt(0)


def timeline_image():
    im = Image.new("RGB", (1800, 520), "#F7FAFC"); d = ImageDraw.Draw(im)
    try:
        normal = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 31)
        bold = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 33)
        small = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 23)
    except OSError:
        normal = bold = small = ImageFont.load_default()
    regimes = [
        ("Stable abundance", "Broad availability\nfast regrowth", "#27B7D6"),
        ("Patchy scarcity", "Concentrated patches\nslow regrowth", "#E49A27"),
        ("Moving opportunities", "Scheduled patch\nrelocation", "#8B5FBF"),
        ("Recovery", "Return to broad\navailability", "#167D9A"),
    ]
    x, width, y, h = 65, 410, 165, 190
    d.text((65, 55), "Pre-registered world schedule (illustrative)", fill="#102A43", font=bold)
    for i, (title, desc, fill) in enumerate(regimes):
        xi = x + i * 435
        d.rounded_rectangle((xi, y, xi + width, y + h), radius=22, fill=fill)
        box = d.textbbox((0, 0), title, font=bold); tw = box[2] - box[0]
        d.text((xi + (width - tw) / 2, y + 42), title, fill="white", font=bold)
        for n, line in enumerate(desc.split("\n")):
            box = d.textbbox((0, 0), line, font=normal); tw = box[2] - box[0]
            d.text((xi + (width - tw) / 2, y + 100 + n * 36), line, fill="white", font=normal)
        if i < 3:
            d.polygon([(xi+width+12, 250), (xi+width+38, 230), (xi+width+38, 242), (xi+width+70, 242), (xi+width+70, 258), (xi+width+38, 258), (xi+width+38, 270)], fill="#627D98")
        d.text((xi + 115, 390), f"Turnovers {i*200}–{(i+1)*200}", fill="#243B53", font=small)
    im.save(TIMELINE)


def trait_graph_image():
    """Create a readable top-down module graph for the proposal."""
    width, height = 1800, 980
    im = Image.new("RGB", (width, height), "#F7FAFC")
    draw = ImageDraw.Draw(im)
    try:
        title_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 32)
        node_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 22)
        small_font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 18)
    except OSError:
        title_font = node_font = small_font = ImageFont.load_default()

    def label_box(center, label, fill, w, h, text_fill="#FFFFFF"):
        x, y = center
        draw.rounded_rectangle((x-w//2, y-h//2, x+w//2, y+h//2), radius=20, fill=fill, outline="#FFFFFF", width=4)
        lines = label.split("\n")
        total = sum(draw.textbbox((0, 0), line, font=node_font)[3] - draw.textbbox((0, 0), line, font=node_font)[1] for line in lines) + (len(lines)-1)*4
        current = y - total/2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=node_font)
            tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text((x-tw/2, current), line, font=node_font, fill=text_fill)
            current += th + 4

    root = (900, 120)
    families = [
        (150, "Mobility", "#27B7D6"),
        (450, "Sensing", "#4D9DE0"),
        (750, "Resource\nuse", "#2D936C"),
        (1050, "Protection", "#8B5FBF"),
        (1350, "Interaction", "#E49A27"),
        (1650, "Adaptability", "#167D9A"),
    ]
    leaves = {
        "Mobility": ["Efficient\nmovement", "Burst\nmovement"],
        "Sensing": ["Resource\ndetection", "Transition\ndetection"],
        "Resource\nuse": ["Efficient\nharvesting", "Energy\nstorage"],
        "Protection": ["Passive\nprotection", "Avoidance\nresponse"],
        "Interaction": ["Contesting", "Disruption"],
        "Adaptability": ["Low-cost\nswitching", "Generalist\nconfiguration"],
    }
    family_y, leaf_y = 390, 710
    # Connections are drawn before nodes so node edges remain clean.
    for x, family, fill in families:
        draw.line((root[0], root[1]+58, x, family_y-55), fill="#A8BED0", width=7)
        for offset in (-82, 82):
            draw.line((x, family_y+55, x+offset, leaf_y-55), fill="#A8BED0", width=6)
    label_box(root, "Core configuration", "#102A43", 350, 116)
    for x, family, fill in families:
        label_box((x, family_y), family, fill, 230, 110)
        for offset, leaf in zip((-82, 82), leaves[family]):
            label_box((x+offset, leaf_y), leaf, "#FFFFFF", 145, 112, "#243B53")
            # Add a restrained colored outline to leaf nodes.
            lx, ly = x+offset, leaf_y
            draw.rounded_rectangle((lx-72, ly-56, lx+72, ly+56), radius=18, outline=fill, width=5)
    draw.text((50, 26), "Illustrative top-down module graph", font=title_font, fill="#102A43")
    draw.text((50, 910), "Each path requires prerequisites, carries an energy cost, and can be favored by different resource regimes.", font=small_font, fill="#627D98")
    im.save(TRAIT_GRAPH)


def configure(doc):
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.top_margin, section.bottom_margin = Inches(.74), Inches(.72)
    section.left_margin, section.right_margin = Inches(1), Inches(1)
    section.header_distance, section.footer_distance = Inches(.38), Inches(.38)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"; normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri"); normal.font.size = Pt(11)
    normal.font.color.rgb = color(INK); normal.paragraph_format.space_after = Pt(6); normal.paragraph_format.line_spacing = 1.1
    for n, s, c, before, after in (("Heading 1",16,NAVY,16,8),("Heading 2",13,BLUE,12,6),("Heading 3",12,NAVY,8,4)):
        st=doc.styles[n]; st.font.name="Calibri"; st._element.rPr.rFonts.set(qn("w:ascii"),"Calibri")
        st._element.rPr.rFonts.set(qn("w:hAnsi"),"Calibri"); st.font.size=Pt(s); st.font.bold=True; st.font.color.rgb=color(c)
        st.paragraph_format.space_before=Pt(before); st.paragraph_format.space_after=Pt(after); st.paragraph_format.keep_with_next=True
    b=doc.styles["List Bullet"]; b.font.name="Calibri"; b.font.size=Pt(11); b.paragraph_format.left_indent=Inches(.5); b.paragraph_format.first_line_indent=Inches(-.25); b.paragraph_format.space_after=Pt(5); b.paragraph_format.line_spacing=1.1
    hp=section.header.paragraphs[0]; hp.alignment=WD_ALIGN_PARAGRAPH.RIGHT; set_font(hp.add_run("PROJECT PROPOSAL"),size=8.5,bold=True,hex_color=MUTED)
    fp=section.footer.paragraphs[0]; fp.alignment=WD_ALIGN_PARAGRAPH.RIGHT; set_font(fp.add_run("ALIVE   |   "),size=9,hex_color=MUTED); add_page_number(fp)


def add_cover(doc):
    p(doc, "MASTER'S PROJECT PROPOSAL", 9.5, True, color_value=AMBER, after=2)
    p(doc, "ALIVE", 32, True, color_value=NAVY, after=3)
    p(doc, "Trait-Graph Evolution in Changing Worlds", 16, False, color_value=BLUE, after=4)
    p(doc, "A Spore-inspired simulation of modular adaptation under controlled environmental change", 13.5, color_value=BLUE, after=13)
    para = doc.add_paragraph(); para.alignment=WD_ALIGN_PARAGRAPH.CENTER; para.paragraph_format.space_after=Pt(8)
    shape=para.add_run().add_picture(str(HERO),width=Inches(6.5)); alt(shape,"Trait-graph co-evolution concept","Two abstract populations explore branching trait pathways in a finite resource world.")
    p(doc,"Concept visualization: a visual language for modular body plans and evolutionary pathways; no game assets are used.",8.5,False,True,MUTED,WD_ALIGN_PARAGRAPH.CENTER,10)
    callout(doc,"Core question","Does reciprocal evolution help populations maintain and generate more adaptable modular trait pathways when the world changes?",PALE,BLUE)
    doc.add_page_break()


def add_model(doc):
    heading(doc,"Abstract",1)
    abstract=("This project proposes a GPU-accelerated evolutionary simulation in which two populations of digital agents compete under finite resources while adapting to researcher-controlled changes in their environment. Agents inherit a modular, branching trait graph inspired by the functional part systems of creature-creation games: continuous traits determine the magnitude of capabilities, while graph modules determine the kinds of capabilities available. Unlike a game progression system, modules are not selected by a player; mutation proposes local changes and natural selection determines which body plans persist. The central experiment compares one-sided and reciprocal evolution under a preregistered schedule of resource regimes, including stable abundance, patchy scarcity, moving opportunities, and recovery. Outcomes quantify trait-graph depth, persistent branch diversity, historical novelty, adaptation lag, recovery when earlier worlds return, and cross-play against archived populations. The study tests sustained diversification and adaptation under explicit environmental variation, not unlimited open-ended evolution.")
    p(doc,abstract,10.4,after=11)
    heading(doc,"1. Research model",1)
    p(doc,"The project uses a visual, modular trait-graph model to make evolutionary pathways legible while retaining a rigorous fixed-shape GPU simulation. Spore is a design reference for readable functional parts, not a copied game system or scientific model.")
    heading(doc,"Research question and hypothesis",2)
    callout(doc,"Question","Does reciprocal evolution produce more diverse, persistent, and adaptable trait pathways than one-sided evolution when environmental regimes change?",LIGHT,BLUE)
    bullet(doc,"Reciprocal adaptation is expected to preserve or generate a wider range of viable trait combinations.")
    bullet(doc,"Environmental transitions should make different modules useful at different times, preventing a single universally optimal build.")
    bullet(doc,"A return to an earlier world will test whether populations retain, re-evolve, or replace previous specializations.")
    heading(doc,"World and agent design",2)
    bullet(doc,"A two-dimensional grid contains finite, regrowing resource values arranged according to the active world regime.")
    bullet(doc,"Two populations share the grid. Agents move, consume resources, interact, expend energy, reproduce, mutate, and die.")
    bullet(doc,"A fixed-capacity agent pool and alive mask maintain GPU-friendly JAX array shapes throughout births and deaths.")
    bullet(doc,"The researcher changes the world on a predetermined schedule; agents do not alter terrain or resource rules.")
    heading(doc,"Behavior policy",2)
    p(doc,"Each population uses one shared trait-conditioned policy. The policy receives local resource information, nearby agents, energy, and the agent's active-module representation. For the primary study, policies are pretrained across all planned regimes and then frozen. This separates behavioral competence from evolutionary selection.")


def add_traits(doc):
    heading(doc,"2. Trait architecture",1)
    p(doc,"The phenotype has two layers. Continuous traits determine how strongly an agent expresses a capability; graph modules determine what categories of capability it has. This avoids an unstructured list of dozens of independent values.")
    headers=["Continuous trait","Role","Typical trade-off"]
    rows=[
        ("trait_0 - scale","Capability and action magnitude","Higher per-step metabolic cost"),
        ("trait_1 - protection","Resistance to interaction pressure","Ongoing maintenance cost"),
        ("trait_2 - intensity","Strength of resource contests","Greater energy expenditure"),
        ("trait_3 - efficiency","Energy obtained per resource unit","Less flexibility or mobility"),
        ("trait_4 - sensing","Range or quality of local information","Maintenance cost"),
        ("trait_5 - storage","Energy retained across scarcity","Lower movement efficiency"),
        ("trait_6 - flexibility","Behavior switching across regimes","Reduced peak specialization"),
        ("trait_7 - recovery","Recovery following costly events","Higher baseline demand"),
    ]
    table=doc.add_table(rows=1,cols=3); table.style="Table Grid"; table.alignment=WD_TABLE_ALIGNMENT.LEFT
    for i,h in enumerate(headers): shade(table.rows[0].cells[i],NAVY); set_font(table.rows[0].cells[i].paragraphs[0].add_run(h),9.3,True,hex_color=WHITE)
    repeat_header(table.rows[0])
    for j,row in enumerate(rows):
        cells=table.add_row().cells
        for i,item in enumerate(row):
            if j%2==1: shade(cells[i],LIGHT)
            set_font(cells[i].paragraphs[0].add_run(item),9.1,bold=(i==0))
            cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    geometry(table,[2500,3400,3460])
    heading(doc,"Module graph",2)
    p(doc,"A graph of approximately 24-30 modules gives the project depth without turning it into an unconstrained invention system. Modules require prerequisites, incur energy costs, and can be beneficial only in particular resource regimes.")
    para=doc.add_paragraph(); para.alignment=WD_ALIGN_PARAGRAPH.CENTER; para.paragraph_format.space_after=Pt(5)
    shape=para.add_run().add_picture(str(TRAIT_GRAPH),width=Inches(6.5))
    alt(shape,"Top-down trait module graph","A core configuration connects to six module families, each branching to two example functional modules.")
    p(doc,"The graph is illustrative: final modules, prerequisites, incompatibilities, and costs are fixed after calibration and before confirmatory runs.",8.4,False,True,MUTED,WD_ALIGN_PARAGRAPH.CENTER,2)


def add_worlds_experiment(doc):
    doc.add_page_break(); heading(doc,"3. Controlled world change",1)
    p(doc,"The environment is an experimental treatment. Regime changes are defined before any confirmatory run and are identical across paired conditions. This prevents the researchers from tuning the world after observing which strategy wins.")
    para=doc.add_paragraph(); para.alignment=WD_ALIGN_PARAGRAPH.CENTER; para.paragraph_format.space_after=Pt(6)
    shape=para.add_run().add_picture(str(TIMELINE),width=Inches(6.5)); alt(shape,"World regime schedule","Four researcher-controlled resource regimes occur at fixed turnover intervals.")
    p(doc,"Illustrative schedule only. Exact durations and parameters will be fixed after ecological calibration, then preregistered before confirmatory runs.",8.5,False,True,MUTED,WD_ALIGN_PARAGRAPH.CENTER,7)
    heading(doc,"World regimes",2)
    headers=["Regime","Resource pattern","Trait pressure"]
    rows=[
        ("Stable abundance","Broad availability; fast regrowth","Low-cost harvesting and simple configurations"),
        ("Patchy scarcity","Concentrated patches; slow regrowth","Sensing, storage, efficiency, targeted movement"),
        ("Moving opportunities","Resource patches relocate predictably","Mobility, transition sensing, flexible policies"),
        ("Recovery","Return to broad availability","Retention, re-evolution, or replacement of strategies"),
    ]
    table=doc.add_table(rows=1,cols=3); table.style="Table Grid"; table.alignment=WD_TABLE_ALIGNMENT.LEFT
    for i,h in enumerate(headers): shade(table.rows[0].cells[i],NAVY); set_font(table.rows[0].cells[i].paragraphs[0].add_run(h),9.3,True,hex_color=WHITE)
    repeat_header(table.rows[0])
    for j,row in enumerate(rows):
        cells=table.add_row().cells
        for i,item in enumerate(row):
            if j%2: shade(cells[i],LIGHT)
            set_font(cells[i].paragraphs[0].add_run(item),9.1,bold=(i==0)); cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    geometry(table,[1850,3000,4510])
    heading(doc,"Experimental conditions",2)
    p(doc,"Stage 1 establishes the static-world baseline. Stage 2 reuses the same evolutionary conditions under the world-change schedule. A-only and B-only are both required because the two populations are not assumed to be symmetric.")
    headers=["Condition","Population A","Population B","World"]
    rows=[
        ("Frozen baseline","Frozen","Frozen","Stable"),
        ("A-only baseline","Evolves","Frozen","Stable"),
        ("B-only baseline","Frozen","Evolves","Stable"),
        ("Reciprocal baseline","Evolves","Evolves","Stable"),
        ("A-only changing","Evolves","Frozen","Scheduled changes"),
        ("B-only changing","Frozen","Evolves","Scheduled changes"),
        ("Reciprocal changing","Evolves","Evolves","Scheduled changes"),
    ]
    table=doc.add_table(rows=1,cols=4); table.style="Table Grid"; table.alignment=WD_TABLE_ALIGNMENT.LEFT
    for i,h in enumerate(headers): shade(table.rows[0].cells[i],NAVY); set_font(table.rows[0].cells[i].paragraphs[0].add_run(h),9.2,True,hex_color=WHITE)
    repeat_header(table.rows[0])
    for j,row in enumerate(rows):
        cells=table.add_row().cells
        for i,item in enumerate(row):
            if j==6: shade(cells[i],PALE)
            set_font(cells[i].paragraphs[0].add_run(item),9.0,bold=(i==0 or j==6),hex_color=NAVY if j==6 else INK)
    geometry(table,[2400,1800,1800,3360])


def add_analysis_and_plan(doc):
    heading(doc,"4. Evaluation, implementation, and delivery",1)
    heading(doc,"Primary measurements",2)
    items=[
        ("Trait-graph depth","How far persistent lineages move from the core configuration."),
        ("Persistent branch diversity","How many distinct module combinations remain viable across turnover time."),
        ("Historical novelty","Whether later successful configurations differ from all earlier successful configurations."),
        ("Adaptation lag","How long population performance takes to stabilize after a regime transition."),
        ("Recovery response","Whether previous specializations return, are retained, or are replaced after a familiar world returns."),
        ("Cross-play","Whether later populations outperform archived populations under standardized environments, separating escalation from cycling."),
    ]
    for title, desc in items: bullet(doc, title + ": " + desc, title + ":")
    heading(doc,"Implementation phases",2)
    phases=[
        ("0","Design lock","Finalize module graph, regime equations, metric definitions, and success criteria."),
        ("1","Core world","Implement fixed-shape grid, energy economics, resource regrowth, births, and deaths."),
        ("2","Trait graph","Add inheritance, mutation, costs, prerequisites, and lineage tracking."),
        ("3","Policies","Pretrain and validate trait-conditioned policies across all planned regimes."),
        ("4","Validation","Benchmark throughput; validate novelty and cycling metrics using synthetic trajectories."),
        ("5","Experiments","Run static baselines, scheduled-change conditions, cross-play, and statistical analysis."),
    ]
    table=doc.add_table(rows=0,cols=3); table.style="Table Grid"; table.alignment=WD_TABLE_ALIGNMENT.LEFT
    for number,name,detail in phases:
        cells=table.add_row().cells; shade(cells[0],BLUE); shade(cells[1],PALE)
        cells[0].vertical_alignment=cells[1].vertical_alignment=cells[2].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        cp=cells[0].paragraphs[0]; cp.alignment=WD_ALIGN_PARAGRAPH.CENTER; set_font(cp.add_run(number),11,True,hex_color=WHITE)
        set_font(cells[1].paragraphs[0].add_run(name),9.8,True,hex_color=NAVY); set_font(cells[2].paragraphs[0].add_run(detail),9.3)
    geometry(table,[600,1800,6960])
    heading(doc,"Time and compute planning",2)
    p(doc,"The expected project duration is 16-22 weeks. Early development should use scripted behavior and small worlds; the GPU benchmark determines the final scale. With frozen policies during evolutionary runs, the full project is estimated at roughly 100-250 GPU-hours: 20-60 for policy training and calibration, 25-70 for development experiments, 60-150 for replicated confirmatory runs, and under 10 for cross-play evaluation.")
    heading(doc,"Scope boundaries and end goals",2)
    bullet(doc,"Core scope: 20-30 modules, eight continuous traits, one resource type, three to four world regimes, two populations, and one fixed schedule.")
    bullet(doc,"Out of primary scope: agent-created environmental modification, arbitrary trait invention, 3D body physics, and online learning during confirmatory evolutionary runs.")
    bullet(doc,"Final deliverables: reproducible JAX simulator, benchmark, configs and seeds, trait-lineage visualizations, world-transition analyses, cross-play results, and a thesis-ready statistical report.")
    heading(doc,"Pre-build decisions",2)
    bullet(doc,"Lock the first module graph and its costs before policy pretraining; add modules only through versioned design changes.")
    bullet(doc,"Choose the resource-regime schedule during calibration, then freeze it before confirmatory runs.")
    bullet(doc,"Define the adaptation metric and persistence window using synthetic trajectories before examining main results.")
    bullet(doc,"Treat a null result, convergence, cycling, or collapse as interpretable results rather than grounds for post-hoc world tuning.")
    callout(doc,"Defensible final claim","The project tests whether reciprocal evolution supports sustained modular diversification and faster adaptation under controlled environmental variation; it does not claim to prove unlimited open-ended evolution.","FFF5E6",AMBER)


def build():
    ASSETS.mkdir(parents=True, exist_ok=True); timeline_image(); trait_graph_image()
    doc=Document(); configure(doc)
    add_cover(doc); add_model(doc); add_traits(doc); add_worlds_experiment(doc); add_analysis_and_plan(doc)
    doc.core_properties.title="ALIVE: Trait-Graph Evolution in Changing Worlds"
    doc.core_properties.subject="Master's project proposal"
    doc.core_properties.author="Research Project Team"
    doc.save(OUT); print(OUT)


if __name__ == "__main__": build()
