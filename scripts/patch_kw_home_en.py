#!/usr/bin/env python3
"""Update Arabic about copy and expand English pages. Does not write Rank Math titles."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_kw_client import rest

WA = (
    '<p><a href="https://wa.me/971586634710">WhatsApp the Kuwait desk</a> · '
    '<a href="mailto:m@rukn-eltatawer.com">m@rukn-eltatawer.com</a>. '
    "Quotes are in Kuwaiti dinar after an on-site inspection.</p>"
)

AR_ABOUT = """<section>
<h2>من نحن — ركن التطور الكويت</h2>
<p>ركن التطور شركة خدمات منزلية تعمل داخل دولة الكويت: كشف تسربات المياه، عزل الأسطح والخزانات، الصيانة العامة، التكييف، السباكة والكهرباء، التنظيف، مكافحة الحشرات، تنسيق الحدائق والمسابح، والصبغ والديكورات.</p>
<p>هذه الصفحات مكتوبة لمحافظات الكويت الست، والتسعير بعد المعاينة بالدينار الكويتي. الفريق يعاين الموقع قبل التسعير، ويسلّم تقريراً يوضح المشكلة ومصدرها، ثم ينفّذ وفق نطاق مكتوب.</p>
<h3>التغطية</h3>
<p>العاصمة، حولي، الفروانية، الأحمدي، الجهراء، ومبارك الكبير. السالمية منطقة داخل حولي، والفنطاس داخل الأحمدي — ليستا محافظتين مستقلتين.</p>
<ul>
<li>تشخيص قبل التكسير أو الإصلاح.</li>
<li>عرض نطاق ومدة بالدينار الكويتي قبل البدء.</li>
<li>خدمات متعددة من جهة واحدة بدل التعامل مع عدة مقاولين.</li>
</ul>
</section>
"""

PAGES = {
    3819: """<h2>Home services across Kuwait — diagnosis before repair</h2>
<p>Rukn El Tatawer is the Kuwait branch of a regional home-services company. Work is booked in the Capital, Hawalli, Farwaniya, Ahmadi, Jahra and Mubarak Al-Kabeer. A technician sees the site before any price in Kuwaiti dinar.</p>
<h3>What we handle</h3>
<p>Water leak detection without breaking tiles first, roof and tank waterproofing, general and building maintenance, plumbing and drain clearing, electrics, AC installation and seasonal service, deep cleaning, pest control, gardens, pools, painting, gypsum and interior finishing.</p>
<h3>Kuwait, not the UAE</h3>
<p>This website is for the State of Kuwait only. We plan around local building rules, roof-tank layouts and Friday–Saturday weekends. WhatsApp reaches the Kuwait coordination desk.</p>
<h3>Governorates we cover</h3>
<ul><li><a href="/kw/en/kuwait-city/">Kuwait City (Capital)</a></li><li><a href="/kw/en/hawalli/">Hawalli</a></li><li><a href="/kw/en/farwaniya/">Farwaniya</a></li><li><a href="/kw/en/ahmadi/">Ahmadi</a></li><li><a href="/kw/en/jahra/">Jahra</a></li><li><a href="/kw/en/mubarak-al-kabeer/">Mubarak Al-Kabeer</a></li></ul>
<p>Salmiya is part of Hawalli. Fintas is part of Ahmadi. They are neighbourhoods, not extra governorates.</p>
<h3>How a job starts</h3>
<p>Send the area and a photo on WhatsApp. We book an inspection, write the scope and price, then execute. You keep one contractor instead of three separate crews.</p>
"""
    + WA,
    3821: """<h2>About Rukn El Tatawer in Kuwait</h2>
