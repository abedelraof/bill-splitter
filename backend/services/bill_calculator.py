from backend import models, schemas


def _resolve_extra(type_: str | None, value: float | None, subtotal: float) -> float:
    if type_ is None or value is None:
        return 0.0
    if type_ == "percent":
        return subtotal * value / 100
    return value  # fixed


def _friend_item_contribution(item: models.BillItem, friend_id: int) -> float:
    assigned_ids = [a.friend_id for a in item.assignments]
    if friend_id not in assigned_ids or not assigned_ids:
        return 0.0
    return item.amount / len(assigned_ids)


def calculate_summary(bill: models.Bill, friends: list[models.Friend]) -> dict:
    items = bill.items
    subtotal = sum(i.amount for i in items)

    vat_amount = _resolve_extra(bill.vat_type, bill.vat_value, subtotal)
    service_amount = _resolve_extra(bill.service_type, bill.service_value, subtotal)
    discount_amount = _resolve_extra(bill.discount_type, bill.discount_value, subtotal)
    net_extras = vat_amount + service_amount - discount_amount
    grand_total = subtotal + net_extras

    friend_summaries = []
    total_assigned = 0.0

    for friend in friends:
        friend_subtotal = sum(_friend_item_contribution(item, friend.id) for item in items)
        if friend_subtotal == 0:
            continue
        extras_share = net_extras * (friend_subtotal / subtotal) if subtotal > 0 else 0.0
        total_assigned += friend_subtotal
        friend_summaries.append(
            schemas.FriendSummary(
                friend_id=friend.id,
                name=friend.name,
                items_subtotal=round(friend_subtotal, 2),
                extras_share=round(extras_share, 2),
                total=round(friend_subtotal + extras_share, 2),
            )
        )

    unassigned_subtotal = round(subtotal - total_assigned, 2)

    return schemas.BillSummaryResponse(
        bill_id=bill.id,
        subtotal=round(subtotal, 2),
        vat_amount=round(vat_amount, 2),
        service_amount=round(service_amount, 2),
        discount_amount=round(discount_amount, 2),
        grand_total=round(grand_total, 2),
        friends=friend_summaries,
        unassigned_subtotal=max(0.0, unassigned_subtotal),
    )
