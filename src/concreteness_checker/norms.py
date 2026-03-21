from __future__ import annotations

from collections.abc import Iterable


def _extend_words(target: dict[str, float], score: float, words: str) -> None:
    for word in words.split():
        target.setdefault(word, score)


def _pluralize(word: str) -> str | None:
    if len(word) < 3 or not word.isalpha():
        return None
    if word.endswith("y") and len(word) > 3 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if word.endswith("f"):
        return word[:-1] + "ves"
    if word.endswith("fe"):
        return word[:-2] + "ves"
    return word + "s"


def _past_tense(word: str) -> str | None:
    if len(word) < 3 or not word.isalpha():
        return None
    if word.endswith("e"):
        return word + "d"
    if word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ied"
    if len(word) >= 3 and word[-1] not in "aeiouwxy" and word[-2] in "aeiou" and word[-3] not in "aeiou":
        return word + word[-1] + "ed"
    return word + "ed"


def _present_participle(word: str) -> str | None:
    if len(word) < 3 or not word.isalpha():
        return None
    if word.endswith("ie"):
        return word[:-2] + "ying"
    if word.endswith("e") and not word.endswith("ee"):
        return word[:-1] + "ing"
    if len(word) >= 3 and word[-1] not in "aeiouwxy" and word[-2] in "aeiou" and word[-3] not in "aeiou":
        return word + word[-1] + "ing"
    return word + "ing"


def _comparative(word: str) -> str | None:
    if len(word) < 4 or not word.isalpha() or word.endswith("ly"):
        return None
    if word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ier"
    if word.endswith("e"):
        return word + "r"
    return word + "er"


def _adverb(word: str) -> str | None:
    if len(word) < 4 or not word.isalpha() or word.endswith("ly"):
        return None
    if word.endswith("ic"):
        return word + "ally"
    if word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ily"
    if word.endswith("le"):
        return word[:-1] + "y"
    return word + "ly"


def _expand_inflections(norms: dict[str, float], words: Iterable[str]) -> None:
    for word in words:
        score = norms[word]
        for variant in (
            _pluralize(word),
            _past_tense(word),
            _present_participle(word),
            _comparative(word),
            _adverb(word),
        ):
            if variant and variant.isalpha():
                norms.setdefault(variant, score)


_BASE_NORMS: dict[str, float] = {
    # === 4.5+ : directly perceivable, physical things ===
    "dog": 4.94, "cat": 4.94, "chair": 4.94, "shoe": 4.94,
    "apple": 4.94, "knife": 4.94, "finger": 4.92, "truck": 4.94,
    "pencil": 4.94, "tree": 4.92, "bottle": 4.92, "hammer": 4.92,
    "nose": 4.92, "elbow": 4.92, "brick": 4.88, "feather": 4.88,
    "bread": 4.92, "door": 4.92, "bone": 4.88, "mud": 4.82,
    "rope": 4.88, "sand": 4.88, "snow": 4.88, "wall": 4.88,
    "blood": 4.80, "skull": 4.86, "stove": 4.88, "lake": 4.88,
    "tongue": 4.86, "jaw": 4.86, "nest": 4.78, "ink": 4.72,

    # === 4.0–4.5 : concrete, sensory, but sometimes used figuratively ===
    "bridge": 4.82, "needle": 4.90, "root": 4.52, "branch": 4.62,
    "shell": 4.62, "wire": 4.78, "chain": 4.62, "pipe": 4.72,
    "thread": 4.42, "hook": 4.72, "blade": 4.82, "lever": 4.58,
    "filter": 4.18, "spring": 4.32, "handle": 4.58, "key": 4.52,
    "pool": 4.62, "stream": 4.58, "channel": 4.08, "edge": 4.12,
    "frame": 4.38, "layer": 3.72, "stack": 4.22, "block": 4.18,
    "node": 3.52, "flag": 4.38, "sink": 4.52, "tap": 4.38,
    "fire": 4.72, "smoke": 4.62, "wave": 3.82, "dust": 4.52,

    # === 3.0–4.0 : midrange, partly grounded ===
    "machine": 4.28, "signal": 3.28, "pattern": 3.22, "weight": 3.82,
    "pressure": 3.42, "force": 3.02, "shape": 3.72, "surface": 3.92,
    "network": 2.82, "model": 2.72, "image": 3.98, "map": 3.92,
    "path": 4.42, "structure": 3.02, "flow": 3.22, "current": 3.42,
    "tension": 3.08, "balance": 2.72, "scale": 3.82, "mark": 3.58,
    "distance": 3.18, "depth": 3.22, "motion": 3.02, "mass": 3.32,
    "contact": 3.22, "link": 3.22, "joint": 3.92, "trace": 2.82,

    # === 2.0–3.0 : mostly abstract, some experiential anchoring ===
    "system": 2.52, "process": 2.38, "method": 2.18, "strategy": 2.02,
    "function": 2.18, "state": 2.42, "condition": 2.22, "context": 2.02,
    "feature": 2.38, "factor": 2.18, "result": 2.28, "effect": 2.18,
    "change": 2.08, "level": 3.18, "type": 2.12, "form": 2.82,
    "domain": 2.48, "range": 2.92, "scope": 2.42, "capacity": 2.72,
    "instance": 2.22, "example": 2.22, "property": 2.22, "rule": 2.18,
    "behavior": 2.18, "event": 2.52, "relation": 2.02, "aspect": 1.92,

    # === 1.0–2.0 : purely abstract ===
    "ontology": 1.42, "epistemology": 1.28, "morphism": 1.52,
    "functor": 1.48, "topology": 1.72, "heuristic": 1.62,
    "invariant": 1.82, "abstraction": 1.58, "validity": 1.62,
    "coherence": 1.62, "equivalence": 1.72, "causation": 1.62,
    "sufficiency": 1.62, "convergence": 1.92, "reification": 1.42,
    "individuation": 1.52, "computation": 1.92, "recursion": 1.82,
    "concept": 1.72, "theory": 1.78, "truth": 1.68, "meaning": 1.72,
    "essence": 1.52, "identity": 1.92, "consciousness": 1.68,
}

