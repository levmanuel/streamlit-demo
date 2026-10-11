"""Calculs du Liquidity Coverage Ratio (Bâle III) — fonctions pures."""

PLAFOND_INFLOWS = 0.75  # les entrées sont plafonnées à 75 % des sorties


def stresser(valeur, facteur_pct):
    """Applique un facteur de stress en % (-100 → 0, +50 → ×1,5)."""
    return valeur * (1 + facteur_pct / 100)


def inflows_cappes(outflows, inflows):
    return min(PLAFOND_INFLOWS * outflows, inflows)


def net_outflows(outflows, inflows):
    return outflows - inflows_cappes(outflows, inflows)


def lcr(hqla, outflows, inflows, decimales=2):
    """LCR en %, ou +inf si les sorties nettes sont nulles."""
    net = net_outflows(outflows, inflows)
    if net <= 0:
        return float("inf")
    return round(100 * hqla / net, decimales)


def simulation(hqla, outflows, inflows, taux_pct, jours=30):
    """Hausse quotidienne des outflows : retourne (jours, outflows, lcr) sur `jours` jours."""
    days, outflow_sim, lcr_sim = [], [], []
    courant = outflows
    for i in range(jours):
        courant = round((1 + taux_pct / 100) * courant, 2)
        days.append(i + 1)
        outflow_sim.append(courant)
        lcr_sim.append(lcr(hqla, courant, inflows, decimales=1))
    return days, outflow_sim, lcr_sim
