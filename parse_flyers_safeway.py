#!/usr/bin/env python3
# parse_flyers_safeway.py - Safeway-specific flyer parser
import sys, json, argparse, base64, glob
from pathlib import Path
from typing import List, Dict
import anthropic


def pdf_to_base64(pdf_path: Path) -> str:
    return base64.standard_b64encode(pdf_path.read_bytes()).decode("utf-8")


def extract_deals_with_ai(pdf_path: Path, api_key: str) -> List[Dict]:
    client = anthropic.Anthropic(api_key=api_key)
    pdf_data = pdf_to_base64(pdf_path)

    prompt = """Extract ALL grocery deals from this Safeway flyer PDF. 

     STEP 1: Identify each product and its associated deal
     - Look at EACH product individually
     - Find the price badge/text DIRECTLY ON or IMMEDIATELY NEXT TO that specific product
     - Ignore deals from other products nearby

     STEP 2: Extract these fields for each item:
     - item: Product name (without size info)
     - sale_price: Sale price as number (or null)
     - reg_price: Regular price as number (or null)
     - unit: Unit like LB, EA (or null)
     - size: Package size like "32oz", "3ct", "16oz", "2lb" (or null)
     - deal_type: "BOGO", "multi_buy", "regular", or null

     STEP 3: Calculate prices based on deal type:

     BOGO deals ("BUY X GET X FREE"):
     - If prices shown: sale_price = reg_price ÷ 2
     - If NO prices shown: sale_price = null, reg_price = null
     - deal_type = "BOGO"

     Multi-buy deals ("X for $Y"):
     - Calculate: sale_price = Y ÷ X
     - "4 for $5" → 5 ÷ 4 = 1.25
     - "3 for $12" → 12 ÷ 3 = 4.00
     - "2 for $6" → 6 ÷ 2 = 3.00
     - deal_type = "multi_buy"

     Regular deals:
     - Use the member price shown
     - deal_type = "regular"

     STEP 4: Return valid JSON only, no markdown

     [
       {"item": "Soup", "sale_price": 1.25, "reg_price": null, "unit": "EA", "size": "10oz", "deal_type": "multi_buy"},
       {"item": "Chips BOGO", "sale_price": null, "reg_price": null, "unit": "EA", "size": "8oz", "deal_type": "BOGO"}
     ]"""

    print(f"  Sending to API...")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=15000,  # Higher for Safeway's larger flyers
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {"type": "text", "text": prompt}
            ],
        }]
    )

    print(f"  Received response, parsing...")

    response_text = message.content[0].text.strip()

    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    if not response_text.endswith(']'):
        last_complete = response_text.rfind('},')
        if last_complete > 0:
            response_text = response_text[:last_complete + 1] + ']'
            print(f"  ⚠ Response was truncated, recovered {response_text.count('{')} items")

    response_text = response_text.replace(",]", "]").replace(",}", "}")

    deals = json.loads(response_text)

    # Fix decimal formatting
    for deal in deals:
        if deal.get('sale_price'):
            deal['sale_price'] = round(float(deal['sale_price']), 2)
        if deal.get('reg_price'):
            deal['reg_price'] = round(float(deal['reg_price']), 2)
        deal['store'] = 'Safeway'

    return deals


def main():
    ap = argparse.ArgumentParser(description="Extract Safeway deals using AI")
    ap.add_argument("pdfs", nargs="+", help="PDF flyer paths")
    ap.add_argument("--api-key", required=True, help="Anthropic API key")
    ap.add_argument("--outdir", default="out_safeway", help="Output directory")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    all_pdfs = []
    for pattern in args.pdfs:
        matches = glob.glob(pattern)
        all_pdfs.extend(matches if matches else [pattern])

    all_deals = []
    for pdf_file in all_pdfs:
        pdf_path = Path(pdf_file)
        if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
            print(f"Skipping {pdf_path}")
            continue

        print(f"Processing {pdf_path}...")
        try:
            deals = extract_deals_with_ai(pdf_path, args.api_key)
            print(f"  ✓ Found {len(deals)} items")
            all_deals.extend(deals)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

    if not all_deals:
        print("\nNo deals extracted!")
        return

    # Fix typos and add missing fields before writing
    for deal in all_deals:
        # Fix the "save_price" typo that appeared in one item
        if 'save_price' in deal:
            deal['sale_price'] = deal.pop('save_price')
        # Add deal_type if missing
        if 'deal_type' not in deal:
            deal['deal_type'] = None

    out_json = outdir / "deals_safeway.json"
    out_json.write_text(json.dumps(all_deals, indent=2), encoding="utf-8")
    print(f"\nWrote {out_json} ({len(all_deals)} items)")

    import csv
    out_csv = outdir / "deals_safeway.csv"
    with out_csv.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, ['store', 'item', 'size', 'unit', 'sale_price', 'reg_price', 'deal_type'])
        w.writeheader()
        w.writerows(all_deals)
    print(f"Wrote {out_csv}")

    # Generate HTML
    out_html = outdir / "index_safeway.html"
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>SlugSaver - Safeway</title>
<style>body{{font-family:system-ui;margin:24px}}input{{width:100%;padding:10px;font-size:16px}}
table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{padding:8px;border-bottom:1px solid #eee;text-align:left}}
th{{background:#fafafa}}.badge{{background:#ff6b6b;color:white;padding:2px 6px;border-radius:6px;font-size:12px}}</style>
</head><body><h1>SlugSaver - Safeway Deals</h1><input id="q" placeholder="Search..." autofocus/>
<table><thead><tr><th>Item</th><th>Size</th><th>Sale</th><th>Reg</th><th>Store</th><th>Unit</th></tr></thead>
<tbody id="rows"></tbody></table><script>
const rowsEl=document.getElementById('rows'),input=document.getElementById('q');let data=[];
fetch('deals_safeway.json').then(r=>r.json()).then(j=>{{data=j;render('')}});
function money(v){{return v==null?'':'$'+Number(v).toFixed(2)}}
function render(q){{rowsEl.innerHTML='';const qq=q.toLowerCase();
data.filter(r=>!qq||r.item.toLowerCase().includes(qq)).forEach(r=>{{
rowsEl.innerHTML+=`<tr><td>${{r.item}}</td><td>${{r.size||''}}</td><td>${{money(r.sale_price)}}</td><td>${{money(r.reg_price)}}</td>
<td><span class="badge">${{r.store}}</span></td><td>${{r.unit||''}}</td></tr>`}})}}
input.addEventListener('input',e=>render(e.target.value));
</script></body></html>"""
    out_html.write_text(html, encoding='utf-8')
    print(f"Wrote {out_html}")


if __name__ == "__main__":
    main()