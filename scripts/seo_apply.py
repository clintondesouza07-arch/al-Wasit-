#!/usr/bin/env python3
"""
Batch SEO injection for Al Wasit product pages, plus sitemap.xml / robots.txt
generation. Run once from the project root:

    python3 seo_apply.py

Idempotent-ish: re-running will re-insert a fresh SEO block (old one removed
first via the marker comments) rather than duplicating tags.
"""
import re, os, glob, json, datetime

ROOT = "."
PRODUCTS_DIR = os.path.join(ROOT, "products")
DOMAIN = "https://PLACEHOLDER-DOMAIN.com"
TODAY = datetime.date.today().isoformat()

START_MARK = "<!-- BEGIN AUTO-SEO -->"
END_MARK = "<!-- END AUTO-SEO -->"

CATEGORY_RULES = [
    (["excavator-attachment"], "Excavator Attachments", "attachments"),
    (["excavator-mini", "mini-excavator"], "Mini Excavators", "excavators"),
    (["excavator"], "Excavators", "excavators"),
    (["bulldozer"], "Bulldozers", "bulldozers"),
    (["wheel-loader"], "Wheel Loaders", "loaders"),
    (["motor-grader"], "Motor Graders", "motor-graders"),
    (["roller-compactor"], "Road Rollers", "rollers"),
    (["backhoe-loader"], "Backhoe Loaders", "backhoe-loaders"),
    (["forklift"], "Forklifts", "forklifts"),
    (["transport-equipment"], "Transport Trailers", "transport"),
    (["commercial-vehicles"], "Commercial Vehicles", "commercial-vehicles"),
]

def escape_attr(s):
    return (s or "").replace('"', "&quot;")

def derive_category(slug):
    for keys, label, cat_param in CATEGORY_RULES:
        if any(k in slug for k in keys):
            return label, cat_param
    return "Heavy Equipment", "equipment"

def derive_brand(name, spec_rows):
    for k, v in spec_rows:
        if k.strip().lower() == "manufacturer":
            return v.strip()
    for token in ["AWM", "Awashi", "CAT", "Komatsu", "CAMC"]:
        if name.upper().startswith(token.upper()):
            return token
    first_word = name.split()[0]
    return first_word

def derive_condition(badge_class, badge_text):
    bt = (badge_text or "").lower()
    if "used" in bt or badge_class == "used":
        return "https://schema.org/UsedCondition"
    return "https://schema.org/NewCondition"

PRICE_RE = re.compile(r'([A-Za-z]{2,4}\$?|\$)\s?([\d,]+(?:\.\d+)?)')

def derive_price(spec_rows):
    for k, v in spec_rows:
        if "price" in k.strip().lower():
            m = PRICE_RE.search(v)
            if m:
                currency_raw, amount_raw = m.groups()
                amount = amount_raw.replace(",", "")
                currency_map = {"usd": "USD", "aed": "AED", "dhs": "AED", "$": "USD"}
                currency = currency_map.get(currency_raw.strip().lower(), None)
                if currency:
                    return currency, amount
    return None, None

def build_meta_description(name, tagline, category, brand):
    base = f"{name} — {tagline}".strip()
    tail = f" Buy or rent from Al Wasit Machinery, Sharjah UAE. {category} sales, hire, spare parts & export across the Middle East, Africa & Asia."
    desc = (base + tail)
    if len(desc) > 300:
        desc = base[:160].rsplit(" ", 1)[0] + "…" + tail
    return desc.replace('"', "'")

