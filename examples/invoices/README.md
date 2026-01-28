# Invoice Examples

This directory contains sample invoice documents for testing Aletheia's parsing capabilities.

## Files

- `sample_invoice.pdf` - Standard business invoice
- `multi_page_invoice.pdf` - Invoice spanning multiple pages
- `scanned_invoice.png` - Scanned/photographed invoice image

## Expected Extraction

Aletheia should extract:
- Invoice number
- Date
- Vendor information
- Line items (description, quantity, price)
- Totals (subtotal, tax, total)
- Payment terms

## Testing

```bash
aletheia parse invoices/sample_invoice.pdf --output invoice_result.json
```
