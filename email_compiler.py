#!/usr/bin/env python3
"""
SEB Email Template Compiler
Compiles Handlebars-style templates to HTML + plain text for deliverability.
"""

import re
import os
import json
from html import unescape as html_unescape
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

try:
    import pystache
except ImportError:
    pystache = None

TEMPLATE_DIR = Path(__file__).parent / "email_templates"
BASE_TEMPLATE = TEMPLATE_DIR / "base.html"


def read_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_partials(content: str) -> Dict[str, str]:
    """Extract {{#>partial}} blocks from template."""
    partials = {}
    pattern = r'\{\{#>([\w_]+)\}\}(.*?)\{\{/>\1\}\}'
    for match in re.finditer(pattern, content, re.DOTALL):
        partials[match.group(1)] = match.group(2).strip()
    return partials


def extract_inline_partials(content: str) -> Dict[str, str]:
    """Extract {{#*inline "name"}} ... {{/inline}} blocks."""
    partials = {}
    pattern = r'\{\{#\*inline\s+"([^"]+)"\}\}(.*?)\{\{/inline\}\}'
    for match in re.finditer(pattern, content, re.DOTALL):
        partials[match.group(1)] = match.group(2).strip()
    return partials


def flatten_context(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten nested dicts into dotted keys, e.g. {'cta': {'url': x}} -> {'cta.url': x}."""
    flat: Dict[str, Any] = {}
    for key, value in data.items():
        dotted = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(flatten_context(value, prefix=f"{dotted}."))
        else:
            flat[dotted] = value
    return flat


def lookup(context: Dict[str, Any], key: str) -> Any:
    """Resolve a possibly dotted key ('cta.secondary.url') against a context dict."""
    current: Any = context
    for part in key.split('.'):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
        if current is None:
            return None
    return current


def html_to_text(html: str) -> str:
    """Convert HTML email to plain text version."""
    # Drop HTML comments first — this includes MSO conditional blocks
    # (<!--[if mso]> ... <o:PixelsPerInch>96</o:PixelsPerInch> ... <![endif]-->),
    # whose contents would otherwise leak into the plain-text part.
    text = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    text = re.sub(r'<xml[^>]*>.*?</xml>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove style and script tags
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Convert common tags
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>', '  \u2022 ', text, flags=re.IGNORECASE)
    text = re.sub(r'</ul>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<ul[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</ol>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<ol[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<h[1-6][^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</h[1-6]>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<strong[^>]*>|<b[^>]*>', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'</strong>|</b>', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'<code[^>]*>', '`', text, flags=re.IGNORECASE)
    text = re.sub(r'</code>', '`', text, flags=re.IGNORECASE)
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', r'\2 (\1)', text, flags=re.IGNORECASE)
    text = re.sub(r'<div[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<span[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</span>', '', text, flags=re.IGNORECASE)

    # Remove remaining tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities (the previous hard-coded replacements were no-ops:
    # e.g. text.replace('&', '&') — the entity literals had been eaten already).
    text = html_unescape(text)
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u2019', "'")
    text = text.replace('\u2018', "'")

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.strip()

    return text


class SEBEmailCompiler:
    """Compile SEB email templates to HTML + plain text."""

    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir or TEMPLATE_DIR
        self.base_template = read_template(self.template_dir / "base.html")
        self.partials = self._load_partials()

    def _load_partials(self) -> Dict[str, str]:
        partials = {}
        # Extract partials from base template
        base_partials = extract_partials(self.base_template)
        partials.update(base_partials)

        # Extract inline partials from all template files
        for tmpl_file in self.template_dir.glob("*.html"):
            if tmpl_file.name == "base.html":
                continue
            content = read_template(tmpl_file)
            inline = extract_inline_partials(content)
            partials.update(inline)
        return partials

    def render(self, template_name: str, context: Dict[str, Any]) -> Tuple[str, str]:
        """
        Render a template to (html, text).
        template_name: e.g., "outreach_authorized" (without .html)
        """
        template_path = self.template_dir / f"{template_name}.html"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        template_content = read_template(template_path)

        # Build full context with defaults
        full_context = {
            "year": datetime.now().year,
            "unsubscribe_url": "https://seb.security/unsubscribe",
            "subject": context.get("subject", "SEB Security — Free AI risk assessment"),
            **context,
        }

        # Generate preheader if not provided
        if "preheader" not in full_context:
            full_context["preheader"] = self._generate_preheader(context)

        # Render body partial
        body_match = re.search(r'\{\{#\*inline\s+"body"\}\}(.*?)\{\{/inline\}\}', template_content, re.DOTALL)
        if not body_match:
            raise ValueError(f"No body partial found in {template_name}")

        body_html = body_match.group(1).strip()

        # Compile base template with body partial.
        # NOTE: pystache 0.6.8's Renderer.render() ignores the 3rd positional
        # `partials` argument — partials must be passed to the Renderer ctor.
        if pystache:
            all_partials = {**self.partials, "body": body_html}
            renderer = pystache.Renderer(partials=all_partials)
            html = renderer.render(self.base_template, full_context)
        else:
            # Simple fallback
            html = self.base_template
            for name, content in {**self.partials, "body": body_html}.items():
                html = html.replace(f'{{{{> {name}}}}}', content)
            for key, value in full_context.items():
                if isinstance(value, (str, int, float)):
                    html = html.replace(f'{{{{ {key} }}}}', str(value))

        # Final pass for any remaining variables
        for key, value in full_context.items():
            if isinstance(value, (str, int, float)):
                html = html.replace(f'{{{{ {key} }}}}', str(value))

        # Handle conditional blocks (simplified)
        html = self._process_conditionals(html, full_context)

        # Generate plain text
        text = html_to_text(html)

        return html, text

    def _generate_preheader(self, context: Dict[str, Any]) -> str:
        """Generate preheader text from context."""
        if "company" in context:
            return f"Free AI risk snapshot for {context['company']} \u2014 no scan without your OK"
        return "SEB Security \u2014 Free AI risk assessment (no scan without your OK)"

    def _process_conditionals(self, html: str, context: Dict[str, Any]) -> str:
        """Process {{#if}} and {{#each}} blocks (simplified)."""
        # {{#if condition}}...{{/if}}
        def replace_if(match):
            condition = match.group(1).strip()
            content = match.group(2)
            val = context.get(condition)
            if val and (not isinstance(val, list) or len(val) > 0):
                return content
            return ""

        html = re.sub(r'\{\{#if\s+([^}]+)\}\}(.*?)\{\{/if\}\}', replace_if, html, flags=re.DOTALL)

        # {{#each items}}...{{/each}}
        def replace_each(match):
            items_key = match.group(1).strip()
            content = match.group(2)
            items = context.get(items_key, [])
            if not isinstance(items, list):
                return ""
            result = []
            for item in items:
                item_html = content
                if isinstance(item, dict):
                    for k, v in item.items():
                        item_html = item_html.replace(f'{{{{ {k} }}}}', str(v))
                else:
                    item_html = item_html.replace('{{ this }}', str(item))
                result.append(item_html)
            return ''.join(result)

        html = re.sub(r'\{\{#each\s+([^}]+)\}\}(.*?)\{\{/each\}\}', replace_each, html, flags=re.DOTALL)

        return html


def compile_all_templates(output_dir: Optional[Path] = None) -> Dict[str, Dict[str, str]]:
    """Compile all outreach templates."""
    compiler = SEBEmailCompiler()
    templates = {
        "outreach_authorized": "Authorized prospect outreach (inbound)",
        "outreach_optin": "Cold opt-in invitation",
        "outreach_inbound": "Post-authorization next steps",
    }

    results = {}
    for name, desc in templates.items():
        try:
            test_context = {
                "first_name": "Alex",
                "company": "CK Catalyst",
                "target_domain": "ckcatalyst.ca",
                "auth_date": "2026-07-22",
                "intake_url": "https://seb.security/intake?company=CK+Catalyst",
                "scope": [
                    "Public chatbot at ckcatalyst.ca/api only",
                    "OWASP LLM Top-10 automated probing",
                    "Third-party platforms (Intercom, etc.) excluded",
                    "No data exfiltration, no DoS",
                ],
                "cta": {
                    "url": "https://seb.security/intake?company=CK+Catalyst",
                    "text": "Get my free risk snapshot",
                },
                "auth_badge": True,
                "auth_date": "2026-07-22",
            }

            html, text = compiler.render(name, test_context)
            results[name] = {"html": html, "text": text, "description": desc}

            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / f"{name}.html").write_text(html, encoding="utf-8")
                (output_dir / f"{name}.txt").write_text(text, encoding="utf-8")

        except Exception as e:
            results[name] = {"error": str(e), "description": desc}

    return results


if __name__ == "__main__":
    # Quick test compile
    results = compile_all_templates(Path("/c/Users/mbapt/src/seb/email_templates/compiled"))
    for name, result in results.items():
        if "error" in result:
            print(f"\u274c {name}: {result['error']}")
        else:
            print(f"\u2705 {name} ({result['description']})")
            print(f"   HTML: {len(result['html'])} chars")
            print(f"   Text: {len(result['text'])} chars")