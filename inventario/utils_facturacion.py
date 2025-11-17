from __future__ import annotations

import io
from dataclasses import dataclass
from typing import List

from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

from .models import Factura, FacturaActivo


@dataclass
class FacturaPDFResult:
    factura: Factura
    pdf_bytes: bytes


def render_factura_pdf(factura: Factura, items: List[FacturaActivo]) -> bytes:
    """Genera el PDF de la factura usando ReportLab con diseño profesional"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=35,
        bottomMargin=35
    )
    elements = []
    
    # Paleta de colores profesional
    primary_color = colors.HexColor('#1e3a8a')      # Azul oscuro profesional
    secondary_color = colors.HexColor('#3b82f6')    # Azul medio
    accent_color = colors.HexColor('#e0f2fe')       # Azul claro
    dark_text = colors.HexColor('#1f2937')          # Gris oscuro
    light_bg = colors.HexColor('#f8fafc')           # Gris muy claro
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Título principal con estilo corporativo (reducido)
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=primary_color,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=24
    )
    
    # Subtítulo (reducido)
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Encabezado de sección (reducido)
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=primary_color,
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        borderPadding=(0, 0, 4, 0)
    )
    
    # Estilo para firmas (reducido)
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=4,
        leading=12,
        fontName='Helvetica'
    )

    normal_style = styles['Normal']
    
    # === ENCABEZADO DEL DOCUMENTO ===
    
    # Título principal
    elements.append(Paragraph("REMITO DE ACTIVOS", title_style))
    elements.append(Paragraph("Sistema de Gestión de Inventario - ASSE-GestACT", subtitle_style))
    
    # Línea divisoria decorativa (más delgada)
    line_table = Table([['']], colWidths=[7.3*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, secondary_color),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(line_table)
    
    # === INFORMACIÓN DE LA FACTURA ===
    
    # Convertir la fecha de emisión a la zona horaria local
    fecha_local = timezone.localtime(factura.fecha_emision)
    fecha_str = fecha_local.strftime('%d/%m/%Y %H:%M')
    lugar_origen = (
        factura.lugar_origen.nombre
        if factura.lugar_origen else 'N/A'
    )
    destinatario = (
        factura.lugar_destino.nombre_completo
        if hasattr(factura.lugar_destino, 'nombre_completo') and factura.lugar_destino.nombre_completo
        else factura.lugar_destino.nombre
    )
    emitido = factura.emitido_por if factura.emitido_por else 'N/A'

    # Tabla de información en dos columnas con diseño moderno (compacta)
    info_data = [
        [
            Paragraph('<b>Nº de Remito:</b>', normal_style),
            Paragraph(f'<b>{factura.numero}</b>', normal_style),
            Paragraph('<b>Fecha de Emisión:</b>', normal_style),
            Paragraph(fecha_str, normal_style)
        ],
        [
            Paragraph('<b>Emitido por:</b>', normal_style),
            Paragraph(emitido, normal_style),
            Paragraph('<b>Lugar Origen:</b>', normal_style),
            Paragraph(lugar_origen, normal_style)
        ],
    ]
    
    info_table = Table(info_data, colWidths=[1.2*inch, 2.45*inch, 1.2*inch, 2.45*inch])
    info_table.setStyle(TableStyle([
        # Fondo alternado
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_text),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, light_bg]),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.08*inch))
    
    # Información de destino en caja destacada (compacta)
    destino_data = [
        [
            Paragraph('<b>DESTINATARIO</b>', heading_style),
        ],
        [
            Paragraph(f'<b>{destinatario}</b><br/>{factura.lugar_destino.nombre}', normal_style)
        ]
    ]
    
    destino_table = Table(destino_data, colWidths=[7.3*inch])
    destino_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), accent_color),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, 1), 9),
        ('BOX', (0, 0), (-1, -1), 1.5, secondary_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(destino_table)
    elements.append(Spacer(1, 0.12*inch))
    
    # === OBSERVACIONES ===
    if factura.observaciones:
        elements.append(Paragraph("OBSERVACIONES", heading_style))
        obs_style = ParagraphStyle('ObsStyle', parent=normal_style, fontSize=8)
        obs_table = Table([[Paragraph(factura.observaciones, obs_style)]], colWidths=[7.3*inch])
        obs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_bg),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(obs_table)
        elements.append(Spacer(1, 0.1*inch))
    
    # === TABLA DE ACTIVOS ===
    elements.append(Paragraph("DETALLE DE ACTIVOS", heading_style))
    elements.append(Spacer(1, 0.05*inch))
    
    if items:
        # Estilo compacto para tabla
        table_style = ParagraphStyle('TableText', parent=normal_style, fontSize=8)
        
        # Encabezados de la tabla con diseño profesional
        activos_data = [
            [
                Paragraph('<b>Tipo</b>', table_style),
                Paragraph('<b>Nombre</b>', table_style),
                Paragraph('<b>Serie</b>', table_style),
                Paragraph('<b>Estado</b>', table_style),
                Paragraph('<b>Lugar Previo</b>', table_style),
                Paragraph('<b>Cant.</b>', table_style)
            ]
        ]

        # Datos de los activos
        for item in items:
            # Truncar nombre si es muy largo
            nombre = item.nombre_activo
            if len(nombre) > 35:
                nombre = nombre[:35] + '...'

            # Truncar lugar previo si es muy largo
            lugar = item.lugar_previo
            if len(lugar) > 25:
                lugar = lugar[:25] + '...'

            activos_data.append([
                Paragraph(item.get_tipo_activo_display(), table_style),
                Paragraph(nombre, table_style),
                Paragraph(item.numero_serie, table_style),
                Paragraph(item.estado_previo, table_style),
                Paragraph(lugar, table_style),
                Paragraph(str(item.cantidad or 1), table_style),
            ])

        col_widths = [0.85*inch, 2.2*inch, 1*inch, 0.95*inch, 1.85*inch, 0.45*inch]
        activos_table = Table(activos_data, colWidths=col_widths)
        activos_table.setStyle(TableStyle([
            # Encabezado con diseño moderno (mismo color que el total)
            ('BACKGROUND', (0, 0), (-1, 0), accent_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), primary_color),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Cuerpo de la tabla
            ('TEXTCOLOR', (0, 1), (-1, -1), dark_text),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Tipo centrado
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Cantidad centrada
            ('ALIGN', (1, 1), (4, -1), 'LEFT'),    # Resto a la izquierda
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            
            # Bordes y fondos alternados
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('BOX', (0, 0), (-1, -1), 1.2, secondary_color),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, light_bg]),
        ]))

        elements.append(activos_table)
        
        # Resumen de cantidad
        total_items = sum(item.cantidad or 1 for item in items)
        summary_data = [[
            '',
            '',
            '',
            '',
            Paragraph('<b>TOTAL:</b>', table_style),
            Paragraph(f'<b>{total_items}</b>', table_style)
        ]]
        summary_table = Table(summary_data, colWidths=col_widths)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (4, 0), (-1, 0), accent_color),
            ('ALIGN', (4, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (4, 0), (-1, 0), 8),
            ('TOPPADDING', (4, 0), (-1, 0), 4),
            ('BOTTOMPADDING', (4, 0), (-1, 0), 4),
            ('BOX', (4, 0), (-1, 0), 1.2, secondary_color),
        ]))
        elements.append(summary_table)
    else:
        msg = "No hay activos en este remito"
        elements.append(Paragraph(msg, normal_style))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # === FIRMAS DE ENTREGA Y RECEPCIÓN ===
    elements.append(Paragraph("CONFIRMACIÓN DE ENTREGA Y RECEPCIÓN", heading_style))
    elements.append(Spacer(1, 0.06*inch))

    # Tabla de firmas con diseño profesional (compacta)
    firma_table_data = [
        [
            Paragraph(
                "<b>Entregado por:</b><br/>"
                "Gestión de Activos - ASSE<br/><br/>"
                "_____________________________<br/>"
                "<font size=7>Firma y Aclaración</font>",
                signature_style,
            ),
            Paragraph(
                "<b>Recibido por:</b><br/>"
                f"{destinatario}<br/><br/>"
                "_____________________________<br/>"
                "<font size=7>Firma y Aclaración</font>",
                signature_style,
            ),
        ],
        [
            Paragraph(
                "<b>Fecha:</b> ____ / ____ / ________",
                signature_style
            ),
            Paragraph(
                "<b>Fecha:</b> ____ / ____ / ________",
                signature_style
            ),
        ],
    ]

    firma_table = Table(firma_table_data, colWidths=[3.65*inch, 3.65*inch])
    firma_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor('#cbd5e1')),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 0), (-1, 0), light_bg),
    ]))

    elements.append(firma_table)
    
    # Pie de página con información legal (compacto)
    elements.append(Spacer(1, 0.12*inch))
    
    footer_text = (
        "<font size=7 color='#64748b'>"
        "Este documento constituye comprobante de entrega de activos. "
        "Conservar para auditorías y control de inventario. "
        f"Generado el {fecha_str} por ASSE-GestACT."
        "</font>"
    )
    footer_para = Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        leading=9
    ))
    elements.append(footer_para)
    
    # Construir el PDF
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def generar_factura_pdf(factura_id: int) -> FacturaPDFResult:
    factura = Factura.objects.get(pk=factura_id)
    items = list(factura.activos.all())
    pdf_bytes = render_factura_pdf(factura, items)
    return FacturaPDFResult(factura=factura, pdf_bytes=pdf_bytes)



