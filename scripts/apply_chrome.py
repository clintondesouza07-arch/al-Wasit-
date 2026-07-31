#!/usr/bin/env python3
"""
Swaps the minimal .pnav / .pfoot on every product page for the fuller
site-wide header (announcement bar + full nav + mobile menu + breadcrumb)
and footer (footer-top columns + footer-bottom), matching alwasit-website.html.
Safe to re-run: matches the exact old blocks and replaces them wholesale.
"""
import re, glob, sys

OLD_NAV = '<nav class="pnav"><div class="container"><a class="brand" href="../alwasit-website.html">AL<span>WASIT</span> MACHINERY</a>\n<a class="back" href="../equipment.html">← Back to all equipment</a></div></nav>'

NEW_HEADER = '''<div class="ann-bar"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;color:var(--orange);margin-right:2px;"><path d="M8 21h8M12 17v4M7 4h10v4a5 5 0 0 1-10 0V4z"/><path d="M7 5H4a1 1 0 0 0-1 1 5 5 0 0 0 4 4.9M17 5h3a1 1 0 0 1 1 1 5 5 0 0 1-4 4.9"/></svg> <span>40+ Years</span> of Heavy Equipment Excellence &nbsp;|&nbsp; Serving <span>30+ Countries</span> Across the Middle East, Africa &amp; Asia &nbsp;|&nbsp; <a href="tel:+97165334912" style="color:var(--orange);font-weight:700;">+971 6 5334912</a></div>
<nav class="pnav" id="navbar">
  <div class="container nav-inner">
    <a class="brand" href="../alwasit-website.html">AL<span>WASIT</span> MACHINERY</a>
    <ul class="nav-links">
      <li><a href="../equipment.html" class="active">Equipment</a></li>
      <li><a href="../alwasit-website.html#about">Our Story</a></li>
      <li><a href="../alwasit-website.html#industries">Industries</a></li>
      <li><a href="../alwasit-website.html#services">Services</a></li>
      <li><a href="../alwasit-website.html#contact">Contact</a></li>
    </ul>
    <div class="nav-cta">
      <div class="nav-phone">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1-9.4 0-17-7.6-17-17 0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/></svg>
        +971 6 5334912
      </div>
      <a href="../alwasit-website.html#quote" class="btn btn-primary">Get a Quote</a>
    </div>
    <div class="hamburger" id="hamburger"><span></span><span></span><span></span></div>
  </div>
  <div class="mobile-menu" id="mobileMenu">
    <a href="../equipment.html">Equipment</a>
    <a href="../alwasit-website.html#about">Our Story</a>
    <a href="../alwasit-website.html#industries">Industries</a>
    <a href="../alwasit-website.html#services">Services</a>
    <a href="../alwasit-website.html#contact">Contact</a>
    <a href="../alwasit-website.html#quote" class="btn btn-primary">Get a Quote</a>
  </div>
</nav>
<div class="pbreadcrumb container"><a class="back" href="../equipment.html">← Back to all equipment</a></div>'''

OLD_FOOTER_RE = re.compile(
    r'<footer class="pfoot"><div class="container">Al Wasit Machinery Trading Establishment.*?</div></footer>',
    re.S
)

