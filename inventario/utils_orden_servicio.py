"""Utilidades para generar PDFs de órdenes de servicio."""
from __future__ import annotations

from datetime import date, datetime
from io import BytesIO
from typing import Optional

from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import OrdenServicio


def _format_datetime(value: Optional[datetime]) -> str:
    if not value:
        return "-"
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    value = timezone.localtime(value)
    return value.strftime("%d/%m/%Y %H:%M")


def _format_date(value: Optional[date]) -> str:
    if not value:
        return "-"
    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y")
    return str(value)


def build_orden_servicio_pdf(orden: OrdenServicio) -> bytes:
    """Genera un PDF profesional con el detalle de una orden de servicio."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    elements = []

    primary_color = colors.HexColor("#0f172a")
    secondary_color = colors.HexColor("#1d4ed8")
    accent_color = colors.HexColor("#e0f2fe")
    neutral_bg = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        "OrdenServicioTitle",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=primary_color,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )

    subtitle_style = ParagraphStyle(
        "OrdenServicioSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER,
        spaceAfter=18,
    )

    section_title_style = ParagraphStyle(
        "OrdenServicioSection",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=secondary_color,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )

    normal_style = styles["Normal"]
    normal_style.fontSize = 9

    elements.append(Paragraph("ORDEN DE SERVICIO", title_style))
    elements.append(
        Paragraph(
            "Sistema de Gestión de Activos - ASSE-GestACT", subtitle_style
        )
    )

    header_data = [
        [
            Paragraph("<b>N° Orden:</b>", normal_style),
            Paragraph(orden.numero_orden, normal_style),
            Paragraph("<b>Estado:</b>", normal_style),
            Paragraph(orden.get_estado_display(), normal_style),
        ],
        [
            Paragraph("<b>Tipo de servicio:</b>", normal_style),
            Paragraph(orden.get_tipo_servicio_display(), normal_style),
            Paragraph("<b>Prioridad:</b>", normal_style),
            Paragraph(orden.get_prioridad_display(), normal_style),
        ],
        [
            Paragraph("<b>Fecha solicitud:</b>", normal_style),
            Paragraph(_format_datetime(orden.fecha_solicitud), normal_style),
            Paragraph("<b>Fecha estimada:</b>", normal_style),
            Paragraph(_format_date(orden.fecha_estimada), normal_style),
        ],
        [
            Paragraph("<b>Fecha inicio:</b>", normal_style),
            Paragraph(_format_datetime(orden.fecha_inicio), normal_style),
            Paragraph("<b>Fecha finalización:</b>", normal_style),
            Paragraph(_format_datetime(orden.fecha_finalizacion), normal_style),
        ],
    ]

    header_table = Table(header_data, colWidths=[1.3 * inch, 2.0 * inch, 1.3 * inch, 2.0 * inch])
    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), neutral_bg),
                ("BOX", (0, 0), (-1, -1), 1, secondary_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5f5")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(header_table)

    elements.append(Paragraph("Información del equipo", section_title_style))
    dispositivo_data = [
        [
            Paragraph("<b>Nombre del equipo:</b>", normal_style),
            Paragraph(orden.dispositivo_nombre or "-", normal_style),
        ],
        [
            Paragraph("<b>Tipo:</b>", normal_style),
            Paragraph(orden.get_tipo_dispositivo_display(), normal_style),
        ],
        [
            Paragraph("<b>N° serie:</b>", normal_style),
            Paragraph(orden.dispositivo_numero_serie or "-", normal_style),
        ],
    ]
    dispositivo_table = Table(dispositivo_data, colWidths=[1.6 * inch, 4.0 * inch])
    dispositivo_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#e2e8f0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(dispositivo_table)

    elements.append(Paragraph("Solicitante y asignaciones", section_title_style))
    asignacion_data = [
        [
            Paragraph("<b>Solicitante:</b>", normal_style),
            Paragraph(orden.solicitante or "-", normal_style),
        ],
        [
            Paragraph("<b>Técnico asignado:</b>", normal_style),
            Paragraph(orden.tecnico_asignado or "-", normal_style),
        ],
    ]
    asignacion_table = Table(asignacion_data, colWidths=[1.6 * inch, 4.0 * inch])
    asignacion_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#e2e8f0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(asignacion_table)

    elements.append(Paragraph("Detalle del servicio", section_title_style))

    detalle_data = []
    detalle_data.append(
        [
            Paragraph("<b>Descripción del problema:</b>", normal_style),
            Paragraph(orden.descripcion_problema or "-", normal_style),
        ]
    )
    if orden.diagnostico:
        detalle_data.append(
            [
                Paragraph("<b>Diagnóstico:</b>", normal_style),
                Paragraph(orden.diagnostico, normal_style),
            ]
        )
    if orden.solucion_aplicada:
        detalle_data.append(
            [
                Paragraph("<b>Solución aplicada:</b>", normal_style),
                Paragraph(orden.solucion_aplicada, normal_style),
            ]
        )
    if orden.observaciones:
        detalle_data.append(
            [
                Paragraph("<b>Observaciones:</b>", normal_style),
                Paragraph(orden.observaciones, normal_style),
            ]
        )

    if detalle_data:
        detalle_table = Table(detalle_data, colWidths=[1.7 * inch, 3.9 * inch])
        detalle_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#e2e8f0")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(detalle_table)
    else:
        elements.append(Paragraph("Sin información adicional registrada.", normal_style))

    elements.append(Spacer(1, 0.3 * inch))
    signature_table = Table(
        [
            [Paragraph("Firma del solicitante", normal_style), "", Paragraph("Firma del técnico", normal_style)],
            ["___________________________", "", "___________________________"],
            [Paragraph("Fecha: __________________", normal_style), "", Paragraph("Fecha: __________________", normal_style)],
        ],
        colWidths=[2.5 * inch, 0.5 * inch, 2.5 * inch],
    )
    signature_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LINEBELOW", (0, 1), (0, 1), 0.6, colors.black),
                ("LINEBELOW", (2, 1), (2, 1), 0.6, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(signature_table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