def process_product(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Strip any previously-injected block so re-runs don't duplicate it.
    html = re.sub(re.escape(START_MARK) + r".*?" + re.escape(END_MARK), "", html, flags=re.S)

    slug = os.path.splitext(os.path.basename(path))[0]

    title_m = re.search(r"<title>(.*?)</title>", html)
    old_title = title_m.group(1) if title_m else slug

    h1_m = re.search(r"<h1>(.*?)</h1>", html)
    name = h1_m.group(1).strip() if h1_m else old_title.split("—")[0].strip()

    sub_m = re.search(r'<p class="sub">(.*?)</p>', html)
    tagline = sub_m.group(1).strip() if sub_m else ""

    badge_m = re.search(r'<span class="badge (\w+)">(.*?)</span>', html)
    badge_class = badge_m.group(1) if badge_m else "new"
    badge_text = badge_m.group(2) if badge_m else "NEW"

    img_m = re.search(r'<img src="(\.\./images/[^"]+)" alt="([^"]*)"', html)
    img_src = img_m.group(1) if img_m else ""
    img_alt = img_m.group(2) if img_m else name
    img_abs = f"{DOMAIN}/{img_src.replace('../', '')}" if img_src else f"{DOMAIN}/icon-512.png"

    spec_rows = re.findall(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", html)
    spec_rows = [(re.sub(r"<.*?>", "", k), re.sub(r"<.*?>", "", v)) for k, v in spec_rows]

    category_label, cat_param = derive_category(slug)
    brand = derive_brand(name, spec_rows)
    condition = derive_condition(badge_class, badge_text)
    currency, amount = derive_price(spec_rows)

    canonical = f"{DOMAIN}/products/{slug}.html"
    meta_desc = build_meta_description(name, tagline, category_label, brand)
    keywords = f"{name}, {brand} {category_label.lower()}, {category_label.lower()} for sale UAE, {category_label.lower()} Sharjah, buy {category_label.lower()} Dubai, {category_label.lower()} rental UAE, Al Wasit Machinery"
    new_title = f"{name} — {category_label} in UAE | Al Wasit Machinery"
    if len(new_title) > 65:
        new_title = f"{name} | Al Wasit Machinery"

    offers_block = ""
    if currency and amount:
        offers_block = f''',
      "offers": {{
        "@type": "Offer",
        "priceCurrency": "{currency}",
        "price": "{amount}",
        "availability": "https://schema.org/InStock",
        "itemCondition": "{condition}",
        "url": "{canonical}"
      }}'''

    breadcrumb = f'''
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{DOMAIN}/alwasit-website.html"}},
        {{"@type": "ListItem", "position": 2, "name": "Equipment", "item": "{DOMAIN}/equipment.html"}},
        {{"@type": "ListItem", "position": 3, "name": "{category_label}", "item": "{DOMAIN}/equipment.html?cat={cat_param}"}},
        {{"@type": "ListItem", "position": 4, "name": "{name}", "item": "{canonical}"}}
      ]
    }}'''

    seo_block = f'''{START_MARK}
<meta name="description" content="{escape_attr(meta_desc)}"/>
<meta name="keywords" content="{escape_attr(keywords)}"/>
<meta name="robots" content="index,follow"/>
<link rel="canonical" href="{canonical}"/>
<link rel="icon" href="../favicon.ico" sizes="any"/>
<link rel="icon" href="../favicon-32.png" type="image/png" sizes="32x32"/>
<link rel="apple-touch-icon" href="../apple-touch-icon.png"/>
<meta property="og:type" content="product"/>
<meta property="og:site_name" content="Al Wasit Machinery Trading Establishment"/>
<meta property="og:title" content="{escape_attr(new_title)}"/>
<meta property="og:description" content="{escape_attr(meta_desc)}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:image" content="{img_abs}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{escape_attr(new_title)}"/>
<meta name="twitter:description" content="{escape_attr(meta_desc)}"/>
<meta name="twitter:image" content="{img_abs}"/>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Product",
      "name": "{name}",
      "image": "{img_abs}",
      "description": "{escape_attr(meta_desc)}",
      "brand": {{"@type": "Brand", "name": "{escape_attr(brand)}"}},
      "category": "{category_label}",
      "url": "{canonical}"{offers_block}
    }},{breadcrumb}
  ]
}}
</script>
<!-- Google tag (gtag.js) — TODO: replace G-XXXXXXXXXX with the real GA4 Measurement ID before launch -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
{END_MARK}
'''

    # Replace <title> with the optimized version, keep a record of the old one as a comment.
    if title_m:
        html = html.replace(title_m.group(0), f"<title>{new_title}</title>")

    # Insert the SEO block right before </head>.
    html = html.replace("</head>", seo_block + "</head>")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "slug": slug, "name": name, "category": category_label,
        "canonical": canonical, "old_title": old_title, "new_title": new_title,
    }

def main():
    results = []
    for path in sorted(glob.glob(os.path.join(PRODUCTS_DIR, "*.html"))):
        results.append(process_product(path))

    print(f"Processed {len(results)} product pages.")
    for r in results:
        print(f"  {r['slug']:55s} [{r['category']:22s}] {r['old_title']!r} -> {r['new_title']!r}")

    # ---- sitemap.xml ----
    urls = [
        (f"{DOMAIN}/alwasit-website.html", "1.0", "weekly"),
        (f"{DOMAIN}/equipment.html", "0.9", "weekly"),
    ]
    for r in results:
        urls.append((r["canonical"], "0.7", "monthly"))

    sitemap_items = "\n".join(
        f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>"""
        for loc, prio, freq in urls
    )
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_items}
</urlset>
'''
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    # ---- robots.txt ----
    robots = f'''# Al Wasit Machinery Trading Establishment
# TODO: replace PLACEHOLDER-DOMAIN.com below with the real domain once confirmed,
# then resubmit sitemap.xml in Google Search Console.

User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
'''
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    print(f"\nWrote sitemap.xml with {len(urls)} URLs and robots.txt.")

if __name__ == "__main__":
    main()