NEW_FOOTER = '''<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <a class="brand" href="../alwasit-website.html">AL<span>WASIT</span> MACHINERY</a>
        <p>Established in 1985, Al Wasit Machinery Trading Establishment is the Middle East's most trusted heavy equipment partner — serving 30+ countries with integrity, expertise and an unmatched inventory.</p>
        <div class="footer-social">
          <a href="#" class="soc" title="LinkedIn"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.03-1.85-3.03-1.86 0-2.15 1.45-2.15 2.94v5.66H9.35V9h3.41v1.56h.05c.47-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z"/></svg></a>
          <a href="#" class="soc" title="Facebook"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 21v-8.15h2.73l.41-3.17h-3.14V7.7c0-.92.25-1.54 1.57-1.54h1.68V3.34C16.44 3.24 15.4 3.15 14.2 3.15c-2.5 0-4.22 1.53-4.22 4.34v2.34H7.24v3.17h2.74V21h3.52z"/></svg></a>
          <a href="#" class="soc" title="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1"/></svg></a>
          <a href="#" class="soc" title="YouTube"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 12s0-3.2-.4-4.7a3 3 0 0 0-2.1-2.1C17.9 4.8 12 4.8 12 4.8s-5.9 0-7.5.4A3 3 0 0 0 2.4 7.3C2 8.8 2 12 2 12s0 3.2.4 4.7a3 3 0 0 0 2.1 2.1c1.6.4 7.5.4 7.5.4s5.9 0 7.5-.4a3 3 0 0 0 2.1-2.1c.4-1.5.4-4.7.4-4.7zM10 15.2V8.8L15.5 12 10 15.2z"/></svg></a>
          <a href="#" class="soc" title="X / Twitter"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 3H22l-7.2 8.2L23 21h-6.6l-5.2-6.4L5.2 21H2l7.7-8.8L1.5 3h6.8l4.7 5.9L18.9 3zM17.7 19h1.8L7.4 5H5.5L17.7 19z"/></svg></a>
        </div>
      </div>
      <div class="footer-col">
        <h5>Equipment</h5>
        <a href="../equipment.html?cat=excavators">Excavators</a>
        <a href="../equipment.html?cat=bulldozers">Bulldozers</a>
        <a href="../equipment.html?cat=loaders">Wheel Loaders</a>
        <a href="../equipment.html?cat=motor-graders">Motor Graders</a>
        <a href="../equipment.html?cat=rollers">Road Rollers</a>
        <a href="../equipment.html?cat=commercial-vehicles">Commercial Vehicles</a>
        <a href="../equipment.html?cat=attachments">Attachments</a>
      </div>
      <div class="footer-col">
        <h5>Company</h5>
        <a href="../alwasit-website.html#about">Our Story</a>
        <a href="../alwasit-website.html#industries">Industries</a>
        <a href="../alwasit-website.html#services">Services</a>
        <a href="../alwasit-website.html#contact">Contact Us</a>
        <a href="../alwasit-website.html#news">News &amp; Insights</a>
      </div>
      <div class="footer-col">
        <h5>Contact</h5>
        <a href="tel:+97165334912">+971 6 5334912</a>
        <a href="mailto:alwasit@alwasit.com">alwasit@alwasit.com</a>
        <a href="https://maps.google.com/?q=Industrial+Area+Sharjah+UAE" target="_blank" rel="noopener">P.O. Box 40258, Industrial Area, Sharjah, UAE</a>
        <a href="../alwasit-website.html#quote">Request a Quote</a>
        <a href="https://wa.me/97165334912" target="_blank">WhatsApp Us</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 Al Wasit Machinery Trading Establishment. All rights reserved.</span>
      <div class="footer-cert">
        <span class="cert-badge">EST. 1985</span>
        <span class="cert-badge">30+ COUNTRIES</span>
      </div>
    </div>
  </div>
</footer>'''

def main():
    files = sorted(glob.glob("products/*.html"))
    nav_hits, foot_hits = 0, 0
    problems = []
    for path in files:
        html = open(path, encoding="utf-8").read()

        if OLD_NAV in html:
            html = html.replace(OLD_NAV, NEW_HEADER)
            nav_hits += 1
        else:
            problems.append((path, "nav block not found/changed"))

        new_html, n = OLD_FOOTER_RE.subn(NEW_FOOTER, html)
        if n == 1:
            html = new_html
            foot_hits += 1
        else:
            problems.append((path, f"footer replace count={n}"))

        open(path, "w", encoding="utf-8").write(html)

    print(f"Files: {len(files)}  nav replaced: {nav_hits}  footer replaced: {foot_hits}")
    for p in problems:
        print("PROBLEM:", p)

if __name__ == "__main__":
    main()