<p>We run home and building jobs inside the State of Kuwait. Neighbouring markets have their own sites. These English pages are only for Kuwait governorates, dinar pricing and local building conditions.</p>
<h3>How a visit is different</h3>
<p>A technician inspects with tools — thermal camera, moisture meter or AC gauges as needed — then you receive photos and a written scope. We do not break tiles to find a leak that could have been mapped first.</p>
<h3>Team and coverage</h3>
<p>Work is dispatched across six governorates. Coastal jobs in Hawalli and Ahmadi use materials that tolerate salt and humidity. Inland Jahra jobs allow for dust on condensers and longer pipe runs.</p>
<h3>Languages</h3>
<p>Supervisors coordinate in Arabic and English. Reports can be issued in either language on request. We do not invent ratings or a blanket guarantee on these pages; any commitment is written on the quote.</p>
"""
    + WA,
    3823: """<h2>Contact the Kuwait desk</h2>
<p>Message WhatsApp with your governorate, the service you need and a photo of the issue. We reply with an inspection window. We do not issue a firm dinar price from a phone description.</p>
<p><a href="https://wa.me/971586634710">WhatsApp Rukn El Tatawer Kuwait</a></p>
<p>Email: <a href="mailto:m@rukn-eltatawer.com">m@rukn-eltatawer.com</a></p>
<h3>Coverage</h3>
<p>Capital, Hawalli, Farwaniya, Ahmadi, Jahra and Mubarak Al-Kabeer. If you are in Salmiya we dispatch from the Hawalli route. If you are in Fintas we dispatch from the Ahmadi route.</p>
<h3>What to send</h3>
<ul><li>Area and building type (villa, apartment, shop)</li><li>A photo of the leak, unit, wall or garden</li><li>Whether children, pets or a closed shop affect the visit time</li></ul>
<p>Arabic contact page: <a href="/kw/contact-us/">اتصل بنا</a>.</p>
""",
    3825: """<h2>Privacy policy — Kuwait website</h2>
<p>This policy applies to rukn-eltatawer.com/kw/ and English pages under /kw/en/. We collect only what is needed to schedule and deliver a home-service job in Kuwait.</p>
<h3>What we collect</h3>
<p>Name, phone, area, message contents, photos you send, and technical logs (IP, browser) needed to keep the site secure.</p>
<h3>Use</h3>
<p>We use this data to reply, visit the site, issue a quote and perform the work. We do not sell personal data. Job photos stay in the job file.</p>
<h3>Retention</h3>
<p>Contact records needed for accounting stay as required by law. You may ask for correction or deletion of records that are not required for that purpose.</p>
<h3>Contact for privacy requests</h3>
<p>Email <a href="mailto:m@rukn-eltatawer.com">m@rukn-eltatawer.com</a>.</p>
"""
    + WA,
    3827: """<h2>All services — one contractor in Kuwait</h2>
<p>Pick the trade you need. Each English service page explains how the work is done under Kuwait climate and building conditions. Arabic location articles remain the detailed local guides.</p>
<h3>Service list</h3>
<ul>
<li><a href="/kw/en/services/water-leak-detection/">Water leak detection</a></li>
<li><a href="/kw/en/services/roof-insulation/">Roof insulation</a></li>
<li><a href="/kw/en/services/waterproofing/">Waterproofing and thermal insulation</a></li>
<li><a href="/kw/en/services/general-maintenance/">General home maintenance</a></li>
<li><a href="/kw/en/services/building-maintenance/">Building maintenance</a></li>
<li><a href="/kw/en/services/plumbing/">Plumbing</a></li>
<li><a href="/kw/en/services/drain-cleaning/">Drain unblocking</a></li>
<li><a href="/kw/en/services/electrical/">Electrical works</a></li>
<li><a href="/kw/en/services/ac-maintenance/">AC installation and maintenance</a></li>
<li><a href="/kw/en/services/cleaning/">Home cleaning and disinfection</a></li>
<li><a href="/kw/en/services/pest-control/">Pest control</a></li>
<li><a href="/kw/en/services/landscaping/">Garden landscaping</a></li>
<li><a href="/kw/en/services/swimming-pools/">Swimming pools</a></li>
<li><a href="/kw/en/services/painting/">Painting and decorating</a></li>
<li><a href="/kw/en/services/gypsum-board/">Gypsum board</a></li>
<li><a href="/kw/en/services/interior-design/">Interior fit-out</a></li>
</ul>
<p>These English pages summarise the trade. Neighbourhood-level Arabic pages cover the six governorates in more depth.</p>
"""
    + WA,
    3829: """<h2>Water leak detection in Kuwait</h2>
