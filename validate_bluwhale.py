import urllib.request, re

url_html = 'http://127.0.0.1:8000/chat'
url_css  = 'http://127.0.0.1:8000/static/style.css'
url_js   = 'http://127.0.0.1:8000/static/app.js'

def chk(label, cond):
    status = "PASS" if cond else "FAIL"
    print("  [" + status + "] " + label)

try:
    html = urllib.request.urlopen(url_html, timeout=5).read().decode('utf-8')
    css  = urllib.request.urlopen(url_css,  timeout=5).read().decode('utf-8')
    js   = urllib.request.urlopen(url_js,   timeout=5).read().decode('utf-8')

    print("=== HTML CHECKS ===")
    title = re.search(r'<title>(.*?)</title>', html)
    print("  Title: " + (title.group(1) if title else "NOT FOUND"))
    chk("BluWhale branding in HTML", "BluWhale" in html)
    chk("No 'Deneb AI' text remains", "deneb AI" not in html and "Deneb AI" not in html)
    chk("Whale SVG logo (logo-whale class)", "logo-whale" in html)
    chk("No robot fa-robot icon in static HTML", "fa-solid fa-robot" not in html)
    chk("wand-magic-sparkles icon for Assistants btn", "wand-magic-sparkles" in html)
    chk("fa-microchip icon replaces robot in badge", "fa-microchip" in html)
    chk("Welcome BluWhale AI Workspace message", "BluWhale AI Workspace" in html)
    chk("welcome-whale-icon div present", "welcome-whale-icon" in html)
    chk("welcome-whale-svg class present", "welcome-whale-svg" in html)

    print("")
    print("=== CSS CHECKS ===")
    chk("--radius-lg: 12px (curved corners)", "--radius-lg: 12px" in css)
    chk("--radius-md: 8px", "--radius-md: 8px" in css)
    chk("--radius-sm: 6px", "--radius-sm: 6px" in css)
    chk("backdrop-filter glassmorphism effect", "backdrop-filter" in css)
    chk("whaleBob keyframe animation", "whaleBob" in css)
    chk("oceanShimmer background animation", "oceanShimmer" in css)
    chk("pulse animation for online dot", "@keyframes pulse" in css)
    chk("Glossy send button shimmer (::before)", "btn-send-console::before" in css)
    chk("accent-amber for folder icons", "accent-amber" in css)
    chk("accent-teal for canvas/source badges", "accent-teal" in css)
    chk("accent-sky for active highlights", "accent-sky" in css)
    chk("accent-green for online status", "accent-green" in css)
    chk("Steel Blue #3a7ca5 (primary)", "#3a7ca5" in css)
    chk("Yale Blue #16425b (dark bg)", "#16425b" in css)
    chk("Dust Grey #d9dcd6 (light mode)", "#d9dcd6" in css)
    chk("Sky Blue #81c3d7", "#81c3d7" in css)
    chk("Baltic Blue #2f6690 (borders)", "#2f6690" in css)
    chk("Gradient text brand-ai", "-webkit-background-clip: text" in css)
    chk("welcome-whale-icon animation styling", "welcome-whale-icon" in css)
    chk("Box-shadow glow effects", "--shadow-glow" in css)
    chk("Tab btn active gradient", ".tab-btn.active" in css)

    print("")
    print("=== JS CHECKS ===")
    chk("bluwhale_theme localStorage key", "bluwhale_theme" in js)
    chk("No old deneb_theme key", "deneb_theme" not in js)
    chk("bluwhale_app_key localStorage", "bluwhale_app_key" in js)
    chk("No old deneb_app_key", "deneb_app_key" not in js)
    chk("bluwhale_artifact download filename", "bluwhale_artifact" in js)
    chk("Whale SVG injected dynamically", "ellipse cx" in js)
    chk("No fa-robot in resetChatWorkspace", "fa-solid fa-robot" not in js)
    chk("BluWhale AI Workspace welcome in JS", "BluWhale AI Workspace" in js)
    chk("welcome-whale-icon in JS template", "welcome-whale-icon" in js)

    print("")
    print("=== ALL VALIDATION COMPLETE ===")

except Exception as e:
    print("ERROR connecting to server: " + str(e))