_SCORE_GROUPS: tuple[tuple[float, str], ...] = (
    (4.96, "house room table desk couch bed lamp floor ceiling window pillow blanket plate spoon fork cup glass oven fridge freezer towel soap mirror clock wallet coin dollar bicycle scooter motorcycle airplane boat canoe island beach forest mountain valley meadow garden farm barn fence gate sidewalk alley road highway tunnel garage attic basement ladder bucket basket backpack suitcase camera radio guitar violin drum trumpet whistle bell candle lantern torch helmet glove scarf jacket shirt pants sock boot sandal ring necklace bracelet watch marble pebble rock stone crystal pearl diamond emerald ruby sapphire coral sponge mushroom carrot potato onion garlic tomato pepper celery lettuce cabbage broccoli pumpkin melon grape berry orange lemon lime peach pear plum cherry coconut walnut almond peanut hazelnut chestnut rice wheat corn bean pea oat barley flour sugar salt cinnamon vanilla chocolate coffee tea milk cheese butter yogurt egg meat chicken turkey pork beef fish salmon tuna shrimp crab lobster oyster clam jelly honey syrup biscuit cookie cake pie tart muffin pancake waffle sandwich burger sausage bacon noodle pasta pizza cereal porridge soup stew salad gravy sauce vinegar oil cream ice"),
    (4.82, "mailman driveway gravel mailbox porch rooftop chimney curtain mattress closet drawer cabinet counter faucet shower bathtub toilet drain sewer gutter shovel rake hoe plow axe saw drill wrench pliers screw nail bolt hinge wheel tire engine pedal brake steering windshield bumper fender radiator piston axle saddle harness stable kennel leash collar whisker paw claw hoof horn beak wing feather fur tail mane snout tusk antler shell scale fin gill reef dune glacier thunder lightning rainbow cloud breeze storm rain hail sleet frost iceberg puddle pond creek river waterfall canyon cliff cave volcano desert swamp marsh lagoon harbor dock pier anchor sail knot plank beam pillar statue monument tower castle temple church mosque school office factory warehouse market bakery butcher tailor mill furnace boiler kiln anvil apron skillet kettle mug saucer newspaper magazine notebook envelope stamp parcel package luggage crate barrel bottlecap cork zipper button tapestry doorknob handrail"),
    (4.58, "pipeline machinery toolbox workshop shoebox handset cookbook teapot firewood haystack birdhouse doghouse classroom newsroom courtroom washroom engineblock headlight taillight workbench doormat blackboard chalkboard keypad joystick trackpad touchscreen cable cord socket outlet thermostat lockbox stairway walkway footpath footbridge drawbridge overpass underpass footstool stool bench shelf rack hanger pottery cutlery cookware dishpan colander ladle spatula whisk griddle tongs tweezers clip clamp buckle shoelace raincoat overcoat sweater hoodie overalls pajamas mitten earmuff napkin tablecloth bedsheet pillowcase toothbrush toothpaste hairbrush shampoo razor comb lunchbox can opener corkscrew keyhole keyring padlock mousetrap fishhook bait net hammock tent tarp kayak oarsman lifeboat wheelbarrow stroller crib diaper pacifier rattle puppet kite balloon frisbee baseball football basketball tennisball golfball hockeypuck chessboard checkerboard domino puzzle atlas postcard blueprint"),
    (4.34, "bridgework branchwork framework wireframe handlebar keyway filterpaper springboard smokehouse windmill waterwheel millstone gearbox pulley cog gear spindle nozzle valve dashboard steeringwheel footrest armrest bookcase bookshelf tabletop countertop handgrip doorway hallway stairwell threshold doorframe windowsill windowpane fieldstone backseat campsite campfire firepit lanternlight torchlight moonlight sunlight starlight shoreline streambank riverbank treeline barkwood rootstock grassland farmland woodland orchard vineyard hedgerow flowerbed seedpod hayloft granary greenhouse beehive anthill spiderweb cobweb birdnest eggshell seashell driftwood tidepool sandbar mudbrick claypot ironbar steelbeam copperwire silverchain goldring stonewall brickwall drywall plaster limestone granite basalt marbletile claytile rooftop gardenwall fencepost gatehouse dogcart handcart pushcart"),
    (4.12, "gear brake lever handle filter channel edge frame layer stack block node flag sink tap spark flare crack scratch stain scent aroma flavor texture color shape line stripe patch ripple tremor echo glint shadow silhouette outline contour wrinkle bruise scar blister splinter shard fragment chunk clump bundle packet kernel cluster capsule tablet screen keyboard mouse speaker headset router modem antenna battery charger adapter toolkit marker crayon eraser chalk ruler compass stapler folder binder receipt invoice ticket passport ledger placard placemat coaster teacup bellrope whistleblow handprint footprint fingerprint signpost billboard guardrail railcar boxcar caboose tractor trailer forklift crane scaffold rebar footing joist conduit cabletray"),
    (3.92, "mail architecture image map pathway contour joint level signal surface marker detail memory archive snapshot footage transcript language accent melody rhythm cadence tempo gesture posture stance glare whisper odor pressurepoint pressurewave weightlessness motion blur focus angle volume pitch resonance pulse drift swell vibration shimmer warmth chill roughness smoothness hardness softness density gravity humidity dryness colorfield massing airflow runoff waveform coordinate vector matrix bitmap dataset cache packet buffer endpoint input output circuit sensor actuator motor rotor stator relay module lattice fabric seam overlap residue shadowline rim border threshold gateway portal corridor lobby atrium chamber pavilion gallery studio theater cinema arena stage aisle courtyard backyard frontyard meadowland grassfield grove thicket"),
    (3.52, "sequence pattern pressure force field pulse wave contact link schema script record file document memo draft sketch diagram chart graph table list index query command prompt signal noise stream branch root thread filter stacktrace pipeline scaffold frame shell bridge span port adapter wrapper container cluster shard mirror anchor weave backbone skeleton interface router daemon worker driver monitor logger tracker scorecard checklist brushstroke watermark headline caption subtitle thumbnail postcard leaflet flyer poster brochure handbook guidebook playbook cookbook workbook dashboard sidebar toolbar footer header navbar"),
    (3.18, "weight scale distance depth motion mass current figure profile route schedule calendar timing duration interval cycle season climate weather skyline ridgeline baseline outline overview viewpoint backdrop foreground middleground midline sideline borderline coastline watershed landmark district quarter suburb village city town county province nation region locale site scene setting atmosphere mood tenor tone strain stress load burden charge meter measure metric benchmark milestone target horizon runway transit traffic commute routing screening framing blocking mapping layering streaming filtering bridging scoping shaping balancing tracing staging seeding anchoring mirroring threading handling branching leveled"),
    (2.82, "network model trace platform service practice approach account reason response quality purpose plan idea theory policy design schema logic syntax grammar semantics narrative message claim argument stance mechanism issue concern context scope range domain capacity instance property behavior event outcome default option parameter variable constant resource asset stock reserve budget margin priority urgency probability tendency trend indicator baseline possibility plausibility doubt belief value norm premise thesis antithesis synthesis analogy metaphor symbol emblem token witness texture overlap discernibility legibility settlement topology transition regime grasp seam replay backlog workflow roadmap pipelinework channelwork stackwork scaffoldwork bridgework threadwork rootwork branchwork statechange topologychange architecturechange"),
    (2.42, "system process method strategy function state condition feature factor result effect change type framework mechanism procedure routine technique convention standard principle guideline assumption interpretation explanation comparison translation formulation distinction category family class variety version edition revision adaptation transformation configuration integration deployment delivery orchestration coordination moderation alignment negotiation analysis review summary feedback reflection planning staffing billing accounting scheduling governance management leadership ownership membership authorship partnership collaboration operation administration maintenance improvement optimization evaluation validation verification calibration estimation aggregation distribution selection classification grouping ordering ranking modeling auditing monitoring budgeting forecasting scenario constraint dependency affordance capability reliability observability usability portability extensibility interoperability determinism generality specificity"),
    (2.12, "methodology functionality modularity composability operability adjustability learnability accessibility maintainability portability readability traceability applicability viability feasibility utility purposefulness clarity ambiguity complexity simplicity precision vagueness flexibility stability resilience continuity consistency regularity normality exceptionality sensitivity specificity selectivity intensity frequency recurrence repeatability comparability similarity difference variance divergence relevance salience confidence caution attention effort labor throughput latency accuracy error defect failure success progress status update report digest abstract conclusion introduction appendix rationale discourse prose writing argumentation notation interpretation conceptualization expression representation correspondence fit mismatch paradox tensionline"),
    (1.82, "invariant recursion theorem lemma corollary proof entailment implication proposition axiom metaphysics phenomenology hermeneutics teleology modality intentionality identity alterity subjectivity objectivity duality plurality totality locality globality continuity discreteness computability decidability undecidability tractability expressivity soundness completeness consistency inconsistency equivalence isomorphism homomorphism endomorphism automorphism functor morphism category adjunction monoid monad algebra coalgebra topology geometry arithmetic calculus analysis pragmatics inference induction deduction abduction formalism abstraction generalization specialization representation interpretation individuation reification causation sufficiency necessity possibility actuality counterfactuality conceptuality ideality essence meaning truth validity coherence correspondence convergence divergence parametricity polymorphism covariance contravariance fixpoint"),
    (1.48, "grasp regime seam texture witness legibility discernible admissible promoted abstractness concreteness notion signification denotation connotation possibilityspace statespace semanticsfield relationfield distinctionfield abstractionlayer metatheory metalogic metaethics ontic epistemic deontic alethic phenomenological ontological hermeneutic teleological recursive reflective dialectical inferential categorical functorial morphic topological heuristicity reificatory individuationist coherencecheck validitycheck"),
)