<p>We locate roof, bathroom and pipe leaks in villas and apartments before any demolition. The stain on a ceiling is often not the source.</p>
<h3>Why leaks spread fast here</h3>
<p>Roof tanks, AC condensate and coastal humidity in Hawalli and Ahmadi hide moisture inside walls. A wet patch under a window may be a tank overflow two floors up, a cracked condensate tray, or a pin-hole in a hot line. We map the path with thermal cameras and moisture meters, then hand you a photo report in Arabic or English.</p>
<h3>What a visit includes</h3>
<ul><li>Non-destructive inspection of roofs, bathrooms, kitchens and wet walls</li><li>Marked leak points and a written scope before tiling is opened</li><li>Repair options priced in KWD after diagnosis, not from a WhatsApp photo</li></ul>
<p>If the reading is dry, we say so. Opening a bathroom “just in case” is not a method. Arabic location guides start at <a href="/kw/water-leak-detection-kuwait/">كشف تسربات في العاصمة</a>.</p>
"""
    + WA,
    3831: """<h2>Roof insulation in Kuwait</h2>
<p>Polyurethane foam and membrane systems built for summers above 45°C and winter rain on flat villa roofs.</p>
<h3>Heat, tanks and flat roofs</h3>
<p>Most Kuwait homes store water on the roof. Poor insulation cooks the top floor and lets tank overflow seep into rooms. We inspect slope, existing foam, tank bases and AC stands before specifying foam, torch-on membrane or a hybrid.</p>
<p>Coverage includes chalets and industrial sheds in Ahmadi as well as Capital and Jahra villas. Foam over a wet deck fails in one season. We dry and patch first. You receive thickness, density and edge-detail on the quote — not a single-line “insulate the roof”.</p>
"""
    + WA,
    3833: """<h2>Waterproofing and thermal insulation</h2>
<p>Bathrooms, tanks, basements, balconies and facades — plus thermal coats that cut indoor heat load.</p>
<h3>Where water actually enters</h3>
<p>Expansion joints, tank rooms, balcony doors and poorly sloped roofs. We treat the wet layer, not only the paint, and we do not start until moisture readings drop.</p>
<p>Thermal paint is not a substitute for a failed membrane. We separate those two jobs on the quote so you are not paying for a white coat that hides a leak. Tank interiors and bathroom floors use different systems; mixing them is how jobs fail in the first winter rain.</p>
"""
    + WA,
    3835: """<h2>General home maintenance in Kuwait</h2>
<p>One crew for plumbing, electrics, doors, gypsum and minor civil repairs so you are not coordinating three contractors on a Friday.</p>
<p>A technician visits, lists defects with photos, and sends a KWD quote. Safety items (gas, live boards, active leaks) go first. Recurring contracts are available for villas and small buildings when you want a monthly walk-through instead of emergency-only calls.</p>
<p>We do not invent a “full villa package” price on the website. Scope depends on access, materials on site and whether the building allows weekday noise. You approve the list before anyone opens a wall.</p>
"""
    + WA,
    3837: """<h2>Building maintenance</h2>
<p>Crack repair, facade touch-ups, wet-area restoration and planned maintenance for residential buildings.</p>
<p>Typical Kuwait issues: hairline cracks from thermal movement, spalling around AC sleeves, and leaking expansion joints. We document each elevation before scaffolding or cradles go up. A single-room paint job is not a building contract.</p>
<p>Common areas, roof plant and basement pumps belong on the same log so the next visit is not a surprise. You get a photo register, not a verbal “we fixed it”. Occupied floors are scheduled around building rules, not our convenience.</p>
"""
    + WA,
    3839: """<h2>Plumbing services in Kuwait</h2>
