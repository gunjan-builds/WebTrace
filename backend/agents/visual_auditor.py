import asyncio
from collections import Counter
from datetime import datetime
from pathlib import Path

from backend.agents.screenshot_highlighter import highlight_screenshot


# ---------------------------------------------------------------------------
# Shared JavaScript helpers (injected into every page.evaluate call)
# ---------------------------------------------------------------------------
JS_HELPERS = r"""
const cssPath = (el) => {
    if (!(el instanceof Element)) return '';
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && node !== document.documentElement) {
        let part = node.tagName.toLowerCase();
        if (node.id) {
            parts.unshift(part + '#' + node.id);
            break;
        }
        const parent = node.parentElement;
        if (parent) {
            const same = Array.from(parent.children).filter(c => c.tagName === node.tagName);
            if (same.length > 1) part += ':nth-of-type(' + (same.indexOf(node) + 1) + ')';
        }
        parts.unshift(part);
        node = parent;
    }
    return parts.join(' > ');
};

const rectOf = (el) => {
    const r = el.getBoundingClientRect();
    return {
        x: r.x + window.scrollX,
        y: r.y + window.scrollY,
        width: r.width,
        height: r.height
    };
};

const isVisible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 &&
        s.display !== 'none' &&
        s.visibility !== 'hidden' &&
        Number(s.opacity) > 0;
};

const accName = (el) => {
    const aria = (el.getAttribute('aria-label') || '').trim();
    if (aria) return aria;

    const labelledBy = el.getAttribute('aria-labelledby');
    if (labelledBy) {
        const t = labelledBy.split(/\s+/).map(id => {
            const n = document.getElementById(id);
            return n ? n.textContent.trim() : '';
        }).join(' ').trim();
        if (t) return t;
    }

    if (el.labels && el.labels.length) {
        const t = Array.from(el.labels).map(l => l.textContent.trim()).join(' ').trim();
        if (t) return t;
    }

    const textual = ['BUTTON', 'A', 'SUMMARY'].includes(el.tagName) ||
        el.getAttribute('role') === 'button';
    if (textual) {
        const t = (el.innerText || el.textContent || '').trim();
        if (t) return t;
    }

    if (el.tagName === 'INPUT' && ['button', 'submit', 'reset'].includes(el.type)) {
        const v = (el.value || '').trim();
        if (v) return v;
    }

    const innerImg = el.querySelector && el.querySelector('img[alt]');
    if (innerImg && innerImg.alt.trim()) return innerImg.alt.trim();

    const svgTitle = el.querySelector && el.querySelector('svg title');
    if (svgTitle && svgTitle.textContent.trim()) return svgTitle.textContent.trim();

    return (el.getAttribute('title') || '').trim();
};
"""


def _js(body):
    return "() => {\n" + JS_HELPERS + "\n" + body + "\n}"


SNAPSHOT_SCRIPT = _js(r"""
const selector = 'a, button, input:not([type="hidden"]), img, h1, h2, h3, [role="button"]';
const items = Array.from(document.querySelectorAll(selector)).slice(0, 300).map(el => {
    const tag = el.tagName.toLowerCase();
    const text = (el.innerText || el.value || el.alt || '').trim().slice(0, 40);
    const key = tag + '|' + (
        el.id || text || el.getAttribute('src') ||
        el.getAttribute('name') || cssPath(el)
    );
    return {
        key,
        tag,
        text,
        visible: isVisible(el),
        rect: rectOf(el)
    };
});

return {
    text: document.body.innerText.slice(0, 5000),
    images: Array.from(document.images).map(img => img.currentSrc || img.src),
    items
};
""")


CLS_SCRIPT = r"""
() => new Promise(resolve => {
    try {
        let total = 0;
        const observer = new PerformanceObserver(list => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) total += entry.value;
            }
        });
        observer.observe({ type: 'layout-shift', buffered: true });
        setTimeout(() => {
            observer.disconnect();
            resolve(total);
        }, 1000);
    } catch (e) {
        resolve(null);
    }
})
"""


BLOCK_PAGE_SCRIPT = r"""
() => {
    const text = ((document.title || '') + ' ' +
        (document.body ? document.body.innerText : '')).slice(0, 2500);
    const pattern = /access denied|captcha|verify you are human|are you a robot|unusual traffic|attention required|request blocked|enable javascript and cookies/i;
    return { blocked: pattern.test(text) && text.length < 1500, length: text.length };
}
"""