def _build_norms() -> dict[str, float]:
    norms = dict(_BASE_NORMS)
    for score, words in _SCORE_GROUPS:
        _extend_words(norms, score, words)

    norms.update(
        {
            "architecture": 2.84,
            "leverages": 2.36,
            "leveraging": 2.36,
            "layered": 3.72,
            "bridges": 4.82,
            "streams": 4.58,
            "filtered": 4.18,
            "output": 2.52,
            "outputs": 2.52,
            "input": 2.52,
            "inputs": 2.52,
            "mailman": 4.90,
            "bit": 3.66,
            "tuesday": 3.12,
            "morning": 3.78,
            "red": 3.92,
            "parked": 3.92,
            "legibility": 1.76,
            "regime": 1.92,
            "grasp": 1.78,
            "morphisms": 1.52,
            "witnesses": 1.86,
            "discernible": 1.88,
            "measures": 2.28,
            "grasps": 1.78,
        }
    )
    _expand_inflections(norms, tuple(norms))
    if len(norms) < 5000:
        raise RuntimeError(f"expected at least 5000 norms, found {len(norms)}")
    return norms


NORMS: dict[str, float] = _build_norms()


_KNOWN_METAPHOR_DONOR_BASES = {
    "handle", "pipe", "pipeline", "bridge", "thread", "fork", "stream", "channel",
    "hook", "root", "branch", "tree", "leaf", "stack", "pool", "filter", "flow",
    "layer", "wire", "scaffold", "frame", "lever", "fire", "push", "pull", "cut",
    "break", "drain", "flood", "cascade", "sink", "tap", "mirror", "anchor", "seed",
    "weave", "fabric", "skeleton", "backbone", "edge", "node", "block", "path",
    "roadmap", "machinery", "engine", "gear", "route", "screen", "lens",
    "signal", "buffer", "cache", "container", "wrapper", "gateway", "portal", "corridor",
    "shell", "span", "surface", "spark", "pulse", "wave", "current", "field", "pressure",
    "load", "burden", "ladder", "stage", "backlog", "road", "rail", "track", "switch",
    "circuit", "conduit", "duct", "mesh", "lattice", "boundary", "interface", "window",
    "door", "gate", "tunnel", "steer", "align", "map", "trace", "footprint", "spine",
    "stitch", "glue", "patch", "bundle", "cluster", "shard", "fan", "funnel", "border",
}


