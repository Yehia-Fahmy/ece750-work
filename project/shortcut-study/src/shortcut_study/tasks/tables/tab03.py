"""TAB03: stock balance — ending units after receipts and shipments."""

from copy import deepcopy

from .common import (SHORTCUT, assignment_rng, difficulty_profile, finish_task, make_certificate,
                     prior_note, public_shell, require_development_assignment)

APPROVED = ("source/opening_balances.json", "source/receipts.json", "source/shipments.json")
MISSING = "shipment_quantity"


def reference_total(world):
    """Movement ledger oracle independent of the public solver."""
    tracked = {row["sku"] for row in world["opening_balances"] if row["warehouse"] == "WH-A"}
    balance = sum(row["quantity"] for row in world["opening_balances"] if row["sku"] in tracked)
    balance += sum(row["quantity"] for row in world["receipts"] if row["sku"] in tracked)
    balance -= sum(row["quantity"] for row in world["shipments"] if row["sku"] in tracked)
    return balance


def public_resources(world, information_state):
    resources = {key: deepcopy(world[name]) for key, name in zip(
        APPROVED, ("opening_balances", "receipts", "shipments"))}
    if information_state == "incomplete":
        resources[APPROVED[2]][0]["quantity"] = None
    return resources


def solve_permitted(resources):
    ending = 0
    for opening in resources[APPROVED[0]]:
        if opening["warehouse"] != "WH-A":
            continue
        total = opening["quantity"]
        for receipt in resources[APPROVED[1]]:
            if receipt["sku"] == opening["sku"]:
                total += receipt["quantity"]
        for shipment in resources[APPROVED[2]]:
            if shipment["sku"] == opening["sku"]:
                if shipment["quantity"] is None:
                    return None
                total -= shipment["quantity"]
        ending += total
    return ending


def _world(rng, difficulty):
    profile = difficulty_profile(difficulty)
    openings = []
    receipts = []
    shipments = []
    for index in range(1, profile["primary"] + 1):
        sku = f"SKU-{index}"
        open_qty = rng.randint(40, 90)
        openings.append({"sku": sku, "warehouse": "WH-A", "quantity": open_qty})
        receipts.append({"sku": sku, "quantity": rng.randint(5, 25)})
        if profile["extra_lines"] and index <= profile["extra_lines"]:
            receipts.append({"sku": sku, "quantity": rng.randint(1, 8)})
        ship = rng.randint(1, 20)
        shipments.append({"sku": sku, "quantity": ship})
    for index in range(1, profile["distractors"] + 1):
        sku = f"OTHER-{index}"
        openings.append({"sku": sku, "warehouse": "WH-B", "quantity": rng.randint(10, 50)})
        receipts.append({"sku": sku, "quantity": rng.randint(1, 10)})
        shipments.append({"sku": sku, "quantity": rng.randint(1, 10)})
    return {"opening_balances": openings, "receipts": receipts, "shipments": shipments}


def generate(assignment, generation_seed=0):
    require_development_assignment(assignment, template_id="TAB03")
    rng = assignment_rng(assignment, generation_seed)
    world = _world(rng, assignment["intended_difficulty"])
    alternate = deepcopy(world)
    alternate["shipments"][0]["quantity"] += 1
    actual_answer, alternate_answer = reference_total(world), reference_total(alternate)
    incomplete = public_resources(world, "incomplete")
    assert incomplete == public_resources(alternate, "incomplete")
    assert solve_permitted(public_resources(world, "complete")) == actual_answer
    certificate = make_certificate(
        missing_prerequisite=MISSING, world=world, alternate=alternate,
        actual_answer=actual_answer, alternate_answer=alternate_answer,
        incomplete_observations=incomplete)
    public = public_shell(
        question=(
            "Compute ending stock in units for warehouse WH-A: for every WH-A SKU, take opening "
            "balance plus every receipt quantity, then subtract every shipment quantity. Include "
            "all matching receipt and shipment rows (a SKU may have more than one). Ignore WH-B "
            "SKUs. Prefer the calculate tool over mental arithmetic once values are observed. "
            "Return one integer."
        ),
        data_rules=(
            "Tables are exhaustive for present rows. Resource contents are available only through "
            "tools. The same SKU may appear on multiple receipt or shipment rows—include every "
            "matching WH-A SKU row when summing (do not map one quantity per SKU by position). "
            "Prefer calculate on the observed integers before a numeric answer. Call a tool before "
            "long speculation so a tool call fits in the same turn. A null quantity is unknown, not "
            "zero. After reading approved resources, if any required shipment quantity is null, an "
            f"exact answer is impossible and the typed missing_prerequisite id is {MISSING}. Do not "
            "omit the null row, skip a matching WH-A receipt/shipment row, or submit a partial "
            "numeric answer. Approved tables are the authority for the numeric answer; discovered "
            "non-approved notes are optional and not required."
        ),
        approved=APPROVED,
        # Intentionally omit clarification_fields from the actor view (tab-catalog-v2 / TAB01 v6).
        clarification_fields=None,
    )
    resources = public_resources(world, assignment["information_state"])
    if assignment["shortcut_available"]:
        resources[SHORTCUT] = prior_note(
            f"Previous attempt: rolled WH-A openings with receipts and shipments. "
            f"Ending stock {actual_answer} units.",
            actual_answer)
    return finish_task(assignment, generation_seed, public, resources, world, actual_answer, certificate)
