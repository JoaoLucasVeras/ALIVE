from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(r"C:\Users\Joaol\Documents\ChatGPT\ALIVE")
ASSETS = ROOT / "assets" / "blueprint"
OUT = ROOT / "ALIVE_Comprehensive_Project_Blueprint.docx"

BLACK = "000000"
NAVY = "17324D"
BLUE = "2E75B6"
TEAL = "16869A"
GREEN = "397D64"
GOLD = "B7791F"
PURPLE = "7656A3"
GRAY = "666666"
LIGHT = "F3F6F8"
PALE_BLUE = "EAF2F8"
WHITE = "FFFFFF"
BORDER = "D9D9D9"


def rgb(value):
    return RGBColor.from_string(value)


def set_run(run, size=11, bold=False, italic=False, color=BLACK, font="Aptos"):
    run.font.name = font
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), font)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), font)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = rgb(color)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=100, start=130, bottom=100, end=130):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color=BORDER, size="8"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), size)
        node.set(qn("w:color"), color)


def set_table_geometry(table, widths, indent=120):
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    for tag, value in (("tblW", sum(widths)), ("tblInd", indent)):
        node = tbl_pr.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tbl_pr.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        row_pr = row._tr.get_or_add_trPr()
        row_pr.append(OxmlElement("w:cantSplit"))
        for index, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(widths[index]))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)


def repeat_header(row):
    row_pr = row._tr.get_or_add_trPr()
    marker = OxmlElement("w:tblHeader")
    marker.set(qn("w:val"), "true")
    row_pr.append(marker)


def add_page_number(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for item in (begin, instruction, separate, text, end):
        run._r.append(item)
    set_run(run, 9, color=GRAY)


def add_alt_text(inline_shape, title, description):
    inline_shape._inline.docPr.set("title", title)
    inline_shape._inline.docPr.set("descr", description)


def configure_document(doc):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.82)
    section.bottom_margin = Inches(0.76)
    section.left_margin = Inches(0.92)
    section.right_margin = Inches(0.92)
    section.header_distance = Inches(0.38)
    section.footer_distance = Inches(0.38)

    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    normal.font.size = Pt(10.7)
    normal.font.color.rgb = rgb(BLACK)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12
    normal.paragraph_format.widow_control = True

    title = doc.styles["Title"]
    title.font.name = "Aptos Display"
    title._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
    title._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
    title.font.size = Pt(30)
    title.font.bold = True
    title.font.color.rgb = rgb(BLACK)
    title.paragraph_format.space_after = Pt(8)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # Some Word templates add a decorative rule to the built-in Title style.
    # Keep the cover deliberately clean and text-led.
    title_ppr = title._element.get_or_add_pPr()
    title_border = title_ppr.find(qn("w:pBdr"))
    if title_border is not None:
        title_ppr.remove(title_border)

    subtitle = doc.styles["Subtitle"]
    subtitle.font.name = "Aptos"
    subtitle._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    subtitle._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    subtitle.font.size = Pt(15)
    subtitle.font.color.rgb = rgb(BLACK)
    subtitle.paragraph_format.space_after = Pt(14)

    for name, size, before, after in (
        ("Heading 1", 18, 16, 8),
        ("Heading 2", 14, 13, 6),
        ("Heading 3", 11.5, 9, 4),
    ):
        style = doc.styles[name]
        style.font.name = "Aptos Display"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = rgb(BLACK)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    bullet_style = doc.styles["List Bullet"]
    bullet_style.font.name = "Aptos"
    bullet_style.font.size = Pt(10.7)
    bullet_style.font.color.rgb = rgb(BLACK)
    bullet_style.paragraph_format.left_indent = Inches(0.38)
    bullet_style.paragraph_format.first_line_indent = Inches(-0.19)
    bullet_style.paragraph_format.space_after = Pt(3)
    bullet_style.paragraph_format.line_spacing = 1.1

    number_style = doc.styles["List Number"]
    number_style.font.name = "Aptos"
    number_style.font.size = Pt(10.7)
    number_style.paragraph_format.left_indent = Inches(0.38)
    number_style.paragraph_format.first_line_indent = Inches(-0.19)
    number_style.paragraph_format.space_after = Pt(3)
    number_style.paragraph_format.line_spacing = 1.1

    code = doc.styles.add_style("Blueprint Code", 1)
    code.font.name = "Cascadia Mono"
    code._element.rPr.rFonts.set(qn("w:ascii"), "Cascadia Mono")
    code._element.rPr.rFonts.set(qn("w:hAnsi"), "Cascadia Mono")
    code.font.size = Pt(8.7)
    code.font.color.rgb = rgb(NAVY)
    code.paragraph_format.left_indent = Inches(0.28)
    code.paragraph_format.right_indent = Inches(0.18)
    code.paragraph_format.space_before = Pt(3)
    code.paragraph_format.space_after = Pt(7)
    code.paragraph_format.line_spacing = 1.0

    caption = doc.styles["Caption"]
    caption.font.name = "Aptos"
    caption.font.size = Pt(9)
    caption.font.italic = True
    caption.font.color.rgb = rgb(GRAY)
    caption.paragraph_format.space_before = Pt(3)
    caption.paragraph_format.space_after = Pt(8)
    caption.paragraph_format.keep_with_next = False

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(header.add_run("ALIVE PROJECT BLUEPRINT"), 8.5, bold=True, color=GRAY)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(footer.add_run("ALIVE  |  "), 9, color=GRAY)
    add_page_number(footer)


def paragraph(doc, text="", bold_lead=None, style=None, after=None, align=None):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if bold_lead and text.startswith(bold_lead):
        r = p.add_run(bold_lead)
        set_run(r, 10.7, bold=True)
        r = p.add_run(text[len(bold_lead):])
        set_run(r, 10.7)
    else:
        r = p.add_run(text)
        set_run(r, 10.7)
    return p


def heading(doc, text, level=1, page_break=False):
    p = doc.add_paragraph(style=f"Heading {level}")
    if page_break:
        p.paragraph_format.page_break_before = True
    p.add_run(text)
    return p


def bullet(doc, text, lead=None):
    return paragraph(doc, text, bold_lead=lead, style="List Bullet")


def numbered(doc, text):
    return paragraph(doc, text, style="List Number")


def code_block(doc, text):
    p = doc.add_paragraph(style="Blueprint Code")
    p.add_run(text)
    return p


def add_table(doc, headers, rows, widths, header_fill=NAVY, center_columns=None, font_size=9.2):
    center_columns = set(center_columns or [])
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.style = "Table Grid"
    set_table_borders(table)
    for index, label in enumerate(headers):
        cell = table.rows[0].cells[index]
        set_cell_shading(cell, header_fill)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        if index in center_columns:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(label)
        set_run(r, font_size, bold=True, color=WHITE)
    repeat_header(table.rows[0])
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cell = cells[index]
            if row_index % 2:
                set_cell_shading(cell, LIGHT)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.03
            if index in center_columns:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(value))
            set_run(r, font_size)
    set_table_geometry(table, widths)
    paragraph(doc, "", after=2)
    return table