def _expand_donor_forms(words: Iterable[str]) -> set[str]:
    donors = set(words)
    donors.discard("pipeline")
    for word in tuple(donors):
        for variant in (
            _pluralize(word),
            _past_tense(word),
            _present_participle(word),
            _comparative(word),
            _adverb(word),
        ):
            if variant and variant.isalpha():
                donors.add(variant)
    donors.update(
        {
            "handles", "handling", "pipes", "piping", "bridges", "threads", "forks", "forking",
            "streams", "streaming", "channels", "hooks", "hooking", "roots", "rooted",
            "branches", "branching", "trees", "leaves", "stacks", "stacking", "pools", "pooling",
            "filters", "filtering", "flows", "layers", "layering", "wires", "wiring", "wired",
            "scaffolding", "frames", "framing", "framed", "levers", "leverage", "leveraged",
            "fires", "firing", "fired", "pushes", "pushing", "pushed", "pulls", "pulling",
            "pulled", "cuts", "cutting", "breaks", "breaking", "drains", "draining", "drained",
            "floods", "flooding", "cascades", "cascading", "sinks", "taps", "tapping",
            "mirrors", "mirroring", "mirrored", "anchors", "anchoring", "seeds", "seeding",
            "weaves", "woven", "skeletons", "edges", "nodes", "blocks", "blocking", "blocked",
            "layered", "filtered", "streams", "channels", "bridging", "threading",
        }
    )
    return donors


