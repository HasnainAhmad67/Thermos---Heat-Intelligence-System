from schemas.models import Asset, RiskScore, PriorityItem


CRITICALITY_WEIGHT = 0.3
RISK_WEIGHT = 0.7


def _build_reason(risk: RiskScore, asset: Asset) -> str:
    top_driver = max(
        risk.drivers.model_dump().items(),
        key=lambda kv: kv[1],
    )[0]

    driver_label = top_driver.replace("_", " ")

    if asset.criticality >= 0.8:
        criticality_note = (
            f" Prioritized higher due to this asset's high "
            f"criticality ({int(asset.criticality * 100)}%)."
        )

    elif asset.criticality <= 0.65:
        criticality_note = (
            f" Priority is tempered by this asset's lower "
            f"criticality ({int(asset.criticality * 100)}%)."
        )

    else:
        criticality_note = ""

    return (
        f"{risk.level} risk ({risk.score}/100), "
        f"driven mainly by {driver_label}."
        f"{criticality_note}"
    )


def _recommend_action(risk: RiskScore, rank: int) -> str:
    top_driver = max(
        risk.drivers.model_dump().items(),
        key=lambda kv: kv[1],
    )[0]

    action_by_driver = {
        "hazard": (
            "Consider shade or reflective coating "
            "to reduce direct heat load."
        ),
        "exposure": (
            "Add shade structure or vegetation buffer "
            "to reduce sun exposure."
        ),
        "vulnerability": (
            "Increase monitoring frequency given "
            "this asset's high criticality."
        ),
        "persistence": (
            "Add ventilation to reduce sustained heat build-up."
        ),
        "response_gap": (
            "Review response readiness and staffing "
            "for this zone."
        ),
    }

    base_action = action_by_driver.get(
        top_driver,
        "Monitor conditions and reassess.",
    )

    if rank == 1:
        return f"Address first: {base_action}"

    return base_action


def rank_priorities(
    assets: list[Asset],
    risk_scores: list[RiskScore],
) -> list[PriorityItem]:

    risk_by_asset = {
        r.asset_id: r
        for r in risk_scores
    }

    items: list[PriorityItem] = []

    for asset in assets:
        risk = risk_by_asset.get(asset.id)

        if not risk:
            continue

        priority_score = round(
            (
                risk.score * RISK_WEIGHT
            )
            + (
                asset.criticality
                * 100
                * CRITICALITY_WEIGHT
            ),
            1,
        )

        items.append(
            PriorityItem(
                asset_id=asset.id,
                asset_name=asset.name,
                risk_score=risk.score,
                criticality=asset.criticality,
                priority_score=priority_score,
                rank=0,
                reason=_build_reason(
                    risk,
                    asset,
                ),
                recommended_action="",
            )
        )

    items.sort(
        key=lambda i: i.priority_score,
        reverse=True,
    )

    for idx, item in enumerate(
        items,
        start=1,
    ):
        item.rank = idx
        item.recommended_action = _recommend_action(
            risk_by_asset[item.asset_id],
            idx,
        )

    return items