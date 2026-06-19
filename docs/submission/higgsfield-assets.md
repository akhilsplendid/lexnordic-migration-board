# Higgsfield Assets

Generated on 2026-06-18 after CLI authentication.

## Recommended Submission Assets

| Asset | Path | Model | Use |
| --- | --- | --- | --- |
| Final poster | `docs/submission/assets/higgsfield/lexnordic-higgsfield-poster-final.png` | GPT Image 2 | Submission thumbnail, opening video frame, deck cover alternative. |
| Preferred cover derivative | `docs/submission/assets/lexnordic-cover-higgsfield.png` | Local crop/resize from final poster | Exact 1600x900 upload-ready cover image. |
| Band room deck visual | `docs/submission/assets/higgsfield/lexnordic-higgsfield-deck-band-room.png` | GPT Image 2 | Slide visual for Band coordination and agent handoffs. |
| Architecture deck visual | `docs/submission/assets/higgsfield/lexnordic-higgsfield-deck-architecture.png` | GPT Image 2 | Slide visual for Supabase, Qdrant, Band, AI/ML API, and Featherless architecture. |
| Legal RAG/source visual | `docs/submission/assets/higgsfield/lexnordic-higgsfield-deck-rag-source.png` | GPT Image 2 | Slide visual for source grounding and retrieval. |
| AI packet deck visual | `docs/submission/assets/higgsfield/lexnordic-higgsfield-deck-packet.png` | GPT Image 2 | Slide visual for final packet workspace. |
| Architecture teaser video | `docs/submission/assets/higgsfield/lexnordic-higgsfield-architecture-teaser.mp4` | Seedance 2.0 | 12-second presentation/video insert showing system-flow motion. |
| Architecture teaser frame | `docs/submission/assets/higgsfield/lexnordic-higgsfield-architecture-teaser-frame.png` | Seedance 2.0 frame capture | Poster frame or deck thumbnail for the teaser. |

## Usage Notes

- Keep main slide text editable in PowerPoint. Use these images as visual panels or backgrounds, not as the only source of slide copy.
- The editable submission deck has been regenerated with these visual panels at `docs/submission/deck/lexnordic-band-of-agents-submission-redone.pptx`; previews are in `docs/submission/deck/previews/`.
- The final poster was locally corrected to remove wording that implied human-side gatekeeping or authority filing.
- The recommended teaser is the architecture-flow video because it avoids UI text distortion and stays readable.
- Non-recommended generations were moved to ignored `.agent-context/higgsfield/rejected/`:
  - an early poster that implied submission/filing;
  - a screenshot-based Theater teaser with distorted UI text;
  - a Band-room video attempt that was blocked by Higgsfield safety classification and produced no output URL.

## Model Rationale

- GPT Image 2 was used for poster and deck visuals because the assets need high-fidelity product/design composition and readable brand text.
- Seedance 2.0 was used for the final teaser because it is the best default Higgsfield model for serious 4-15 second production video and image-to-video motion.
