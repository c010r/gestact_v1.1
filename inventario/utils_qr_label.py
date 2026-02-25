"""
utils_qr_label.py
Genera un PDF de etiqueta con código QR para identificación visual de activos.
"""
import datetime
from io import BytesIO

import qrcode
import qrcode.constants
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# ── Paleta de colores (consistente con el resto del sistema) ──────────────────
COLOR_PRIMARIO = colors.HexColor('#0f172a')       # Azul oscuro
COLOR_SECUNDARIO = colors.HexColor('#1d4ed8')     # Azul
COLOR_ACENTO = colors.HexColor('#e0f2fe')         # Celeste muy claro
COLOR_FONDO = colors.HexColor('#f8fafc')          # Blanco roto
COLOR_BORDE = colors.HexColor('#cbd5e1')          # Gris claro
COLOR_TEXTO_CLARO = colors.HexColor('#64748b')    # Gris medio
COLOR_BLANCO = colors.white

# ── Etiquetas para tipos de activo ────────────────────────────────────────────
TIPO_LABELS = {
    'computadora': 'Computadora',
    'monitor': 'Monitor',
    'impresora': 'Impresora',
    'networking': 'Networking',
    'telefonia': 'Telefonía',
    'periferico': 'Periférico',
    'tecnologia_medica': 'Tecnología Médica',
    'software': 'Software',
    'insumo': 'Insumo',
    'mobiliario': 'Mobiliario',
    'vehiculo': 'Vehículo',
    'herramienta': 'Herramienta',
}


def _generate_qr_png(content: str) -> BytesIO:
    """Genera un código QR en formato PNG y lo retorna como BytesIO."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def _get_identificador(activo, tipo_activo: str) -> str:
    """Retorna el identificador principal del activo según su tipo."""
    if tipo_activo == 'software':
        return getattr(activo, 'numero_licencia', None) or '-'
    return getattr(activo, 'numero_serie', None) or '-'


def build_qr_label_pdf(activo, tipo_activo: str, url: str) -> bytes:
    """
    Genera un PDF de etiqueta con código QR para identificación visual del activo.

    Args:
        activo: Instancia del modelo de activo.
        tipo_activo: Clave del tipo (ej. 'computadora').
        url: URL absoluta al detalle del activo (contenido del QR).

    Returns:
        bytes del PDF generado.
    """
    buf = BytesIO()

    # Dimensiones: A4 con margen mínimo para maximizar la etiqueta
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Etiqueta - {getattr(activo, 'nombre', str(activo))}",
    )

    # ── Datos del activo ──────────────────────────────────────────────────────
    tipo_label = TIPO_LABELS.get(tipo_activo, tipo_activo.capitalize())
    nombre = getattr(activo, 'nombre', str(activo)) or '-'
    identificador = _get_identificador(activo, tipo_activo)
    numero_inventario = getattr(activo, 'numero_inventario', None) or '-'
    lugar = getattr(activo, 'lugar', None)
    lugar_nombre = getattr(lugar, 'nombre_completo', None) or getattr(lugar, 'nombre', None) or '-'
    estado = getattr(activo, 'estado', None)
    estado_nombre = getattr(estado, 'nombre', None) or '-'
    fecha_gen = datetime.date.today().strftime('%d/%m/%Y')

    # ── Estilos de texto ──────────────────────────────────────────────────────
    st_titulo = ParagraphStyle(
        'titulo',
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=COLOR_BLANCO,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    st_subtitulo = ParagraphStyle(
        'subtitulo',
        fontName='Helvetica',
        fontSize=11,
        textColor=COLOR_ACENTO,
        alignment=TA_RIGHT,
        spaceAfter=0,
    )
    st_label = ParagraphStyle(
        'label',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=COLOR_TEXTO_CLARO,
        alignment=TA_LEFT,
        spaceAfter=1,
    )
    st_valor = ParagraphStyle(
        'valor',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=COLOR_PRIMARIO,
        alignment=TA_LEFT,
        spaceAfter=4,
        leading=13,
    )
    st_url = ParagraphStyle(
        'url',
        fontName='Helvetica',
        fontSize=7,
        textColor=COLOR_TEXTO_CLARO,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    st_fecha = ParagraphStyle(
        'fecha',
        fontName='Helvetica',
        fontSize=7,
        textColor=COLOR_TEXTO_CLARO,
        alignment=TA_RIGHT,
        spaceAfter=0,
    )
    st_nombre_grande = ParagraphStyle(
        'nombre_grande',
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=COLOR_PRIMARIO,
        alignment=TA_LEFT,
        spaceAfter=2,
        leading=16,
    )

    # ── Generar QR ────────────────────────────────────────────────────────────
    qr_buf = _generate_qr_png(url)
    qr_reader = ImageReader(qr_buf)
    qr_size = 4.2 * cm

    # ── Tabla del encabezado (fondo azul oscuro) ──────────────────────────────
    header_data = [[
        Paragraph('ASSE-GestACT', st_titulo),
        Paragraph(tipo_label, st_subtitulo),
    ]]
    header_table = Table(header_data, colWidths=['65%', '35%'])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_PRIMARIO),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_BLANCO),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (0, -1), 12),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    # ── Contenido central: QR + datos ────────────────────────────────────────
    # Columna izquierda: QR
    from reportlab.platypus import Image as RLImage
    qr_img = RLImage(qr_buf, width=qr_size, height=qr_size)

    # Columna derecha: datos del activo
    label_nombre = Paragraph('Nombre del Activo', st_label)
    val_nombre = Paragraph(nombre, st_nombre_grande)

    label_id = Paragraph('N° de Serie / Identificador', st_label)
    identificador_display = identificador if identificador != '-' else '—'
    val_id = Paragraph(f'<b>{identificador_display}</b>', ParagraphStyle(
        'val_id',
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=COLOR_SECUNDARIO,
        alignment=TA_LEFT,
        spaceAfter=4,
    ))

    label_inv = Paragraph('N° Inventario', st_label)
    val_inv = Paragraph(numero_inventario, st_valor)

    label_ubi = Paragraph('Ubicación', st_label)
    val_ubi = Paragraph(lugar_nombre, st_valor)

    label_est = Paragraph('Estado', st_label)
    val_est = Paragraph(estado_nombre, st_valor)

    datos_col = [
        label_nombre, val_nombre,
        label_id, val_id,
        label_inv, val_inv,
        label_ubi, val_ubi,
        label_est, val_est,
    ]

    from reportlab.platypus import KeepTogether
    datos_tabla = Table(
        [[item] for item in datos_col],
        colWidths=['100%'],
    )
    datos_tabla.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    # Tabla central con QR a la izquierda y datos a la derecha
    body_data = [[qr_img, datos_tabla]]
    body_table = Table(body_data, colWidths=[qr_size + 0.4 * cm, None])
    body_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_FONDO),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (0, -1), 10),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 12),
        ('LEFTPADDING', (1, 0), (1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDE),
    ]))

    # ── Pie de la etiqueta: URL + fecha ──────────────────────────────────────
    # Truncar URL si es muy larga
    url_display = url if len(url) <= 80 else url[:77] + '...'
    footer_data = [[
        Paragraph(url_display, st_url),
        Paragraph(f'Generado: {fecha_gen}', st_fecha),
    ]]
    footer_table = Table(footer_data, colWidths=['70%', '30%'])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ACENTO),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (0, -1), 10),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    # ── Armar documento ───────────────────────────────────────────────────────
    elements = [
        header_table,
        body_table,
        footer_table,
    ]

    doc.build(elements)
    return buf.getvalue()
