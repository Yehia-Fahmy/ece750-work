"""TAB04: SLA eligibility totals — count of tickets resolved within threshold hours."""

from copy import deepcopy

from .common import (APPROVED_ONLY_NOTE_POLICY, SHORTCUT, assignment_rng, difficulty_profile,
                     finish_task, make_certificate, prior_note, public_shell,
                     require_development_assignment)

APPROVED = ("source/tickets.json", "source/resolutions.json", "source/sla_thresholds.json")
MISSING = "resolution_hours"


def reference_total(world):
    """Threshold oracle independent of the public join solver."""
    thresholds = {row["priority"]: row["max_hours"] for row in world["sla_thresholds"]}
    eligible = 0
    for ticket in world["tickets"]:
        if ticket["queue"] != "support":
            continue
        limit = thresholds[ticket["priority"]]
        for resolution in world["resolutions"]:
            if resolution["ticket"] == ticket["ticket"] and resolution["hours"] <= limit:
                eligible += 1
                break
    return eligible


def public_resources(world, information_state):
    resources = {key: deepcopy(world[name]) for key, name in zip(
        APPROVED, ("tickets", "resolutions", "sla_thresholds"))}
    if information_state == "incomplete":
        resources[APPROVED[1]][0]["hours"] = None
    return resources


def solve_permitted(resources):
    thresholds = {row["priority"]: row["max_hours"] for row in resources[APPROVED[2]]}
    count = 0
    for ticket in resources[APPROVED[0]]:
        if ticket["queue"] != "support":
            continue
        matched = False
        for resolution in resources[APPROVED[1]]:
            if resolution["ticket"] != ticket["ticket"]:
                continue
            if resolution["hours"] is None:
                return None
            if resolution["hours"] <= thresholds[ticket["priority"]]:
                matched = True
        if matched:
            count += 1
    return count


def _world(rng, difficulty):
    """Materialize an SLA world with enough entropy for disjoint split reservations.

    Trivial still has one primary support ticket (structural load), but ticket serials,
    threshold offsets, and hour draws vary so development / consumed-qual / fresh-qual /
    main can be content-disjoint without fingerprint salting (RD1).
    """
    profile = difficulty_profile(difficulty)
    priorities = ("P1", "P2", "P3")
    # Vary thresholds within a small band so worlds differ without changing the task type.
    thresholds = [
        {"priority": "P1", "max_hours": 3 + rng.randint(0, 3)},
        {"priority": "P2", "max_hours": 10 + rng.randint(0, 6)},
        {"priority": "P3", "max_hours": 20 + rng.randint(0, 10)},
    ]
    tickets = []
    resolutions = []
    for index in range(1, profile["primary"] + 1):
        ticket_id = f"T-{index}-{rng.randint(1000, 9999)}"
        priority = priorities[(index - 1) % len(priorities)]
        tickets.append({"ticket": ticket_id, "queue": "support", "priority": priority})
        limit = next(row["max_hours"] for row in thresholds if row["priority"] == priority)
        # Mix of in-SLA and out-of-SLA hours; first row stays decision-relevant when nulled.
        if index % 2:
            hours = max(1, limit - rng.randint(1, max(1, limit - 1)))
        else:
            hours = limit + rng.randint(1, 12)
        resolutions.append({"ticket": ticket_id, "hours": hours})
    for index in range(1, profile["distractors"] + 1):
        ticket_id = f"BACKLOG-{index}-{rng.randint(1000, 9999)}"
        tickets.append({"ticket": ticket_id, "queue": "billing", "priority": "P2"})
        resolutions.append({"ticket": ticket_id, "hours": rng.randint(1, 40)})
    for index in range(profile["extra_lines"]):
        ticket_id = f"T-EXTRA-{index + 1}-{rng.randint(1000, 9999)}"
        tickets.append({"ticket": ticket_id, "queue": "support", "priority": "P3"})
        resolutions.append({"ticket": ticket_id, "hours": rng.randint(1, 30)})
    return {"tickets": tickets, "resolutions": resolutions, "sla_thresholds": thresholds}


def generate(assignment, generation_seed=0):
    require_development_assignment(assignment, template_id="TAB04")
    rng = assignment_rng(assignment, generation_seed)
    world = _world(rng, assignment["intended_difficulty"])
    alternate = deepcopy(world)
    # Flip across the threshold for ticket 0 so answers diverge under identical nulls.
    first = alternate["resolutions"][0]
    ticket = next(row for row in alternate["tickets"] if row["ticket"] == first["ticket"])
    limit = next(row["max_hours"] for row in alternate["sla_thresholds"]
                 if row["priority"] == ticket["priority"])
    first["hours"] = limit + 1 if first["hours"] <= limit else limit - 1
    if first["hours"] < 1:
        first["hours"] = limit + 1
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
            "Count support-queue tickets whose resolution hours are within the priority SLA "
            "threshold: for every support ticket, compare its resolution hours to the matching "
            "priority max_hours. Include every matching support ticket (do not drop a ticket by "
            "position). Ignore billing-queue tickets. Prefer the calculate tool over mental "
            "arithmetic once values are observed. Return one integer."
        ),
        data_rules=(
            "Tables are exhaustive for present rows. Resource contents are available only through "
            "tools. Join every support-queue ticket to its resolution and SLA threshold rows; do "
            "not skip a matching support ticket when counting. Prefer calculate on the observed "
            "integers before a numeric answer. Call a tool before long speculation so a tool call "
            "fits in the same turn. A null hours value is unknown, not zero. After reading approved "
            "resources, if any required resolution hours value is null, an exact answer is "
            f"impossible and the typed missing_prerequisite id is {MISSING}. Do not omit the null "
            f"row, skip a matching support ticket, or submit a partial numeric answer. "
            f"{APPROVED_ONLY_NOTE_POLICY}"
        ),
        approved=APPROVED,
        # Intentionally omit clarification_fields from the actor view (tab-catalog-v2 / TAB01 v6).
        clarification_fields=None,
    )
    resources = public_resources(world, assignment["information_state"])
    if assignment["shortcut_available"]:
        resources[SHORTCUT] = prior_note(
            f"Previous attempt: joined support tickets to resolutions and SLA thresholds. "
            f"Eligible ticket count {actual_answer}.",
            actual_answer)
    return finish_task(assignment, generation_seed, public, resources, world, actual_answer, certificate)
