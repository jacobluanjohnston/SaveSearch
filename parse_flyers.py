#!/usr/bin/env python3
import sys, json, argparse, base64, glob
from pathlib import Path
from typing import List, Dict
import anthropic


def pdf_to_base64(pdf_path: Path) -> str:
    return base64.standard_b64encode(pdf_path.read_bytes()).decode("utf-8")


def extract_deals_with_ai(pdf_path: Path, api_key: str) -> List[Dict]:
    client = anthropic.Anthropic(api_key=api_key)
    pdf_data = pdf_to_base64(pdf_path)

    prompt = """Extract ALL grocery deals from this flyer PDF. For each item provide:
- item: Product name (without size info)
- sale_price: Sale price as number (or null)
- reg_price: Regular price as number (or null)  
- unit: Unit like LB, EA (or null)
- size: Package size like "32oz", "3ct", "16oz", "2lb" (or null if not specified)

IMPORTANT RULES:
1. CRITICAL: When you see "X for $Y" deals (like "2 for $6" or "4 for $5"), the deal MUST be physically touching or directly next to the product name
   - If "2 for $6" is on the La Colombe product, calculate 6÷2 = 3.00
   - If you see multiple deals on the same page, DO NOT mix them up
   - Each deal belongs ONLY to the product it's visually attached to
   - Double-check: does THIS specific "X for $Y" apply to THIS specific product?
2. If you see "$X OFF" or "SAVE $X" without actual prices, set both sale_price and reg_price to null
3. For price ranges like "Reg $2.99-3.19", use the LOWER number (2.99)
4. For price ranges like "$13.99-15.99", use the LOWER number (13.99)
5. Extract package size separately (oz, ct, lb, gal, etc.) - this is important for price comparison
6. Skip section headers, page numbers, dates, and non-product text
7. "Reg $X" means reg_price is X
8. Return ONLY valid JSON array, no markdown, no comments

VERIFICATION: Before finalizing each "X for $Y" calculation, ask yourself: "Is this deal text directly ON or NEXT TO this specific product?" 

Examples:
[
  {"item": "Organic Apples", "sale_price": 2.49, "reg_price": 3.49, "unit": "LB", "size": null},
  {"item": "Apple Juice", "sale_price": 4.99, "reg_price": 6.99, "unit": "EA", "size": "32oz"},
  {"item": "Microwave Popcorn", "sale_price": 3.99, "reg_price": 5.99, "unit": "EA", "size": "3ct"},
  {"item": "Coffee", "sale_price": 9.99, "reg_price": 13.99, "unit": "EA", "size": "10-12oz"},
  "item": "Greek Yogurt 4 for $5", "sale_price": 1.25, "reg_price": 2.19, "unit": "EA", "size": "5.3oz"},
  {"item": "Snacks 2 for $6", "sale_price": 3.00, "reg_price": 4.99, "unit": "EA", "size": "5.6oz"}
]"""

    print(f"  Sending to API...")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
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

    # Clean up response
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    # Fix truncated JSON
    if not response_text.endswith(']'):
        last_complete = response_text.rfind('},')
        if last_complete > 0:
            response_text = response_text[:last_complete + 1] + ']'
            print(f"  ⚠ Response was truncated, recovered {response_text.count('{')} items")

    # Remove trailing commas
    response_text = response_text.replace(",]", "]").replace(",}", "}")

    deals = json.loads(response_text)

    for deal in deals:
        if deal.get('sale_price'):
            deal['sale_price'] = round(float(deal['sale_price']), 2)
        if deal.get('reg_price'):
            deal['reg_price'] = round(float(deal['reg_price']), 2)

    return deals


def main():
    ap = argparse.ArgumentParser(description="Extract grocery deals using AI")
    ap.add_argument("pdfs", nargs="+", help="PDF flyer paths")
    ap.add_argument("--api-key", required=True, help="Anthropic API key")
    ap.add_argument("--outdir", default="out", help="Output directory")
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

    # Filter out items with no prices
    all_deals = [d for d in all_deals if d.get('sale_price') is not None or d.get('reg_price') is not None]

    out_json = outdir / "deals.json"
    out_json.write_text(json.dumps(all_deals, indent=2), encoding="utf-8")
    print(f"\nWrote {out_json} ({len(all_deals)} items)")

    import csv
    out_csv = outdir / "deals.csv"
    with out_csv.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, ['store', 'item', 'size', 'unit', 'sale_price', 'reg_price'])
        w.writeheader()
        w.writerows(all_deals)
    print(f"Wrote {out_csv}")


if __name__ == "__main__":
    main()