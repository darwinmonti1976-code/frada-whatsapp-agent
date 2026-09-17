# agent/tools.py — Herramientas del agente
# Generado por AgentKit

"""
Herramientas especificas de Frada Skin Center.

OJO: estas funciones NO se ejecutan solas todavia. La informacion del negocio le llega
al agente por el system prompt (config/prompts.yaml), asi que para CONTESTAR preguntas
no hace falta nada de aca. Este archivo es el lugar para las ACCIONES —registrar un lead,
anotar una solicitud de devis, abrir un ticket de soporte— y conectarlas al ciclo de tool
use de Claude es un paso aparte.
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger("agentkit")

CARPETA_KNOWLEDGE = Path("knowledge")

URL_RESERVA = "https://frada-skin-center.agenda.ch"


def cargar_info_negocio() -> dict:
    """Carga la informacion del negocio desde config/business.yaml."""
    try:
        with open("config/business.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.error("config/business.yaml no encontrado")
        return {}


def obtener_horario() -> dict:
    """Retorna el horario de atencion del negocio."""
    info = cargar_info_negocio()
    return {
        "horario": info.get("negocio", {}).get("horario", "No disponible"),
        "esta_abierto": True,  # TODO: calcular segun la hora actual y el horario
    }


def buscar_en_knowledge(consulta: str) -> str:
    """
    Busca informacion en los archivos de /knowledge.
    Retorna los fragmentos que coinciden con la consulta.
    """
    if not CARPETA_KNOWLEDGE.is_dir():
        return "No hay archivos de conocimiento disponibles."

    resultados = []
    for ruta in sorted(CARPETA_KNOWLEDGE.iterdir()):
        if ruta.name.startswith(".") or not ruta.is_file():
            continue
        try:
            contenido = ruta.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binarios y archivos ilegibles se saltean
        if consulta.lower() in contenido.lower():
            resultados.append(f"[{ruta.name}]: {contenido[:500]}")

    if resultados:
        return "\n---\n".join(resultados)
    return "No encontre informacion especifica sobre eso en mis archivos."


# ════════════════════════════════════════════════════════════
# AGENDAR CITAS
#
# Frada NO tiene un sistema de reservas propio conectado: las citas se toman
# en agenda.ch. Por eso no hay una funcion "reservar_cita" que escriba en un
# calendario — la accion es orientar a la clienta hacia ese link.
# ════════════════════════════════════════════════════════════

def obtener_link_reserva() -> str:
    """Retorna el link donde la clienta puede elegir su propio horario."""
    return URL_RESERVA


# ════════════════════════════════════════════════════════════
# CALIFICAR Y ATENDER LEADS
# ════════════════════════════════════════════════════════════

def registrar_lead(telefono: str, servicio_interes: str, notas: str = "") -> dict:
    """
    Registra un prospecto interesado en un servicio.

    TODO: hoy solo loguea. Conectar a una hoja de calculo, CRM o tabla propia
    cuando Frada quiera hacer seguimiento real de los leads.
    """
    logger.info(f"[LEAD] {telefono} — interes: {servicio_interes} — notas: {notas}")
    return {"telefono": telefono, "servicio_interes": servicio_interes, "notas": notas}


# ════════════════════════════════════════════════════════════
# TOMAR PEDIDOS / SOLICITUDES DE DEVIS
#
# Varios servicios de Frada son "sur devis" (epilation laser, Aquahydra,
# radiofrequence): el precio depende de la zona o del caso. Esta funcion
# deja registrada la solicitud para que el equipo la cotice.
# ════════════════════════════════════════════════════════════

def crear_solicitud_devis(telefono: str, servicio: str, detalle: str = "") -> dict:
    """
    Registra una solicitud de presupuesto para un servicio "sur devis".

    TODO: hoy solo loguea. Conectar a email, CRM o planilla cuando Frada
    quiera que estas solicitudes lleguen automaticamente al equipo.
    """
    logger.info(f"[DEVIS] {telefono} — servicio: {servicio} — detalle: {detalle}")
    return {"telefono": telefono, "servicio": servicio, "detalle": detalle}


# ════════════════════════════════════════════════════════════
# SOPORTE POST-VENTA
# ════════════════════════════════════════════════════════════

def crear_ticket_soporte(telefono: str, problema: str) -> dict:
    """
    Abre un ticket de soporte post-soin (dudas, molestias, seguimiento).

    TODO: hoy solo loguea. Conectar a un sistema de tickets real cuando
    Frada quiera llevar registro y asignacion formal de estos casos.
    """
    logger.info(f"[SOPORTE] {telefono} — problema: {problema}")
    return {"telefono": telefono, "problema": problema, "estado": "abierto"}
