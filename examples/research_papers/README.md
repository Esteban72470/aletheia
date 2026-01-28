# Research Paper Examples

This directory contains sample academic/research papers for testing Aletheia's parsing capabilities.

## Files

- `arxiv_sample.pdf` - Sample arXiv paper with figures and equations
- `ieee_format.pdf` - IEEE formatted paper
- `acm_format.pdf` - ACM formatted paper

## Expected Extraction

Aletheia should extract:
- Title and authors
- Abstract
- Section headings and content
- Figures with captions
- Tables with captions
- References/bibliography
- Equations (as LaTeX or MathML)
- Footnotes

## Document Structure

Research papers typically have:
1. Header (title, authors, affiliations)
2. Abstract
3. Introduction
4. Methodology
5. Results
6. Discussion
7. Conclusion
8. References

## Testing

```bash
aletheia parse research_papers/arxiv_sample.pdf --output paper_result.json
aletheia parse research_papers/arxiv_sample.pdf --query "extract all figures and their captions"
```