class VisualAuditor:
    """
    Detects UI problems on a live Playwright page.

    Findings are split into two types:
      - "bug":     real problems (JS errors, HTTP errors, broken images,
                   missing/hidden expected elements, empty buttons, overflow,
                   disappearing elements, broken links). Drawn as numbered
                   callouts on the annotated screenshot.
      - "warning": accessibility / review items (missing alt, unlabeled
                   fields, empty links, possible overlaps, dynamic changes).
                   Grouped by category; a few are drawn as small badges.
    """

    MAX_WARNING_BOXES = 12
    MAX_WARNING_BOXES_PER_CATEGORY = 4

    WARNING_CATEGORIES = {
        "image_missing_alt",
        "form_field_without_label",
        "checkbox_without_label",
        "empty_link",
        "possible_layout_overlap",
        "dynamic_content_changed",
        "element_appeared_after_reload",
        "layout_shift",
        "cumulative_layout_shift",
        "selector_check_error",
        "audit_may_be_blocked",
    }

    STEPS = {
        "javascript_error": "Open the page and check the browser console; the error is logged on load.",
        "page_http_error": "Open the page URL; the server responds with an error status.",
        "broken_image": "Open the page and scroll to the image; it shows as broken.",
        "broken_link": "Click the link on the page; the target returns an error.",
        "missing_element": "Open the page and look for the expected element; it is not present.",
        "hidden_element": "Open the page; the expected element exists but is not visible.",
        "horizontal_overflow": "Open the page and scroll sideways; content extends past the screen.",
        "empty_button": "Inspect the button; it has no text or accessible name.",
        "element_disappeared": "Open the page and wait a second; the element vanishes.",
        "element_disappeared_after_reload": "Open the page, then reload it; the element is gone.",
        "image_missing_alt": "Inspect the image element; it has no alt attribute.",
        "form_field_without_label": "Inspect the input field; it has no label or accessible name.",
        "checkbox_without_label": "Inspect the checkbox; it has no label.",
        "empty_link": "Inspect the link; it has no text or accessible name.",
        "possible_layout_overlap": "Open the page and check whether the elements cover each other.",
        "dynamic_content_changed": "Open the page and wait; content changes without interaction.",
        "element_appeared_after_reload": "Reload the page; a new element appears.",
        "layout_shift": "Open the page and watch; elements move without interaction.",
        "cumulative_layout_shift": "Open the page and watch; content jumps while loading.",
        "audit_may_be_blocked": "Open the page in a normal browser; it may show a CAPTCHA or block page to automated tools.",
    }

    def __init__(
        self,
        screenshot_dir=None,
        timeout=10000,
        observe_ms=1000,
        reload_check=True,
        max_links_to_check=25,
    ):
        self.screenshot_dir = Path(screenshot_dir or "backend/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        self.timeout = timeout
        self.observe_ms = observe_ms
        self.reload_check = reload_check
        self.max_links_to_check = max_links_to_check

        self.issues = []
        self.js_errors = []
        self.highlight_boxes = []
        self._issue_counter = 0
        self._seen = {}
        self._warning_boxes_total = 0
        self._warning_boxes_by_category = Counter()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _add_issue(
        self,
        category,
        description,
        severity="medium",
        element=None,
        evidence=None,
        confidence="high",
    ):
        """Add an issue. The same category + element is only reported once."""
        key = (category, str(element) if element is not None else description)

        if key in self._seen:
            return self._seen[key]

        self._issue_counter += 1

        issue = {
            "id": self._issue_counter,
            "type": "warning" if category in self.WARNING_CATEGORIES else "bug",
            "category": category,
            "description": description,
            "severity": severity,
            "element": element,
            "evidence": evidence,
            "confidence": confidence,
        }

        self.issues.append(issue)
        self._seen[key] = issue
        return issue

    def _highlight(self, issue, rect, label, detail=None):
        """Mark an element on the annotated screenshot."""
        if not rect or rect.get("width", 0) <= 0 or rect.get("height", 0) <= 0:
            return

        if issue["type"] == "warning":
            category = issue["category"]

            if (
                self._warning_boxes_total >= self.MAX_WARNING_BOXES
                or self._warning_boxes_by_category[category]
                >= self.MAX_WARNING_BOXES_PER_CATEGORY
            ):
                return

            self._warning_boxes_total += 1
            self._warning_boxes_by_category[category] += 1

        self.highlight_boxes.append({
            "x": rect["x"],
            "y": rect["y"],
            "width": rect["width"],
            "height": rect["height"],
            "label": label,
            "detail": detail or str(issue.get("element") or ""),
            "category": issue["category"],
            "severity": issue["severity"],
            "type": issue["type"],
            "id": issue["id"],
        })

    def _banner(self, issue, label):
        """Show a page-level bug as a ribbon above the screenshot."""
        if issue["type"] == "warning":
            return

        self.highlight_boxes.append({
            "banner": True,
            "label": label,
            "category": issue["category"],
            "severity": issue["severity"],
            "type": issue["type"],
            "id": issue["id"],
        })

    async def _safe_evaluate(self, page, script, default=None):
        try:
            return await page.evaluate(script)
        except Exception:
            return default

    # ------------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------------
    async def _check_blocked_page(self, page):
        result = await self._safe_evaluate(page, BLOCK_PAGE_SCRIPT, {})

        if result and result.get("blocked"):
            self._add_issue(
                "audit_may_be_blocked",
                "The page looks like a CAPTCHA or access-denied page, so the "
                "audit may not reflect the real website.",
                severity="medium",
                element="page",
                evidence=result,
                confidence="medium",
            )

    async def _check_missing_elements(self, page, expected_selectors):
        for selector in expected_selectors or []:
            try:
                locator = page.locator(selector)
                count = await locator.count()

                if count == 0:
                    issue = self._add_issue(
                        "missing_element",
                        f"Expected element was not found: {selector}",
                        severity="high",
                        element=selector,
                        evidence={"selector": selector},
                    )
                    self._banner(issue, f"Missing element: {selector}")
                    continue

                visible = False

                for index in range(count):
                    if await locator.nth(index).is_visible():
                        visible = True
                        break

                if not visible:
                    issue = self._add_issue(
                        "hidden_element",
                        f"Expected element exists but is not visible: {selector}",
                        severity="medium",
                        element=selector,
                        evidence={"selector": selector},
                    )
                    box = await locator.first.bounding_box()
                    if box and box["width"] > 0 and box["height"] > 0:
                        scroll = await self._safe_evaluate(
                            page,
                            "() => ({x: window.scrollX, y: window.scrollY})",
                            {"x": 0, "y": 0},
                        )
                        self._highlight(
                            issue,
                            {
                                "x": box["x"] + scroll["x"],
                                "y": box["y"] + scroll["y"],
                                "width": box["width"],
                                "height": box["height"],
                            },
                            "Hidden element",
                            detail=selector,
                        )
                    else:
                        self._banner(issue, f"Hidden element: {selector}")

            except Exception as error:
                self._add_issue(
                    "selector_check_error",
                    f"Could not check selector {selector}: {error}",
                    severity="low",
                    element=selector,
                )

    async def _check_broken_images(self, page):
        images = await self._safe_evaluate(
            page,
            _js(r"""
            return Array.from(document.images).map(img => ({
                src: img.currentSrc || img.src || '',
                alt: img.getAttribute('alt'),
                complete: img.complete,
                lazy: img.loading === 'lazy',
                naturalWidth: img.naturalWidth,
                visible: isVisible(img),
                path: cssPath(img),
                rect: rectOf(img)
            }));
            """),
            [],
        )

        for image in images:
            src = image["src"]

            # Broken image: finished loading but has no pixels.
            if src and image["complete"] and image["naturalWidth"] == 0:
                rect = image["rect"]
                tiny = rect["width"] <= 32 and rect["height"] <= 32

                issue = self._add_issue(
                    "broken_image",
                    f"Image failed to load: {src}",
                    severity="low" if tiny else "medium",
                    element=image["path"],
                    evidence={
                        "src": src,
                        "alt": image["alt"] or "",
                        "selector": image["path"],
                    },
                )
                self._highlight(
                    issue, rect, "Broken image",
                    detail="inline image" if src.startswith("data:")
                    else src.split("?")[0].rstrip("/").split("/")[-1] or src,
                )
                continue

            # Working image with no alt attribute at all (warning).
            if src and image["visible"] and image["alt"] is None:
                issue = self._add_issue(
                    "image_missing_alt",
                    f"Image has no alt attribute: {src}",
                    severity="low",
                    element=image["path"],
                    evidence={"src": src, "selector": image["path"]},
                    confidence="medium",
                )
                self._highlight(issue, image["rect"], "Image missing alt")

    async def _check_empty_buttons(self, page):
        buttons = await self._safe_evaluate(
            page,
            _js(r"""
            return Array.from(document.querySelectorAll(
                'button, input[type="button"], input[type="submit"], [role="button"]'
            )).map(el => ({
                name: accName(el),
                visible: isVisible(el),
                path: cssPath(el),
                rect: rectOf(el),
                html: el.outerHTML.slice(0, 200)
            }));
            """),
            [],
        )

        for button in buttons:
            if button["visible"] and not button["name"]:
                issue = self._add_issue(
                    "empty_button",
                    "Visible button has no detectable accessible name.",
                    severity="medium",
                    element=button["path"],
                    evidence={"html": button["html"], "selector": button["path"]},
                )
                self._highlight(issue, button["rect"], "Empty button")

    async def _check_empty_links(self, page):
        links = await self._safe_evaluate(
            page,
            _js(r"""
            return Array.from(document.querySelectorAll('a[href]')).map(el => ({
                name: accName(el),
                visible: isVisible(el),
                href: el.getAttribute('href'),
                path: cssPath(el),
                rect: rectOf(el)
            }));
            """),
            [],
        )

        for link in links:
            if link["visible"] and not link["name"]:
                issue = self._add_issue(
                    "empty_link",
                    f"Visible link has no text or accessible name: {link['href']}",
                    severity="low",
                    element=link["path"],
                    evidence={"href": link["href"], "selector": link["path"]},
                    confidence="medium",
                )
                self._highlight(issue, link["rect"], "Empty link")

    async def _check_horizontal_overflow(self, page):
        result = await self._safe_evaluate(
            page,
            _js(r"""
            const viewportWidth = document.documentElement.clientWidth;
            const viewportHeight = window.innerHeight;
            const documentWidth = document.documentElement.scrollWidth;
            const documentHeight = document.documentElement.scrollHeight;
            const offenders = [];

            if (documentWidth > viewportWidth + 5) {
                const all = document.body ? document.body.querySelectorAll('*') : [];
                for (const el of all) {
                    if (offenders.length >= 3) break;
                    if (!isVisible(el)) continue;
                    const r = el.getBoundingClientRect();
                    if (r.right > viewportWidth + 5) {
                        offenders.push(cssPath(el));
                    }
                }
            }

            return { viewportWidth, viewportHeight, documentWidth, documentHeight, offenders };
            """),
            {},
        )

        if not result:
            return

        viewport_width = result.get("viewportWidth", 0)
        document_width = result.get("documentWidth", 0)

        if document_width > viewport_width + 5:
            offenders = result.get("offenders", [])

            issue = self._add_issue(
                "horizontal_overflow",
                "Page content extends beyond the viewport horizontally.",
                severity="medium",
                element=offenders[0] if offenders else "page",
                evidence={
                    "viewportWidth": viewport_width,
                    "documentWidth": document_width,
                    "offenders": offenders,
                },
                confidence="medium",
            )

            # Mark the part of the page that sticks out past the screen edge.
            self._highlight(
                issue,
                {
                    "x": viewport_width,
                    "y": 0,
                    "width": document_width - viewport_width,
                    "height": result.get("documentHeight", 0)
                    or result.get("viewportHeight", 0),
                },
                "Horizontal overflow",
                detail=f"page {document_width}px > screen {viewport_width}px",
            )

    async def _check_layout_overlap(self, page):
        overlaps = await self._safe_evaluate(
            page,
            _js(r"""
            const elements = Array.from(document.querySelectorAll(
                'h1, h2, h3, button, input:not([type="hidden"]), img, p, a'
            )).filter(el => {
                const r = el.getBoundingClientRect();
                return r.width > 5 && r.height > 5 && isVisible(el) &&
                    !el.closest('[role="dialog"], [aria-modal="true"]');
            }).slice(0, 400);

            const results = [];

            for (let i = 0; i < elements.length && results.length < 5; i++) {
                const a = elements[i];
                const ar = a.getBoundingClientRect();

                for (let j = i + 1; j < elements.length; j++) {
                    const b = elements[j];
                    if (a.contains(b) || b.contains(a)) continue;

                    const br = b.getBoundingClientRect();
                    const width = Math.min(ar.right, br.right) - Math.max(ar.left, br.left);
                    const height = Math.min(ar.bottom, br.bottom) - Math.max(ar.top, br.top);
                    if (width <= 0 || height <= 0) continue;

                    const smaller = Math.min(ar.width * ar.height, br.width * br.height);
                    if (smaller > 0 && (width * height) / smaller > 0.65) {
                        results.push({
                            first: a.tagName.toLowerCase(),
                            second: b.tagName.toLowerCase(),
                            firstPath: cssPath(a),
                            secondPath: cssPath(b),
                            rect: rectOf(b)
                        });
                        break;
                    }
                }
            }

            return results;
            """),
            [],
        )

        for overlap in overlaps:
            issue = self._add_issue(
                "possible_layout_overlap",
                "Visible elements overlap substantially; manual review is recommended.",
                severity="low",
                element=f"{overlap['firstPath']} / {overlap['secondPath']}",
                evidence={
                    "first": overlap["first"],
                    "second": overlap["second"],
                },
                confidence="low",
            )
            self._highlight(issue, overlap["rect"], "Possible overlap")

    async def _check_form_fields(self, page):
        fields = await self._safe_evaluate(
            page,
            _js(r"""
            return Array.from(document.querySelectorAll(
                'input:not([type="hidden"]):not([type="checkbox"]):not([type="submit"]):not([type="button"]):not([type="reset"]):not([type="image"]), textarea, select'
            )).map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.type || '',
                id: el.id,
                path: cssPath(el),
                hasLabel: !!accName(el),
                hasPlaceholder: !!(el.getAttribute('placeholder') || '').trim(),
                visible: isVisible(el),
                rect: rectOf(el)
            }));
            """),
            [],
        )

        for field in fields:
            if field["visible"] and not field["hasLabel"]:
                rect = field.pop("rect")
                issue = self._add_issue(
                    "form_field_without_label",
                    "Visible form field has no detectable associated label or accessible name.",
                    severity="low",
                    element=field["path"],
                    evidence=field,
                    confidence="medium",
                )
                self._highlight(issue, rect, "Field without label")

    async def _check_checkboxes(self, page):
        checkboxes = await self._safe_evaluate(
            page,
            _js(r"""
            return Array.from(document.querySelectorAll('input[type="checkbox"]')).map(el => ({
                id: el.id,
                path: cssPath(el),
                checked: el.checked,
                disabled: el.disabled,
                hasLabel: !!accName(el),
                visible: isVisible(el),
                rect: rectOf(el)
            }));
            """),
            [],
        )

        for checkbox in checkboxes:
            if checkbox["visible"] and not checkbox["hasLabel"]:
                rect = checkbox.pop("rect")
                issue = self._add_issue(
                    "checkbox_without_label",
                    "Visible checkbox has no detectable associated label.",
                    severity="low",
                    element=checkbox["path"],
                    evidence=checkbox,
                    confidence="medium",
                )
                self._highlight(issue, rect, "Checkbox without label")

    async def _check_links(self, page):
        links = await self._safe_evaluate(
            page,
            _js(r"""
            const seen = new Set();
            const out = [];
            for (const a of document.querySelectorAll('a[href]')) {
                const href = a.href;
                if (!/^https?:/i.test(href) || seen.has(href)) continue;
                seen.add(href);
                out.push({ href, path: cssPath(a), rect: rectOf(a), visible: isVisible(a) });
            }
            return out;
            """),
            [],
        )

        for link in links[: self.max_links_to_check]:
            try:
                response = await page.request.head(link["href"], timeout=5000)

                if response.status in (403, 405, 501):
                    response = await page.request.get(link["href"], timeout=5000)

                if response.status >= 400:
                    issue = self._add_issue(
                        "broken_link",
                        f"Link returned HTTP {response.status}: {link['href']}",
                        severity="medium",
                        element=link["path"],
                        evidence={
                            "href": link["href"],
                            "status": response.status,
                        },
                    )
                    if link["visible"]:
                        self._highlight(
                            issue,
                            link["rect"],
                            "Broken link",
                            detail=f"HTTP {response.status} {link['href']}",
                        )
            except Exception:
                continue

    async def _measure_cls(self, page):
        return await self._safe_evaluate(page, CLS_SCRIPT, None)

    async def _check_dynamic_behavior(self, page):
        """
        Compares observations of the page over time:
        text/image changes, elements that disappear, elements that move
        and cumulative layout shift. Optionally reloads the page to catch
        elements that appear/disappear between loads.
        """
        before = await self._safe_evaluate(page, SNAPSHOT_SCRIPT, None)
        if not before:
            return

        cls_task = asyncio.create_task(self._measure_cls(page))
        await page.wait_for_timeout(self.observe_ms)
        after = await self._safe_evaluate(page, SNAPSHOT_SCRIPT, None)
        cls_value = await cls_task

        if not after:
            return

        # --- Text / image changes -------------------------------------
        text_changed = before["text"] != after["text"]
        images_changed = before["images"] != after["images"]

        if text_changed or images_changed:
            self._add_issue(
                "dynamic_content_changed",
                "Page text or image sources changed between observations. "
                "This may be expected behavior.",
                severity="info",
                evidence={
                    "text_changed": text_changed,
                    "images_changed": images_changed,
                },
                confidence="medium",
            )

        # --- Disappeared / moved elements ------------------------------
        before_items = {i["key"]: i for i in before["items"]}
        after_items = {i["key"]: i for i in after["items"]}

        disappeared = [
            item
            for key, item in before_items.items()
            if item["visible"]
            and (key not in after_items or not after_items[key]["visible"])
        ]

        for item in disappeared[:5]:
            issue = self._add_issue(
                "element_disappeared",
                f"Element disappeared during observation: {item['key']}",
                severity="medium",
                element=item["key"],
                evidence={"key": item["key"], "text": item["text"]},
                confidence="medium",
            )
            self._highlight(
                issue, item["rect"], "Element disappeared", detail=item["key"]
            )

        moved = []
        for key, old in before_items.items():
            new = after_items.get(key)
            if not new or not old["visible"] or not new["visible"]:
                continue

            dx = abs(new["rect"]["x"] - old["rect"]["x"])
            dy = abs(new["rect"]["y"] - old["rect"]["y"])
            dw = abs(new["rect"]["width"] - old["rect"]["width"])
            dh = abs(new["rect"]["height"] - old["rect"]["height"])

            if max(dx, dy, dw, dh) > 10:
                moved.append((old, new, max(dx, dy, dw, dh)))

        for old, new, delta in moved[:5]:
            issue = self._add_issue(
                "layout_shift",
                f"Element moved or resized by {round(delta)}px without user interaction: {old['key']}",
                severity="low",
                element=old["key"],
                evidence={"before": old["rect"], "after": new["rect"]},
                confidence="medium",
            )
            self._highlight(issue, old["rect"], "Layout shift", detail=old["key"])

        if cls_value is not None and cls_value > 0.1:
            self._add_issue(
                "cumulative_layout_shift",
                f"Cumulative Layout Shift is {cls_value:.3f} "
                "(above the 0.1 'good' threshold).",
                severity="medium" if cls_value > 0.25 else "low",
                evidence={"cls": round(cls_value, 4)},
                confidence="medium",
            )

        # --- Reload comparison -----------------------------------------
        # Avoid false positives for pages created using page.set_content().
        if (
            self.reload_check
            and page.url not in ("about:blank", "about:srcdoc")
        ):
            await self._check_reload_stability(page, after_items)

    async def _check_reload_stability(self, page, baseline_items):
        try:
            await page.reload(wait_until="load", timeout=self.timeout)
            await page.wait_for_timeout(500)
        except Exception:
            return

        reloaded = await self._safe_evaluate(page, SNAPSHOT_SCRIPT, None)
        if not reloaded:
            return

        reloaded_items = {i["key"]: i for i in reloaded["items"]}

        baseline_visible = {k for k, v in baseline_items.items() if v["visible"]}
        reloaded_visible = {k for k, v in reloaded_items.items() if v["visible"]}

        for key in sorted(baseline_visible - reloaded_visible)[:5]:
            item = baseline_items[key]
            issue = self._add_issue(
                "element_disappeared_after_reload",
                f"Element present on first load is missing after reload: {key}",
                severity="medium",
                element=key,
                evidence={"key": key, "text": item["text"]},
                confidence="medium",
            )
            self._highlight(
                issue, item["rect"], "Gone after reload", detail=key
            )

        for key in sorted(reloaded_visible - baseline_visible)[:5]:
            item = reloaded_items[key]
            self._add_issue(
                "element_appeared_after_reload",
                f"Element not present on first load appeared after reload: {key}",
                severity="low",
                element=key,
                evidence={"key": key, "text": item["text"]},
                confidence="low",
            )

    # ------------------------------------------------------------------
    # Final report shaping
    # ------------------------------------------------------------------
    @staticmethod
    def _short_detail(issue):
        """A short, human-readable detail for the legend and the report."""
        evidence = issue.get("evidence") or {}
        category = issue["category"]

        if category in ("broken_image", "image_missing_alt"):
            src = str(evidence.get("src") or "")
            if src.startswith("data:"):
                return "inline image"
            return src.split("?")[0].rstrip("/").split("/")[-1] or "image"

        if category == "page_http_error":
            return f"HTTP {evidence.get('status', '')}".strip()

        if category == "javascript_error":
            return str(evidence.get("message") or "")

        if category == "horizontal_overflow":
            return (
                f"page {evidence.get('documentWidth', '?')}px > "
                f"screen {evidence.get('viewportWidth', '?')}px"
            )

        if category in ("missing_element", "hidden_element"):
            return str(evidence.get("selector") or issue.get("element") or "")

        return str(issue.get("element") or "")

    def _finalize_issues(self, original_path, annotated_path):
        """
        - Keeps every bug as its own issue.
        - Groups warnings by category (one entry with a count).
        - Adds detail, steps_to_reproduce and screenshot evidence to each issue.
        - Renumbers ids so screenshot numbers match the report.
        Returns the legend list used by the screenshot highlighter.
        """
        bugs = [i for i in self.issues if i["type"] == "bug"]

        grouped = {}
        for issue in self.issues:
            if issue["type"] == "warning":
                grouped.setdefault(issue["category"], []).append(issue)

        final = []
        id_map = {}
        details = {}

        for issue in bugs:
            new_id = len(final) + 1
            id_map[issue["id"]] = new_id
            details[new_id] = self._short_detail(issue)
            issue["id"] = new_id
            final.append(issue)

        for category, items in grouped.items():
            first = items[0]
            new_id = len(final) + 1
            description = first["description"]

            if len(items) > 1:
                description = (
                    f"{len(items)} occurrences of "
                    f"{category.replace('_', ' ')}. "
                    f"Example: {first['description']}"
                )

            for item in items:
                id_map[item["id"]] = new_id

            details[new_id] = self._short_detail(first)

            final.append({
                "id": new_id,
                "type": "warning",
                "category": category,
                "description": description,
                "severity": first["severity"],
                "element": first["element"],
                "evidence": {
                    "count": len(items),
                    "examples": [str(i["element"]) for i in items[:5]],
                },
                "confidence": first["confidence"],
            })

        legend = []

        for issue in final:
            issue["detail"] = details.get(issue["id"], "")
            issue["steps_to_reproduce"] = self.STEPS.get(
                issue["category"],
                "Open the page and review the highlighted area.",
            )
            issue["screenshot"] = original_path
            issue["annotated_screenshot"] = annotated_path

            count = 1
            if issue["type"] == "warning":
                count = (issue.get("evidence") or {}).get("count", 1)

            legend.append({
                "id": issue["id"],
                "type": issue["type"],
                "category": issue["category"],
                "severity": issue["severity"],
                "count": count,
                "detail": issue["detail"],
            })

        for box in self.highlight_boxes:
            box["id"] = id_map.get(box.get("id"), box.get("id"))

        self.issues = final
        return legend

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    async def audit_page(
        self,
        page,
        expected_selectors=None,
        js_errors=None,
        check_links=False,
        page_status=None,
    ):
        """Never raises: always returns a valid result dictionary."""
        try:
            return await self._audit_page_impl(
                page, expected_selectors, js_errors, check_links, page_status
            )
        except Exception as error:
            return {
                "agent": "Visual Auditor",
                "status": "error",
                "error": str(error),
                "page_url": getattr(page, "url", ""),
                "issues_found": 0,
                "bugs_found": 0,
                "warnings_found": 0,
                "issues": [],
                "summary": {"by_severity": {}, "by_category": {}},
                "javascript_errors": [],
                "screenshot": None,
                "annotated_screenshot": None,
            }

    async def _audit_page_impl(
        self,
        page,
        expected_selectors=None,
        js_errors=None,
        check_links=False,
        page_status=None,
    ):
        self.issues = []
        self.highlight_boxes = []
        self.js_errors = list(js_errors or [])
        self._issue_counter = 0
        self._seen = {}
        self._warning_boxes_total = 0
        self._warning_boxes_by_category = Counter()

        def on_page_error(error):
            message = str(error)
            if message not in self.js_errors:
                self.js_errors.append(message)

        page.on("pageerror", on_page_error)

        try:
            # 0. Let the page settle (heavy sites keep loading after "load").
            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass

            # 1. Page-level HTTP error
            if page_status is not None and page_status >= 400:
                issue = self._add_issue(
                    "page_http_error",
                    f"Page returned HTTP status {page_status}.",
                    severity="high",
                    element="page",
                    evidence={"status": page_status, "url": page.url},
                )
                self._banner(issue, f"HTTP ERROR: {page_status}")

            # 2. Static checks (positions match the screenshot taken below)
            await self._check_blocked_page(page)
            await self._check_missing_elements(page, expected_selectors)
            await self._check_broken_images(page)
            await self._check_empty_buttons(page)
            await self._check_empty_links(page)
            await self._check_horizontal_overflow(page)
            await self._check_layout_overlap(page)
            await self._check_form_fields(page)
            await self._check_checkboxes(page)

            if check_links:
                await self._check_links(page)

            # 3. Screenshot BEFORE the dynamic phase (which may reload the page)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            original_path = self.screenshot_dir / f"audit_{timestamp}.png"
            annotated_path = self.screenshot_dir / f"audit_{timestamp}_annotated.png"

            try:
                await page.screenshot(path=str(original_path), full_page=True)
            except Exception:
                await page.screenshot(path=str(original_path), full_page=False)

            device_scale = await self._safe_evaluate(
                page, "() => window.devicePixelRatio || 1", 1
            )

            # 4. Dynamic behavior checks
            await self._check_dynamic_behavior(page)

            # 5. JavaScript errors (includes errors raised during reload)
            for error in self.js_errors:
                issue = self._add_issue(
                    "javascript_error",
                    f"JavaScript runtime error: {error}",
                    severity="high",
                    element=error[:120],
                    evidence={"message": error},
                )
                self._banner(issue, f"JS ERROR: {error[:100]}")

            # 6. Group warnings, add evidence + steps, renumber ids
            legend = self._finalize_issues(
                original_path.as_posix(), annotated_path.as_posix()
            )

            # 7. Annotated screenshot (numbered callouts + legend)
            highlight_screenshot(
                input_path=str(original_path),
                output_path=str(annotated_path),
                boxes=self.highlight_boxes,
                scale=device_scale or 1,
                legend=legend,
                subtitle=page.url,
            )

            return {
                "agent": "Visual Auditor",
                "status": "completed",
                "page_url": page.url,
                "issues_found": len(self.issues),
                "bugs_found": sum(1 for i in self.issues if i["type"] == "bug"),
                "warnings_found": sum(
                    1 for i in self.issues if i["type"] == "warning"
                ),
                "issues": self.issues,
                "summary": {
                    "by_severity": dict(
                        Counter(i["severity"] for i in self.issues)
                    ),
                    "by_category": dict(
                        Counter(i["category"] for i in self.issues)
                    ),
                },
                "javascript_errors": self.js_errors,
                "screenshot": original_path.as_posix(),
                "annotated_screenshot": annotated_path.as_posix(),
            }

        finally:
            page.remove_listener("pageerror", on_page_error)