<p>Hot and cold lines, fixtures, pumps and hidden leaks under tiles. Upper floors often show weak pressure from a shared pump, not a failed heater.</p>
<p>We isolate the stopcock before opening joints. Chemical drain openers are not a plumbing repair. After a fix we test the line with you still on site so a joint does not weep after we leave.</p>
<h3>Roof tanks and booster pumps</h3>
<p>Kuwait villas usually feed the house from a roof tank. Noisy night-time pumps, air in the hot line after a tank clean, and wet ceilings under the tank room are plumbing jobs, not “wait and see”. We quote parts after we see the pump, valves and pipe material — galvanised, PPR or copper behave differently in this climate.</p>
"""
    + WA,
    3841: """<h2>Drain unblocking</h2>
<p>Kitchen fat, bathroom hair and collapsed stacks. A slow floor drain or odour after a sandstorm is usually a line problem, not a missing perfume block.</p>
<p>We jet and camera-check. Floors open only if the pipe is collapsed. Repeat clogging in the same week means the source is still open — a broken gully, a root, or a neighbour’s stack on a shared building line.</p>
<p>Grease in villa kitchens and sand in yard drains are the two Kuwait patterns we see most. We tell you which one it is. A bottled gel poured overnight is not a diagnosis, and we will not sell you a second gel if the camera shows a sag in the pipe.</p>
"""
    + WA,
    3843: """<h2>Electrical works</h2>
<p>Distribution boards, lighting, extra sockets and fault finding under Kuwait summer AC load.</p>
<p>We isolate the circuit, test residual-current devices, and will not add load on an undersized breaker just to finish the same day. A hot socket is a visit, not a larger adaptor.</p>
<p>Peak AC load in July trips boards that looked fine in January. We measure actual draw, label circuits, and write what must wait for a board upgrade. Lighting and extra sockets are scheduled after the board is safe. We do not work live to “save time”.</p>
"""
    + WA,
    3845: """<h2>AC installation and maintenance</h2>
<p>Split and central cleaning, refrigerant charge, coil wash and seasonal contracts before the May–September peak.</p>
<p>Outdoor units on Ahmadi and Salmiya roofs take salt and dust. A proper service is coil wash, drain flush, electrical check and a written reading — not perfume in the vents. Gas is charged only after a leak check.</p>
<p>We record suction, discharge and supply temperature on the job sheet. A unit that cools the majlis but not the bedroom is often a damper, a blocked return or an undersized indoor unit — not “add gas”. Installation includes condensate routing so the next leak is not inside a gypsum bulkhead.</p>
"""
    + WA,
    3847: """<h2>Home cleaning and disinfection</h2>
<p>Deep cleaning for villas, apartments and offices: kitchens, bathrooms, floors and roof-tank rooms with materials tested on marble and wood first.</p>
<p>We schedule around building quiet hours and leave wet areas dry. Tank cleaning is a separate roof job, not a mop of the lid. Move-in and post-renovation runs follow a written room order so dust is not walked back into finished rooms.</p>
<p>Kuwait dust returns. We say what a visit will and will not hold: kitchen grease, bathroom scale and floor grit, not a promise that the house stays showroom-clean until next year. You tell us which rooms, we confirm products on marble and painted gypsum before we start.</p>
"""
    + WA,
    3849: """<h2>Pest control in Kuwait</h2>
<p>Treatment for cockroaches, ants, rodents and stored-product insects in kitchens, stores and villa yards.</p>
<p>German cockroaches live in cabinets and drains, not only the majlis. We close food, moisture and cracks before any product. You get the product name, waiting time and a follow-up visit if activity returns. We do not promise a house that never sees an insect again.</p>
<p>Yard annexes, water-tank rooms and AC drip lines are inspection points, not extras. A spray of the visible insect while the harbour stays open is how jobs bounce. Preparation (emptying lower cabinets, clearing the yard edge) is written on the appointment message so the visit is usable.</p>
"""
    + WA,
    3851: """<h2>Garden landscaping</h2>