KNOWN_METAPHOR_DONORS = _expand_donor_forms(_KNOWN_METAPHOR_DONOR_BASES)


def lookup_norm(word: str, norms: dict[str, float]) -> float | None:
    """Look up concreteness, stripping suffixes to find base forms."""
    if word in norms:
        return norms[word]
    suffixes = [
        ("ying", "y"), ("ying", "ie"),
        ("ies", "y"), ("ied", "y"),
        ("ness", ""), ("ment", ""), ("tion", ""), ("sion", ""),
        ("ting", "t"), ("ning", "n"), ("ping", "p"),
        ("ding", "d"), ("ging", "g"), ("ling", "l"),
        ("ming", "m"), ("ring", "r"), ("ving", "v"),
        ("zing", "z"), ("bing", "b"),
        ("lled", "l"), ("tted", "t"), ("pped", "p"),
        ("nned", "n"), ("gged", "g"), ("dded", "d"),
        ("mmed", "m"), ("rred", "r"), ("bbed", "b"),
        ("ing", "e"), ("ing", ""),
        ("ed", "e"), ("ed", ""),
        ("er", "e"), ("er", ""),
        ("es", "e"), ("es", ""),
        ("ly", ""),
        ("s", ""),
    ]
    for suffix, replacement in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            base = word[:-len(suffix)] + replacement
            if base in norms:
                return norms[base]
    return None