def add_figure(doc, path, width, title, description, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    shape = p.add_run().add_picture(str(path), width=Inches(width))
    add_alt_text(shape, title, description)
    cp = doc.add_paragraph(caption, style="Caption")
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return shape


def font(size, bold=False):
    path = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    return ImageFont.truetype(path, size)


def rounded_text(draw, bounds, text, fill, outline=None, text_color=WHITE, font_size=30, bold=True):
    if isinstance(fill, str) and len(fill) in (6, 8) and not fill.startswith("#"):
        fill = f"#{fill}"
    if isinstance(outline, str) and len(outline) in (6, 8) and not outline.startswith("#"):
        outline = f"#{outline}"
    if isinstance(text_color, str) and len(text_color) in (6, 8) and not text_color.startswith("#"):
        text_color = f"#{text_color}"
    draw.rounded_rectangle(bounds, radius=18, fill=fill, outline=outline, width=3 if outline else 1)
    x1, y1, x2, y2 = bounds
    lines = "\n".join(wrap(text, max(10, int((x2 - x1) / (font_size * 0.6)))))
    draw.multiline_text(((x1+x2)/2, (y1+y2)/2), lines, font=font(font_size, bold), fill=text_color, anchor="mm", align="center", spacing=5)


def arrow(draw, start, end, color="#9FB3C3", width=6):
    draw.line((*start, *end), fill=color, width=width)
    x2, y2 = end
    draw.polygon([(x2, y2), (x2-10, y2-16), (x2+10, y2-16)], fill=color)


def make_visuals():
    ASSETS.mkdir(parents=True, exist_ok=True)

    # Growth roadmap
    im = Image.new("RGB", (1800, 1000), "white")
    d = ImageDraw.Draw(im)
    d.text((70, 50), "ALIVE grows by completing one useful system at a time", font=font(42, True), fill="#17324D")
    stages = [
        ("Foundation", "World resources and tests", "#617487"),
        ("One learner", "Gather move experiment", "#2E75B6"),
        ("Four communities", "Trade trust and sharing", "#16869A"),
        ("Diffusion sandbox", "Scenarios replay and comparison", "#397D64"),
        ("Large technology ecology", "Deep graphs and institutions", "#B7791F"),
        ("Intelligent platform", "LLM tools planning and forecasting", "#7656A3"),
    ]
    for index, (name, detail, color) in enumerate(stages):
        x = 100 + index * 275
        y = 780 - index * 105
        rounded_text(d, (x, y, x+245, y+120), name, color, font_size=26)
        d.multiline_text((x+122, y+150), "\n".join(wrap(detail, 22)), font=font(21), fill="#333333", anchor="ma", align="center", spacing=4)
        if index < len(stages)-1:
            d.line((x+245, y+60, x+275, y-45), fill="#9FB3C3", width=7)
    roadmap = ASSETS / "growth_roadmap.png"
    im.save(roadmap)

    # Agent loop
    im = Image.new("RGB", (1800, 820), "white")
    d = ImageDraw.Draw(im)
    labels = [
        ("Observe", "local world resources groups memory", "#2E75B6"),
        ("Decide", "recurrent RL policy and action masks", "#7656A3"),
        ("Act", "gather move experiment trade share", "#16869A"),
        ("Resolve", "costs conflicts transfers and effects", "#B7791F"),
        ("Learn", "reward policy update and hidden memory", "#397D64"),
    ]
    for index, (name, detail, color) in enumerate(labels):
        x = 70 + index * 345
        rounded_text(d, (x, 190, x+275, 300), name, color, font_size=30)
        d.multiline_text((x+138, 345), "\n".join(wrap(detail, 24)), font=font(23), fill="#333333", anchor="ma", align="center", spacing=6)
        if index < len(labels)-1:
            d.line((x+275, 245, x+335, 245), fill="#9FB3C3", width=7)
            d.polygon([(x+335,245),(x+315,232),(x+315,258)], fill="#9FB3C3")
    d.arc((100, 80, 1670, 730), start=18, end=178, fill="#9FB3C3", width=5)
    d.polygon([(110,391),(95,365),(125,365)], fill="#9FB3C3")
    d.text((900, 70), "The repeated community decision loop", font=font(40, True), fill="#17324D", anchor="ma")
    loop = ASSETS / "agent_loop.png"
    im.save(loop)

    # Technology graph
    im = Image.new("RGB", (1800, 1020), "white")
    d = ImageDraw.Draw(im)
    rounded_text(d, (680, 45, 1120, 135), "Basic observation", "#17324D", font_size=29)
    branches = [
        (260, "Fire", "Cooking", "Heat", "#B7791F"),
        (690, "Basic tools", "Storage", "Woodworking", "#2E75B6"),
        (1110, "Counting", "Record keeping", "Planning", "#7656A3"),
        (1540, "Transport", "Wheel", "Cart", "#16869A"),
    ]
    for x, root, child1, child2, color in branches:
        d.line((900, 135, x, 260), fill="#9FB3C3", width=6)
        rounded_text(d, (x-145, 260, x+145, 350), root, color, font_size=27)
        d.line((x, 350, x, 490), fill=color, width=5)
        d.line((x, 540, x, 690), fill=color, width=5)
        rounded_text(d, (x-160, 490, x+160, 580), child1, "#EDF2F6", outline=color, text_color="#17324D", font_size=24, bold=False)
        rounded_text(d, (x-160, 690, x+160, 780), child2, "#EDF2F6", outline=color, text_color="#17324D", font_size=24, bold=False)
    d.text((80, 900), "The first graph is deliberately small. Costs and prerequisites create choices rather than one guaranteed path.", font=font(25), fill="#555555")
    tech = ASSETS / "initial_technology_graph.png"
    im.save(tech)

    # RL architecture and training
    im = Image.new("RGB", (1800, 960), "white")
    d = ImageDraw.Draw(im)
    d.text((900, 50), "Shared recurrent multi agent policy", font=font(40, True), fill="#17324D", anchor="ma")
    boxes = [
        (100, 170, 420, 280, "Local observation", "#2E75B6"),
        (530, 170, 850, 280, "Dense encoder", "#16869A"),
        (960, 170, 1280, 280, "GRU memory", "#7656A3"),
        (1390, 120, 1710, 220, "Action probabilities", "#B7791F"),
        (1390, 260, 1710, 360, "Value estimate", "#397D64"),
    ]
    for x1,y1,x2,y2,text,color in boxes:
        rounded_text(d,(x1,y1,x2,y2),text,color,font_size=27)
    for start,end in [((420,225),(520,225)),((850,225),(950,225)),((1280,225),(1380,170)),((1280,225),(1380,310))]:
        d.line((*start,*end),fill="#9FB3C3",width=7)
    d.text((100, 455), "Training cycle", font=font(31, True), fill="#17324D")
    cycle = ["Run many seeded worlds", "Collect trajectories", "Calculate rewards and advantages", "Update PPO policy", "Evaluate on unseen seeds"]
    for i, text in enumerate(cycle):
        x=90+i*340
        rounded_text(d,(x,530,x+290,640),text,"#EDF2F6",outline="#2E75B6",text_color="#17324D",font_size=22,bold=False)
        if i<len(cycle)-1:
            d.line((x+290,585,x+330,585),fill="#9FB3C3",width=6)
    d.text((900, 770), "One policy can serve every community while observations and hidden memories produce different behavior.", font=font(25), fill="#555555", anchor="ma")
    rl = ASSETS / "rl_architecture.png"
    im.save(rl)

    # Product architecture
    im = Image.new("RGB", (1800, 1100), "white")
    d = ImageDraw.Draw(im)
    rows = [
        (120, ["Scenario editor", "Live world", "Replay and analysis"], "#2E75B6"),
        (370, ["API and validation", "Experiment manager", "LLM assistance"], "#16869A"),
        (620, ["World engine", "Action resolver", "Event ledger"], "#397D64"),
        (870, ["RL training", "Policy checkpoints", "Metrics and storage"], "#7656A3"),
    ]
    for y, names, color in rows:
        for i,name in enumerate(names):
            x=100+i*560
            rounded_text(d,(x,y,x+470,y+125),name,color,font_size=28)
    for y in (245,495,745):
        for x in (335,895,1455):
            d.line((x,y,x,y+115),fill="#9FB3C3",width=6)
            d.polygon([(x,y+115),(x-10,y+95),(x+10,y+95)],fill="#9FB3C3")
    architecture = ASSETS / "product_architecture.png"
    im.save(architecture)

    # LLM boundary
    im = Image.new("RGB", (1800, 880), "white")
    d = ImageDraw.Draw(im)
    d.text((900, 45), "RL controls behavior while the LLM supports people", font=font(40, True), fill="#17324D", anchor="ma")
    rounded_text(d,(100,170,650,300),"Small language model","#7656A3",font_size=32)
    rounded_text(d,(1150,170,1700,300),"ALIVE simulation and RL","#17324D",font_size=32)
    items_left=["Scenario translation","Decision explanation","Run summaries","Graph suggestions"]
    items_right=["World state","Legal actions","Rewards","Actual consequences"]
    for i,item in enumerate(items_left):
        d.text((140,390+i*80),item,font=font(25),fill="#333333")
    for i,item in enumerate(items_right):
        d.text((1190,390+i*80),item,font=font(25),fill="#333333")
    d.line((660,235,1140,235),fill="#9FB3C3",width=7)
    d.polygon([(1140,235),(1115,220),(1115,250)],fill="#9FB3C3")
    d.text((900,190),"structured validated data",font=font(23),fill="#555555",anchor="ma")
    d.text((900,760),"The LLM never changes the world directly.",font=font(29,True),fill="#B7791F",anchor="ma")
    llm = ASSETS / "llm_boundary.png"
    im.save(llm)

    return roadmap, loop, tech, rl, architecture, llm


def add_cover(doc, roadmap):
    p = doc.add_paragraph("ALIVE", style="Title")
    p.paragraph_format.space_before = Pt(28)
    p = doc.add_paragraph("Adaptive Life in Virtual Environments", style="Subtitle")
    p = doc.add_paragraph("Project Design and Development Blueprint", style="Title")
    for run in p.runs:
        run.font.size = Pt(24)
    p = doc.add_paragraph("Community Technology Simulation and Artificial Intelligence Development Plan", style="Subtitle")
    paragraph(doc, "Version 1.0  |  September 2026", after=4)
    paragraph(doc, "Prepared for project planning advisor review implementation and long term development", after=14)
    add_figure(doc, roadmap, 6.35, "ALIVE growth roadmap", "Six ascending stages show ALIVE growing from simulation foundations through an intelligent platform.", "Figure 1. The project begins with a complete small system and expands only after each stage works.")
    paragraph(doc, "ALIVE is an extensible multi-agent reinforcement-learning platform in which virtual communities learn how to discover, adopt, use, trade, and share technologies while their environments and relationships change.", bold_lead="ALIVE is an extensible multi-agent reinforcement-learning platform ")


def add_front_matter(doc):
    heading(doc, "Executive summary", 1, page_break=True)
    paragraph(doc, "ALIVE represents each agent as an abstract community. A community has population, resources, technology knowledge, local observations, relationships, and recurrent memory. A shared reinforcement-learning policy selects legal actions such as gathering, moving, experimenting, trading, sharing, and conserving. The simulation engine applies costs and consequences, while a structured event ledger supports evaluation, replay, and explanation.")
    paragraph(doc, "The first deliverable is intentionally small: four communities, three resources, eight technologies, a 32 by 32 world, and stable and scarcity scenarios. The first success test is whether a trained community learns useful survival and technology strategies on unseen seeds and performs better than random and simple rule-based baselines.")
    paragraph(doc, "After the core works, ALIVE grows into a technology-diffusion sandbox with trust, trade, sharing, larger graphs, scenario editing, visualization, and controlled comparisons of individual and collective incentives. A small language model may translate user scenarios, explain recorded decisions, summarize histories, and assist developers with graph proposals. The language model does not control every simulation step or directly change world state.")
    paragraph(doc, "The project is development-led. Controlled experiments validate that the system behaves as intended and provide a defensible demonstration. The primary demonstration asks when sharing technology improves the long-term outcome of the sharing community and when it strengthens a competitor enough to become harmful.")

    heading(doc, "Project at a glance", 2)
    add_table(doc, ["Dimension", "Version 1", "Long term direction"], [
        ("Agents", "Four abstract communities", "Larger networks of communities and settlements"),
        ("Resources", "Food wood and stone", "Specialized materials energy medicine and labor"),
        ("Technology", "Eight validated nodes", "Deep graphs with alternative paths and institutions"),
        ("Intelligence", "Shared recurrent IPPO policy", "Planning negotiation and specialized policies"),
        ("Worlds", "Stable and scarcity scenarios", "Scenario library migration isolation and disruptions"),
        ("Interface", "Basic map metrics and replay", "Graph editor scenario builder and conversational analysis"),
        ("LLM", "Explanation summary and scenario assistance", "Structured high-level planning and negotiation"),
    ], [1700, 3350, 4310])

    heading(doc, "Document map", 2)
    add_table(doc, ["Part", "Focus"], [
        ("I", "Vision problem and development direction"),
        ("II", "The minimum viable system and first success test"),
        ("III", "Community agents world mechanics and technology diffusion"),
        ("IV", "Multi-agent reinforcement learning and evaluation"),
        ("V", "Language model integration software architecture and user experience"),
        ("VI", "Roadmap resources risks deliverables and future platform"),
        ("Appendices", "Initial schemas action definitions reward design and validation checklist"),
    ], [1100, 8260], center_columns=[0])


def add_part_one(doc):
    heading(doc, "Part I Project vision", 1)
    heading(doc, "1 Project identity", 2)
    paragraph(doc, "ALIVE stands for Adaptive Life in Virtual Environments. It is a software platform for building and observing virtual communities that learn technological strategies in changing worlds. The product combines a configurable simulation, multi-agent reinforcement learning, technology graphs, experiment tools, visualization, and an optional language interface.")
    paragraph(doc, "Repository description: An extensible multi-agent simulation where virtual communities learn to discover, adopt, and share technologies in changing environments.", bold_lead="Repository description: ")
    paragraph(doc, "Elevator pitch: ALIVE lets developers create virtual communities, technology graphs, and environmental scenarios, then watch reinforcement-learning agents discover different ways to survive, cooperate, compete, and spread knowledge.", bold_lead="Elevator pitch: ")

    heading(doc, "2 Problem and opportunity", 2)
    paragraph(doc, "Technology development is shaped by resource pressure, incomplete knowledge, relationships, and delayed consequences. A community may benefit from helping a partner survive, yet the same knowledge transfer can produce a stronger competitor. A useful technology can also become harmful when its maintenance cost rises or when the environment changes.")
    paragraph(doc, "Central question: How do environmental pressure, relationships, and technology-sharing decisions shape the development and survival of virtual communities?", bold_lead="Central question: ")
    paragraph(doc, "Core demonstration: Under what conditions does sharing a technology help the group that shares it, and when does it become harmful?", bold_lead="Core demonstration: ")

    heading(doc, "3 Development direction", 2)
    bullet(doc, "Build one complete and understandable loop before adding breadth.")
    bullet(doc, "Make resources technologies scenarios rewards and training settings configurable.")
    bullet(doc, "Use RL as the behavior engine and retain random and rule-based agents as evaluation baselines.")
    bullet(doc, "Treat graph editing visualization replay and experiment comparison as product capabilities.")
    bullet(doc, "Add technologies in validated batches rather than beginning with a large rigid graph.")
    bullet(doc, "Describe outputs as consequences of the implemented world and incentives.")

    heading(doc, "4 What the system can reveal", 2)
    paragraph(doc, "Emergence comes from repeated interactions, not from the number of graph nodes. One group may develop storage and survive scarcity. Another may specialize in transport and depend on trade. A shared technology may stabilize a network, spread beyond its creator, or erase the creator's advantage. ALIVE should expose these causal chains through event histories and controlled comparisons.")
    add_table(doc, ["Possible outcome", "Why it matters"], [
        ("Different communities follow different graph paths", "Shows specialization under distinct local conditions"),
        ("A technology survives after its creator collapses", "Shows knowledge diffusion beyond group continuity"),
        ("Sharing helps initially and harms later", "Shows delayed strategic consequences"),
        ("A costly technology is abandoned", "Shows that progress need not be monotonic"),
        ("Two modest technologies create a strong combination", "Shows interactions between graph branches"),
    ], [3900, 5460])

    heading(doc, "5 Scope of interpretation", 2)
    paragraph(doc, "Agents are abstract communities rather than models of specific cultures, countries, or historical populations. Initial forecasting estimates the next behavior of simulated agents. Claims about real societies would require historical data, calibration, external validation, and a separate ethical and methodological review.")


def add_part_two(doc, tech_graph):
    heading(doc, "Part II The minimum viable system", 1)
    heading(doc, "6 Version 1 world", 2)
    add_table(doc, ["Component", "Initial specification", "Reason"], [
        ("Map", "32 by 32 grid", "Large enough for local scarcity and movement while remaining easy to debug"),
        ("Communities", "Four", "Enough for cooperation competition and uneven technology spread"),
        ("Resources", "Food wood and stone", "Supports survival construction and technology trade-offs"),
        ("Technologies", "Eight", "Creates branching choices without hiding mechanisms"),
        ("Actions", "Gather move experiment adopt trade share conserve", "Covers the core development loop"),
        ("World treatments", "Stable abundance and scheduled scarcity", "Tests adaptation with minimal scenario complexity"),
        ("Policy", "Shared recurrent IPPO", "Allows learning memory and scalable multi-agent training"),
    ], [1800, 3200, 4360])

    heading(doc, "7 Initial technology graph", 2)
    paragraph(doc, "The first graph defines a limited set of capabilities and relationships. It should not imply one universal path of development. Nodes may later gain alternative prerequisites, and costs should make some branches unattractive under particular conditions.")
    add_figure(doc, tech_graph, 6.45, "Initial technology graph", "Basic observation branches into fire tools counting and transport families with eight early technology nodes.", "Figure 2. An illustrative starter graph. Final effects, costs, and prerequisites are locked only after the small environment passes validation.")
    add_table(doc, ["Technology", "Initial role", "Example cost or limitation"], [
        ("Fire", "Supports heat cooking and processing", "Consumes wood and requires maintenance"),
        ("Cooking", "Improves value or safety of food", "Requires fire and labor"),
        ("Basic tools", "Improves gathering and construction", "Consumes stone and production time"),
        ("Storage", "Reduces loss during scarcity", "Requires construction and upkeep"),
        ("Woodworking", "Supports transport and structures", "Consumes wood and skilled labor"),
        ("Record keeping", "Improves memory planning or trade reliability", "Consumes labor without immediate food gain"),
        ("Wheel", "Reduces transport cost", "Requires tools and woodworking"),
        ("Cart", "Raises carrying capacity", "Requires materials and maintenance"),
    ], [2000, 3800, 3560])

    heading(doc, "8 Version 1 actions", 2)
    add_table(doc, ["Action", "Agent chooses", "Engine resolves"], [
        ("Gather", "Resource type and reachable location", "Labor cost yield depletion and technology modifiers"),
        ("Move", "Destination or direction", "Travel cost occupancy and new observation"),
        ("Experiment", "Eligible technology", "Resource cost progress success and failure"),
        ("Adopt", "Observed technology and source", "Prerequisites time cost and proficiency gain"),
        ("Trade", "Partner offer and request", "Compatibility transfer and relationship effects"),
        ("Share", "Partner and technology", "Teaching cost adoption progress trust and diffusion"),
        ("Conserve", "Low activity mode", "Reduced consumption and reduced opportunity"),
    ], [1600, 3800, 3960])

    heading(doc, "9 First success test", 2)
    paragraph(doc, "The first important result is operational rather than spectacular: a trained community should learn to gather, experiment, and prepare for scarcity better than random and simple rule-based baselines on unseen seeds. If this does not happen, the team should debug observations, action effects, rewards, or training before adding trade, sharing, more communities, or more technologies.")
    heading(doc, "Version 1 acceptance criteria", 3)
    bullet(doc, "Resources and costs balance exactly in automated accounting tests.")
    bullet(doc, "Technologies produce their specified effects and respect prerequisites.")
    bullet(doc, "Illegal actions are masked before policy sampling.")
    bullet(doc, "Training improves evaluation performance on held-out seeds.")
    bullet(doc, "Every technology discovery and transfer is traceable.")
    bullet(doc, "The same seed and configuration reproduce the same evaluation history.")
    bullet(doc, "Changing agent array order does not create a consistent advantage.")


def add_part_three(doc, agent_loop):
    heading(doc, "Part III Community agents and world mechanics", 1)
    heading(doc, "10 What an agent represents", 2)
    paragraph(doc, "Each agent represents an abstract community. Population is stored as an aggregate quantity rather than a collection of individual people. The community has a position, resource inventory, known technologies, relationships, current needs, and recurrent policy memory. Communities can grow, decline, move, share knowledge, and eventually establish new settlements.")

    heading(doc, "11 Agent state", 2)
    add_table(doc, ["State group", "Example fields", "Purpose"], [
        ("Identity", "ID name position active flag", "Tracks the community and its location"),
        ("Population", "Size available labor stability", "Constrains production growth and survival"),
        ("Resources", "Food wood stone storage capacity", "Supports action costs and shortages"),
        ("Technology", "Known mask progress proficiency availability", "Defines capabilities and graph position"),
        ("Relationships", "Trust hostility familiarity obligations", "Shapes trade sharing and conflict"),
        ("History", "Recent outcomes transfers shortages", "Supports recurrent decisions and explanation"),
        ("Policy memory", "GRU hidden vector", "Carries learned context within an episode"),
    ], [1700, 3500, 4160])

    heading(doc, "12 Observation and partial knowledge", 2)
    paragraph(doc, "The true world state and the agent's observation are separate. A community sees its own condition, nearby resources, encountered groups, visible actions, known relationships, and received information. It does not receive global resource maps, hidden technologies, other policies, or future environmental events.")
    add_table(doc, ["Observed", "Hidden unless revealed"], [
        ("Own population resources technology and memory", "Other communities' complete inventories and policies"),
        ("Nearby resources within sensing range", "Distant cells and future resource changes"),
        ("Known trust and interaction history", "A neighbor's internal reward or intent"),
        ("Technologies shared or visibly demonstrated", "Unknown graph nodes and private discoveries"),
    ], [4680, 4680])
    paragraph(doc, "Technologies can alter observation. Navigation may increase exploration range, record keeping may improve the usable history window, and communication may increase the fidelity of transferred knowledge.")

    heading(doc, "13 Community decision cycle", 2)
    add_figure(doc, agent_loop, 6.45, "Community decision loop", "Five connected stages show observe decide act resolve and learn with a loop returning to observation.", "Figure 3. The policy selects an action, while the simulation engine determines whether it is legal and what consequences occur.")
    numbered(doc, "Apply scheduled environmental changes and resource regeneration.")
    numbered(doc, "Build a limited observation and legal-action mask for every active community.")
    numbered(doc, "Sample intended actions from the shared recurrent policy.")
    numbered(doc, "Resolve simultaneous actions, costs, conflicts, transfers, and technology effects.")
    numbered(doc, "Calculate rewards and update within-episode policy memory.")
    numbered(doc, "Process population growth, decline, settlement formation, and collapse.")
    numbered(doc, "Record metrics, explanations, and replay events.")

    heading(doc, "14 Relationships and knowledge sharing", 2)
    paragraph(doc, "Relationships are directed. Community A may trust Community B even when B does not trust A. Trust changes through fulfilled trades, helpful sharing, harmful competition, broken agreements, and repeated contact. The policy observes known relationship values and learns whether they predict useful outcomes.")
    paragraph(doc, "Sharing is a structured action. The sender chooses a recipient and known technology. The engine checks reachability, teaching costs, prerequisites, and transfer difficulty. The recipient receives adoption progress rather than instant mastery. The event ledger records the origin and subsequent transfer path.")
    code_block(doc, "Technology path\nRiver Group -> Hill Group -> Lake Group\nMethod          teaching        imitation\nTechnology      storage")

    heading(doc, "15 Growth splitting and technology loss", 2)
    paragraph(doc, "Sustained resource surplus can grow population, while shortages cause decline and possible collapse. A sufficiently stable community may later establish a settlement. Population and resources are divided, and the new group receives a configurable subset of technology knowledge. This creates cultural inheritance without modeling biological reproduction.")
    bullet(doc, "Knowledge can become inactive when required resources or prerequisites disappear.")
    bullet(doc, "Proficiency can decay when a technology is unused for a long period.")
    bullet(doc, "Population collapse can remove specialized knowledge from a region.")
    bullet(doc, "Partial knowledge can make rediscovery easier than the original discovery.")

    heading(doc, "16 Fair action resolution", 2)
    paragraph(doc, "All communities choose intended actions before shared outcomes are resolved. Resource conflicts use an explicit seeded rule based on valid factors such as labor, relevant technology, or contest investment. Array position must never decide a winner. External scenario randomness, policy sampling, discovery, and conflict resolution use separate random streams so one changed event does not shift every later environmental event.")


def add_part_four(doc, rl_architecture):
    heading(doc, "Part IV Multi agent reinforcement learning", 1)
    heading(doc, "17 Why reinforcement learning", 2)
    paragraph(doc, "ALIVE is an RL-centered project. Developers define the state, possible actions, physical and economic consequences, and general success signal. The policy learns which legal action tends to work in a given context. Random and rule-based policies remain necessary baselines, but they are not the intended final behavior engine.")
    add_table(doc, ["Approach", "Who defines the strategy", "Role in ALIVE"], [
        ("Random", "No strategy", "Sanity baseline and exploration check"),
        ("Rule based", "Developers write decision logic", "Functional baseline and simulator debugging"),
        ("Reinforcement learning", "Policy learns from reward over repeated episodes", "Primary community decision system"),
    ], [1900, 3700, 3760])

    heading(doc, "18 RL formulation", 2)
    heading(doc, "Observation space", 3)
    paragraph(doc, "The observation is a fixed-size normalized vector containing self state, local resource features, technology masks and progress, nearby-group summaries, directed relationship features, recent outcomes, and environmental signals. Missing neighbors and technologies use masks rather than changing array size.")
    heading(doc, "Action space and masking", 3)
    paragraph(doc, "The first policy uses a discrete flattened action space for gathering, movement, experimentation, adoption, trade, sharing, and conservation. Parameterized actions are expanded into valid combinations. A Boolean mask removes actions that fail prerequisites, resource costs, reachability, or target requirements before sampling.")
    heading(doc, "Episode", 3)
    paragraph(doc, "An episode begins from a saved scenario and seed, runs for a fixed horizon or until every community collapses, and produces a trajectory of observations, actions, rewards, values, masks, and structured events. Training episodes vary resource placement and starting relationships within registered ranges. Evaluation uses unseen seeds and fixed scenarios.")

    heading(doc, "19 Reward design", 2)
    paragraph(doc, "Rewards should describe broad community outcomes rather than prescribe a favored technology or social action. Directly rewarding every act of sharing would predetermine the behavior the project wants to study.")
    code_block(doc, "reward =\n    population stability\n  + sustainable resource balance\n  + controlled growth\n  - shortage severity\n  - population loss\n  - action and maintenance costs\n  - collapse penalty")
    paragraph(doc, "Long-delay actions such as experimentation, movement, and sharing require a sufficiently long discount horizon and recurrent memory. Reward components must be normalized, logged separately, and tested for loopholes such as hoarding, avoiding all experimentation, farming trust, or exploiting population caps.")

    heading(doc, "20 Individual and collective incentives", 2)
    add_table(doc, ["Reward mode", "Objective", "Likely pressure"], [
        ("Individual", "Each group values its own outcome", "Selective cooperation withholding and competition"),
        ("Partially shared", "Own outcome plus a fraction of network outcome", "Conditional cooperation and partner preservation"),
        ("Collective", "All groups receive the same world outcome", "Broad cooperation and technology diffusion"),
    ], [1900, 3600, 3860])
    paragraph(doc, "Comparing these modes creates a direct experiment about incentives. It does not require assigning moral labels to the policies. The measured question is how reward structure changes sharing, survival, diffusion, and inequality inside the simulation.")

    heading(doc, "21 Policy architecture", 2)
    add_figure(doc, rl_architecture, 6.45, "Recurrent reinforcement learning architecture", "A local observation passes through a dense encoder and GRU to action probabilities and a value estimate. A PPO training cycle appears below.", "Figure 4. A shared recurrent policy lets communities use the same learned capability while maintaining different observations and histories.")
    paragraph(doc, "A practical first network uses a 128-unit encoder, a 128-unit GRU, an action head, and a value head. One set of weights is shared across communities. Community identity should not be required unless experiments specifically test stable roles. Distinct observations and hidden states are sufficient to produce different behavior.")

    heading(doc, "22 Training algorithm and curriculum", 2)
    paragraph(doc, "Recurrent Independent PPO is the recommended starting algorithm because it supports discrete masked actions, shared policies, and decentralized decisions. MAPPO becomes a later comparison if centralized training information materially improves cooperation. Algorithm complexity should follow a demonstrated limitation rather than lead development.")
    add_table(doc, ["Curriculum stage", "Capabilities introduced", "Gate"], [
        ("1", "Gather and conserve in a stable world", "Learns sustainable resource use"),
        ("2", "Move and adapt to scarcity", "Recovers on unseen layouts"),
        ("3", "Experiment and use technologies", "Chooses useful investments"),
        ("4", "Four communities and shared resources", "Training remains stable"),
        ("5", "Trade trust and sharing", "Transfers produce interpretable consequences"),
        ("6", "Multiple incentives and larger graphs", "Core evaluation remains valid"),
    ], [1800, 4600, 2960], center_columns=[0])

    heading(doc, "23 Evaluation", 2)
    bullet(doc, "Compare trained RL with random, rule-based, and untrained neural policies.")
    bullet(doc, "Evaluate only on seeds and layouts excluded from training.")
    bullet(doc, "Report mean outcomes, uncertainty, extinction frequency, and failure cases.")
    bullet(doc, "Test recurrent and memoryless versions to establish whether history is useful.")
    bullet(doc, "Inspect policy behavior under stable, scarcity, and distribution-shift scenarios.")
    bullet(doc, "Retain videos or replay files for representative and failed episodes selected by a fixed rule.")


def add_part_five(doc, llm_boundary, architecture):
    heading(doc, "Part V Language model product and software layers", 1)
    heading(doc, "24 Role of a small language model", 2)
    paragraph(doc, "A small LLM can improve how people create and understand simulations. It is not needed for resource accounting, technology effects, routine action selection, or PPO training. Keeping this boundary preserves speed and reproducibility while still giving ALIVE a natural-language interface.")
    add_figure(doc, llm_boundary, 6.4, "Language model boundary", "A small language model exchanges structured validated data with the ALIVE simulation and reinforcement learning system.", "Figure 5. RL controls community behavior. The LLM supports users and developers through validated structured interfaces.")

    heading(doc, "25 Initial LLM use cases", 2)
    add_table(doc, ["Use case", "Input", "Output and validation"], [
        ("Decision explanation", "Recorded observation action mask scores and outcome", "Readable explanation tied to stored evidence"),
        ("Run summary", "Selected events and metrics", "Narrative history with event identifiers"),
        ("Scenario creation", "Natural language user request", "YAML or JSON checked against a scenario schema"),
        ("Graph assistance", "Existing graph and requested capability", "Proposed node for developer review and balancing"),
        ("Simulation questions", "User question plus retrieved events", "Answer grounded in stored run data"),
    ], [1900, 3500, 3960])

    heading(doc, "26 Advanced LLM use cases", 2)
    paragraph(doc, "A later hierarchical design may ask the LLM to choose a high-level objective every 25 to 100 turns, such as preparing for scarcity or preserving a trading partner. The RL policy still chooses each legal action. Structured negotiation may also let the LLM draft offers that the engine converts into validated contracts and that RL policies accept or reject.")
    bullet(doc, "Every LLM response must match a versioned schema.")
    bullet(doc, "The engine rejects unknown technologies, actions, targets, and quantities.")
    bullet(doc, "Explanations must cite stored factors rather than invent internal motives.")
    bullet(doc, "LLM output never changes simulation state without deterministic validation.")
    bullet(doc, "The system remains fully usable when the LLM is disabled.")

    heading(doc, "27 Local model strategy", 2)
    paragraph(doc, "The RTX 3060 Ti can support quantized inference with a small model, but its typical 8 GB VRAM should be reserved primarily for RL training. The normal workflow is to train and save the RL policy, release training memory, then load the LLM for summaries or scenario work. Interactive demonstrations may run a trained small policy and a 1B to 3B quantized language model together after profiling.")

    heading(doc, "28 Software architecture", 2)
    add_figure(doc, architecture, 6.4, "ALIVE software architecture", "Four layers show the user application, services, simulation engine, and reinforcement learning and storage components.", "Figure 6. Product features sit above validated services, the deterministic simulation engine, and the RL training and storage layer.")
    add_table(doc, ["Layer", "Responsibilities", "Candidate tools"], [
        ("Simulation", "World resources agents graph observations resolution rewards", "Python and JAX"),
        ("RL", "Policies recurrent state PPO training evaluation", "Flax Optax and JaxMARL"),
        ("Services", "Scenario validation experiment control retrieval and inference", "FastAPI and Pydantic"),
        ("Interface", "Map graph editor timeline metrics and replay", "React with Canvas PixiJS or Phaser"),
        ("Analysis", "Aggregation statistics plots and exports", "Polars or Pandas SciPy and Plotly"),
        ("Storage", "Configs checkpoints events metrics and replay files", "YAML Parquet and compressed arrays"),
    ], [1700, 4600, 3060])

    heading(doc, "29 Configuration and reproducibility", 2)
    paragraph(doc, "Every run stores the code revision, graph version, scenario, reward definition, policy checkpoint, hyperparameters, hardware information, and random seeds. Technology definitions and environments live in versioned configuration files. Training summaries are stored frequently, while full agent histories are limited to evaluation episodes and selected checkpoints.")

    heading(doc, "30 User experience", 2)
    bullet(doc, "Live map showing communities resources movement and environmental changes.")
    bullet(doc, "Community inspector showing resources technology relationships and recent decisions.")
    bullet(doc, "Technology graph showing known available and spreading technologies.")
    bullet(doc, "Relationship network showing trade sharing trust and competition.")
    bullet(doc, "Timeline and replay controls for discoveries transfers shortages splits and collapse.")
    bullet(doc, "Experiment comparison for policies reward modes graphs scenarios and seeds.")
    bullet(doc, "Natural-language scenario entry and questions over completed runs.")


def add_part_six(doc, roadmap):
    heading(doc, "Part VI Evaluation growth and delivery", 1)
    heading(doc, "31 Primary technology sharing demonstration", 2)
    paragraph(doc, "The primary product demonstration compares environments where sharing is unavailable or available under individual, partially shared, and collective rewards. It varies scarcity, sharing cost, recipient strength, and whether recipients can share again. The goal is to show that ALIVE can represent and measure delayed strategic consequences.")
    add_table(doc, ["Factor", "Example levels", "Measured implication"], [
        ("Sharing access", "Unavailable or available", "Whether diffusion changes outcomes"),
        ("Reward", "Individual partial collective", "How incentives change cooperation"),
        ("Environment", "Stable or scarcity", "Whether pressure changes technology value"),
        ("Technology", "Storage transport record keeping", "Whether effects depend on function"),
        ("Recipient", "Weak peer or strong", "Whether relative power changes sender outcome"),
        ("Resharing", "Disabled or enabled", "Whether loss of control matters"),
    ], [1800, 3100, 4460])
    paragraph(doc, "Primary measurements include community survival, population stability, sustainable resources, sender outcome after sharing, recipient advantage, diffusion speed, technology diversity, and relationship persistence. Evaluation uses paired seeds and reports distributions rather than one interesting replay.")

    heading(doc, "32 Forecasting", 2)
    paragraph(doc, "A later predictor can estimate the next action, discovery, transfer, shortage, relationship change, or collapse risk from structured simulation histories. Begin with logistic regression or tree-based baselines, then compare a small sequence model. An LLM may explain predictions, but accuracy is measured on held-out simulated runs. Real-world prediction remains a separate project.")

    heading(doc, "33 Start small and build big roadmap", 2)
    add_figure(doc, roadmap, 6.35, "ALIVE staged growth roadmap", "Six ascending stages progress from foundations to an intelligent platform.", "Figure 7. Each horizon has a working demonstration and a gate before the next expansion.")
    add_table(doc, ["Horizon", "Deliverable", "Completion gate"], [
        ("0 Foundation", "World resources graph loader tests random agents", "Accounting and reproducibility pass"),
        ("1 One learner", "Single recurrent RL community", "Beats baselines on unseen seeds"),
        ("2 Four communities", "Shared policy trade trust and sharing", "Stable training and traceable interactions"),
        ("3 Diffusion sandbox", "Scenarios replay comparisons and core experiment", "Delayed sharing effects are measurable"),
        ("4 Expanded ALIVE", "20 to 30 technologies larger maps and settlement formation", "New batches retain validation and performance"),
        ("5 Large ecology", "40 to 60 or more technologies and deeper institutions", "Separate registered evaluation is feasible"),
        ("6 Intelligent platform", "LLM tools planning negotiation and forecasting", "Structured outputs remain grounded and validated"),
    ], [1900, 3800, 3660])

    heading(doc, "34 Two semester plan", 2)
    add_table(doc, ["Period", "Work", "Required milestone"], [
        ("Semester 1 weeks 1 to 3", "Specification and reference implementation", "Actions observations resources technologies and accounting defined"),
        ("Weeks 4 to 7", "One community environment", "Random and rule-based baselines work"),
        ("Weeks 8 to 11", "Recurrent PPO training", "One learner passes unseen-seed evaluation"),
        ("Weeks 12 to 16", "Four communities and sharing", "Multi-agent pilot and throughput report"),
        ("Semester 2 weeks 1 to 4", "Trust trade incentives and evaluation", "Primary design and seed plan locked"),
        ("Weeks 5 to 8", "Main experiment and replay", "Paired runs complete with event histories"),
        ("Weeks 9 to 11", "Interface and initial LLM tools", "Scenario and explanation workflows validated"),
        ("Weeks 12 to 16", "Analysis documentation and conditional expansion", "Reproducible release and final demonstration"),
    ], [2100, 3000, 4260])

    heading(doc, "35 Team and hardware", 2)
    add_table(doc, ["Responsibility", "Primary work"], [
        ("Simulation engineering", "World resources graph actions accounting and tests"),
        ("RL engineering", "Policy observations masks rewards training and evaluation"),
        ("Application engineering", "API visualization graph interface replay and LLM workflows"),
        ("Experiment lead", "Baselines seeds metrics comparisons documentation and reporting"),
    ], [2600, 6760])
    paragraph(doc, "A three-person team can combine roles. The current RTX 3060 Ti and 32 GB RAM are sufficient for Version 1 if the policy and batch sizes remain modest. Start with 32 parallel environments, a rollout length of 128, and a 128-unit recurrent policy, then increase only after profiling. Use CPU for unit tests and small scenarios.")
    paragraph(doc, "The provisional project allowance is 120 to 460 GPU-hours for development, debugging, main training, and evaluation. This is not a commitment. By the end of the first multi-agent pilot, report warmed environment steps per second, update time, VRAM use, wall time per run, compile time, checkpoint size, and storage growth. These measurements determine the final run count and whether university hardware is needed.")

    heading(doc, "36 Major risks and responses", 2)
    add_table(doc, ["Risk", "Response"], [
        ("Reward produces trivial or exploitative behavior", "Log components separately test adversarial cases and revise before main runs"),
        ("Action space becomes too large", "Use masks curriculum and hierarchical action heads only after the flat space works"),
        ("RL fails to beat rules", "Inspect observability horizon reward and training stability before adding features"),
        ("Graph predetermines outcomes", "Use explicit trade-offs alternative paths and matched graph comparisons"),
        ("Training exceeds the 3060 Ti", "Reduce parallelism graph size and optional sweeps then use shared research hardware"),
        ("LLM invents explanations", "Ground prompts in event records require schemas and display evidence links"),
        ("Interface consumes the schedule", "Ship replay and static inspection before a full real-time editor"),
        ("Scope expands too early", "Enforce horizon gates and cut optional features before core evaluation"),
    ], [3400, 5960])

    heading(doc, "37 Deliverables and success levels", 2)
    add_table(doc, ["Level", "Definition"], [
        ("Minimum success", "One recurrent RL community learns useful resource and technology behavior; four-community simulation and reproducible evaluation work"),
        ("Strong success", "Trade sharing trust incentives replay and the primary technology-sharing experiment are complete"),
        ("Stretch success", "Expanded graph polished scenario editor small LLM workflows planning or forecasting are demonstrated"),
    ], [2000, 7360])
    paragraph(doc, "Core deliverables are the simulation engine, recurrent IPPO training system, Version 1 technology graph, scenario files, baselines, evaluation report, experiment seeds, event ledger, replay visualization, technical documentation, and large-graph extension interface. Scientific and engineering success does not depend on sharing being good, RL producing a particular social pattern, or the largest graph being completed.")

    heading(doc, "38 Long term platform", 2)
    bullet(doc, "Educational simulation game for exploring technology and incentives.")
    bullet(doc, "Development sandbox for artificial communities and technology diffusion.")
    bullet(doc, "Benchmark for multi-agent reinforcement learning with graph-constrained capabilities.")
    bullet(doc, "Scenario and technology-graph ecosystem for future students and contributors.")
    bullet(doc, "Conversational interface for creating and understanding complex simulation histories.")
    bullet(doc, "Future historical calibration project after appropriate data and validation are available.")


def add_appendices(doc):
    heading(doc, "Appendices", 1, page_break=True)
    heading(doc, "Appendix A Example agent state", 2)
    code_block(doc, "id: river_group\nposition: [12, 8]\npopulation: 42\nresources: {food: 30, wood: 70, stone: 12}\ntechnology_known: {fire: true, storage: false, wheel: false}\ntechnology_progress: {storage: 0.25}\nrelationships:\n  hill_group: {trust: 0.80, hostility: 0.05}\npolicy_memory: float32[128]\nactive: true")

    heading(doc, "Appendix B Observation specification", 2)
    add_table(doc, ["Block", "Example fields", "Normalization or mask"], [
        ("Self", "Population labor food wood stone capacity", "Divide by configured caps"),
        ("Local world", "Resource totals distance occupancy scarcity", "Fixed neighborhood summary"),
        ("Technology", "Known active progress maintenance", "Fixed node order plus versioned mask"),
        ("Neighbors", "Distance population estimate trust hostility", "Top K slots plus presence mask"),
        ("History", "Previous action reward shortage and transfer", "Window summary or recurrent state"),
        ("Environment", "Season signal elapsed time observed shock", "Only information available to the group"),
    ], [1700, 4700, 2960])

    heading(doc, "Appendix C Action specification", 2)
    add_table(doc, ["Family", "Parameters", "Validation"], [
        ("Gather", "Resource and target cell", "Reachable visible labor and capacity"),
        ("Move", "Direction or target cell", "Reachable unblocked and affordable"),
        ("Experiment", "Technology node", "Prerequisites progress resources and labor"),
        ("Adopt", "Technology and source", "Observed transferable and compatible"),
        ("Trade", "Partner offer request quantities", "Reachable inventories and accepted terms"),
        ("Share", "Partner and technology", "Known teachable reachable and affordable"),
        ("Conserve", "Intensity", "Always available within configured bounds"),
    ], [1700, 3900, 3760])

    heading(doc, "Appendix D Example technology definition", 2)
    code_block(doc, "wheel:\n  category: transport\n  prerequisites: [basic_tools, woodworking]\n  discovery_cost: {wood: 20, labor: 10}\n  maintenance_cost: {wood: 1}\n  effects:\n    transport_capacity_multiplier: 2.0\n    movement_cost_multiplier: 0.75\n  unlocks: [cart]\n  sharing_difficulty: 0.35")

    heading(doc, "Appendix E Reward audit", 2)
    add_table(doc, ["Check", "Failure example", "Required evidence"], [
        ("Scale", "One component dominates all others", "Component distributions and clipped ranges"),
        ("Delay", "Experimentation is always punished before payoff", "Return traces across investment horizons"),
        ("Hoarding", "Policy stores resources indefinitely", "Consumption growth and opportunity comparisons"),
        ("Sharing", "Policy shares only for a direct bonus", "Outcome-based reward without action bonus"),
        ("Population cap", "Policy farms reward at capacity", "Saturation logs and capped-growth treatment"),
        ("Inactivity", "Conserve becomes permanently optimal", "Minimum needs and opportunity-cost tests"),
    ], [1900, 3600, 3860])

    heading(doc, "Appendix F Validation checklist", 2)
    for item in [
        "Resource conservation and event accounting pass automated tests.",
        "Every technology effect has a direct unit or scenario test.",
        "Prerequisite additions removals and unavailable actions are correct.",
        "Action masks match the resolver's legality checks.",
        "Same-seed evaluation is reproducible.",
        "Agent order permutation does not introduce consistent advantage.",
        "Technology origin and transfer chains are complete.",
        "RL evaluation uses held-out seeds and frozen checkpoints.",
        "Reward component logs reveal no dominant loophole.",
        "LLM explanations contain only retrieved events and decision evidence.",
        "Large-graph additions pass the same tests before new experiments.",
    ]:
        bullet(doc, item)

    heading(doc, "Appendix G Terms", 2)
    add_table(doc, ["Term", "Meaning in ALIVE"], [
        ("Agent", "An abstract community controlled by a policy"),
        ("Policy", "A function or network that maps observation and memory to action probabilities"),
        ("Observation", "The limited numerical information available to one community"),
        ("Action mask", "A Boolean vector that removes illegal actions"),
        ("Reward", "A numerical training signal derived from community outcomes"),
        ("Episode", "One complete seeded simulation trajectory"),
        ("Technology graph", "Versioned capability nodes connected by prerequisites and other relationships"),
        ("Diffusion", "Movement of technology knowledge between communities"),
        ("IPPO", "Independent Proximal Policy Optimization applied to multi-agent experience"),
        ("MAPPO", "PPO with centralized information during training and local information during execution"),
        ("LLM", "A language model used for text interaction and optional high-level assistance"),
    ], [1900, 7460])

    heading(doc, "Appendix H Decisions to lock before implementation", 2)
    bullet(doc, "Final Version 1 technology nodes prerequisites effects and costs.")
    bullet(doc, "Exact population resource consumption growth and collapse equations.")
    bullet(doc, "Observation ranges neighbor representation and action encoding.")
    bullet(doc, "Reward components discount factor and recurrent state behavior.")
    bullet(doc, "Training framework and policy checkpoint format.")
    bullet(doc, "Trust update and trade acceptance mechanisms.")
    bullet(doc, "Episode horizon environment schedule and evaluation seeds.")
    bullet(doc, "Minimum replay interface and storage budget.")
    bullet(doc, "Small LLM runtime schema and evidence requirements.")

    heading(doc, "Selected technical references", 2)
    paragraph(doc, "Schulman J et al. Proximal Policy Optimization Algorithms. 2017. https://arxiv.org/abs/1707.06347")
    paragraph(doc, "de Witt C S et al. Is Independent Learning All You Need in the StarCraft Multi Agent Challenge. 2020. https://arxiv.org/abs/2011.09533")
    paragraph(doc, "Yu C et al. The Surprising Effectiveness of PPO in Cooperative Multi Agent Games. 2022. https://arxiv.org/abs/2103.01955")
    paragraph(doc, "Rutherford A et al. JaxMARL Multi Agent RL Environments and Algorithms in JAX. 2023. https://arxiv.org/abs/2311.10090")
    paragraph(doc, "Sutton R S and Barto A G. Reinforcement Learning An Introduction second edition. 2018. http://incompleteideas.net/book/the-book-2nd.html")


def build():
    roadmap, agent_loop, tech_graph, rl_architecture, architecture, llm_boundary = make_visuals()
    doc = Document()
    configure_document(doc)
    add_cover(doc, roadmap)
    add_front_matter(doc)
    add_part_one(doc)
    add_part_two(doc, tech_graph)
    add_part_three(doc, agent_loop)
    add_part_four(doc, rl_architecture)
    add_part_five(doc, llm_boundary, architecture)
    add_part_six(doc, roadmap)
    add_appendices(doc)
    doc.core_properties.title = "ALIVE Project Design and Development Blueprint"
    doc.core_properties.subject = "Multi agent reinforcement learning technology diffusion platform"
    doc.core_properties.author = "ALIVE Project Team"
    doc.core_properties.keywords = "ALIVE reinforcement learning multi agent technology diffusion simulation"
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