<p>Irrigation, shade, turf and planting that survives Kuwait heat and saline water.</p>
<p>We plan drip lines, timer zones and soil replacement so the garden does not die in July. Chalets and rooftop planters on the coast get salt-tolerant specs. A pretty delivery day is not the test — the test is August.</p>
<p>Bore or tanker water, existing timers and shade from the next villa all change the design. We do not lay turf on builder’s sand and call it a garden. You receive a plant list, irrigation sketch and a watering calendar, then a follow-up after the first heat wave — not a silent handover.</p>
"""
    + WA,
    3853: """<h2>Swimming pool construction and maintenance</h2>
<p>Leak checks, tiling, pumps, sand filters and seasonal commissioning for villa and chalet pools.</p>
<p>Emptying a pool in August without covering it can crack finishes. We test structure and plumbing before recommending a refill, retile or liner. Filter media and chemistry are part of the same visit, not an afterthought.</p>
<p>Coastal chalets in Ahmadi collect salt on metal plant. Inland Jahra pools collect dust on the waterline. The same “pool service” is not the same kit. We write pump model, filter pressure and a leak-test result on the sheet. Construction quotes include shell, plant room and tiling as separate lines.</p>
"""
    + WA,
    3855: """<h2>Painting and decorating</h2>
<p>Interior and exterior painting with primers suited to dusty facades and humid bathrooms.</p>
<p>We wash, fill and spot-prime. Exterior coats are scheduled for early morning so they do not flash-dry at midday. We do not paint over an active leak stain and call the job complete.</p>
<p>Gypsum, emulsion and wet-area epoxy are different systems. You get a product name and sheen on the quote. Furniture is shifted or covered as agreed; we do not paint around a sofa and invoice a “full room”. Colour samples are viewed on site in Kuwait daylight, not only on a phone screen.</p>
"""
    + WA,
    3857: """<h2>Gypsum board installation</h2>
<p>Ceilings, bulkheads and AC pelmets in moisture-resistant boards for Kuwait bathrooms and kitchens.</p>
<p>We leave access panels at valves and never trap a leak behind a sealed ceiling. Joints are taped and sanded before paint. Lighting cut-outs are measured before the board closes.</p>
<p>False ceilings that hide condensate lines need a fall and a service hatch. A sealed pretty ceiling over a wet pipe is a second job in six months. We coordinate with the AC and electrical visits so cut-outs are not guessed after the board is hung.</p>
"""
    + WA,
    3859: """<h2>Interior fit-out</h2>
<p>Partitions, lighting layouts, built-ins and finishing coordinated with plumbing and AC.</p>
<p>Sequence matters: MEP first, finishes last, so you are not ripping new paint for a pipe. You receive drawings and a KWD bill of quantities before site works start.</p>
<p>Majlis, kitchen and wet rooms are specified separately. We do not copy a showroom photo onto a villa with a different slab height and call it design. Site measure, existing services and the building’s noise rules go on the first visit. Changes after paint starts are written as variations, not absorbed silently.</p>
"""
    + WA,
    3861: """<h2>Home services in Kuwait City (Capital)</h2>
<p>Sharq, Mirqab, Dasma, Daiya and nearby blocks. Parking and building access are agreed before the visit. Capital apartments often hide AC condensate in false ceilings; older walk-ups still run galvanised lines that weep at joints.</p>
<p>We diagnose first, then quote in KWD. Tower lifts and old mid-rise walk-ups need different equipment, so the same trade is not the same timetable. Security desks need a name and a window; we send that before we arrive.</p>
<p>Arabic guides for the Capital start at <a href="/kw/">ركن التطور الكويت</a>. English visitors use this page to book the inspection — leak detection, AC, plumbing or a general punch-list — without mixing the job with UAE copy.</p>
"""
    + WA,
    3863: """<h2>Home services in Hawalli</h2>
