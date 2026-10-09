from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def _value(parent, name, value):
    el = SubElement(parent, name)
    el.text = "" if value is None else str(value)
    return el

def build_xml(data_inicio, data_fim, resumo, financeiro, glosas, produtos):
    root = Element("relatorio_oncologia")

    periodo = SubElement(root, "periodo")
    _value(periodo, "inicio", data_inicio)
    _value(periodo, "fim", data_fim)

    convenio = SubElement(root, "convenio")
    _value(convenio, "codigo", 11)
    _value(convenio, "nome", "CONVENIO_DEMO")

    r = SubElement(root, "resumo")
    for k, v in (resumo or {}).items():
        _value(r, k, v)

    f = SubElement(root, "financeiro")
    for k, v in (financeiro or {}).items():
        _value(f, k, v)

    gs = SubElement(root, "glosas")
    for row in glosas:
        g = SubElement(gs, "glosa")
        for k, v in row.items():
            _value(g, k, v)

    ps = SubElement(root, "produtos")
    for row in produtos:
        p = SubElement(ps, "produto")
        for k, v in row.items():
            _value(p, k, v)

    rough = tostring(root, encoding="utf-8")
    return minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8")