<p>Hawalli, Salmiya, Jabriya and Shaab. Humidity and older stacks need careful leak and AC work. Salmiya is a Hawalli district, not a seventh governorate, so dispatch follows the Hawalli route.</p>
<p>We work around tight parking and building quiet hours. Written access notes go on the job sheet. Coastal aluminium and outdoor AC units fail faster here than inland; coil wash is not optional perfume.</p>
<p>Shared stacks in apartment buildings mean a bathroom leak may belong to the neighbour above. We map that before anyone opens your tiles. Send the block, floor and a photo on WhatsApp and we reply with an inspection window, not a dinar guess.</p>
"""
    + WA,
    3865: """<h2>Home services in Farwaniya</h2>
<p>Farwaniya, Khaitan, Riggae and surrounding blocks: family villas and apartment buildings with roof tanks and shared stacks.</p>
<p>Street dust returns quickly after cleaning. Shop units often need after-hours work. Same-day visits depend on access. We still do not price unseen leaks.</p>
<p>Mixed residential-commercial streets change the noise window. A villa job and a shop shutter job are not the same crew plan. Roof-tank overflow and summer AC load are the two calls we see most. You get a photo list after inspection so the quote matches the building you actually have.</p>
"""
    + WA,
    3867: """<h2>Home services in Ahmadi</h2>
<p>Ahmadi, Fahaheel, Mahboula, Fintas and coastal chalets. Fintas is an Ahmadi district. Salt air attacks AC coils, steel and pool plant, so outdoor specs differ from Capital jobs.</p>
<p>Distances between neighbourhoods are longer than in Hawalli, so we confirm the day window rather than a vague week. Coastal-grade materials are specified for outdoor units and roof coatings. Chalet pool plant is a separate line, not a villa add-on.</p>
<p>Friday–Saturday access is common for chalets. We write that on the appointment. A WhatsApp pin is enough to start; a firm KWD figure still waits for the inspection.</p>
"""
    + WA,
    3869: """<h2>Home services in Jahra</h2>
<p>West Kuwait: larger plots, longer pipe runs and dusty outdoor units that need coil washing, not perfume.</p>
<p>Travel time is included in the appointment window you receive on WhatsApp. Yard annexes and open storage are common hiding places for pests and sand around equipment. We inspect those with the house, not as a surprise extra at the gate.</p>
<p>Bore water, long irrigation laterals and roof tanks on larger villas change plumbing and garden work. We do not copy a Salmiya apartment method onto a Jahra plot. Send the area and a photo; we answer with a visit window that already includes the drive.</p>
"""
    + WA,
    3871: """<h2>Home services in Mubarak Al-Kabeer</h2>
<p>Qurain, Adan, Abu Ftaira and nearby villas. Typical issues are roof foam, bathroom leaks and summer AC load. Yards and annexes are part of the inspection, not extras added later.</p>
<p>Parking is usually easier than in Salmiya, but dusty yards still clog outdoor units. We send a photo report after inspection so you can approve the scope before tiling opens.</p>
<p>Family villas here often mix a diwaniya, a roof tank and a small garden on one plot. We quote those as one visit with separate lines, so a leak job does not silently become a garden rebuild. Arabic neighbourhood articles remain the long guides; this page is the English booking note for the governorate.</p>
"""
    + WA,
}


def main():
    rest("/wp/v2/pages/1280", method="POST", body={"content": AR_ABOUT})
    print("OK 1280 about-us")
    for pid, html in PAGES.items():
        r = rest(f"/wp/v2/pages/{pid}", method="POST", body={"content": html})
        print(f"OK {pid} {r.get('slug')} words={len(html.split())}")


if __name__ == "__main__":
    main()
