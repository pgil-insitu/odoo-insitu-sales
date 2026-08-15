# Product Design QA — inSitu Sales Odoo Marketplace Listing

## Comparison target

- Source visual truth for the compatibility/CTA revision: `design-qa/implementation-desktop-viewport.png` and `design-qa/implementation-mobile.png`, supported by the authentic inSitu Sales assets in `insitu_sales_connector/static/description/`.
- Implementation: `insitu_sales_connector/static/description/index.html`.
- Desktop implementation screenshot: `design-qa/implementation-odoo16plus-native.png`.
- Mobile implementation screenshot: `design-qa/implementation-odoo16plus-mobile.png`.
- Selling-motions screenshot: `design-qa/implementation-selling-motions.png`.
- Inventory-and-pricing screenshot: `design-qa/implementation-inventory-pricing.png`.
- Synchronization-section screenshot: `design-qa/implementation-sync-section.png`.
- Combined source/implementation comparison: `design-qa/comparison-odoo16plus.png`.
- State: default page state, plus the `#insitu-sync` anchor destination.

## Capture normalization

- Source CSS viewport and capture: 1280 x 720 pixels, device pixel ratio 1; normalized to 1064 x 599 for the comparison board.
- Desktop implementation: native in-app browser viewport of 1064 x 887 CSS/captured pixels, device pixel ratio 1; the top 1064 x 599 region is used in the comparison board.
- Mobile implementation: 390 x 844 CSS pixels and 390 x 844 captured pixels, device pixel ratio 1.
- Combined comparison: desktop source/implementation and mobile source/implementation are paired in one 2200 x 1639 pixel image.

## Full-view comparison evidence

`design-qa/comparison-odoo16plus.png` places the previously approved first viewport and the latest compatibility/CTA revision in the same image. The revision preserves the approved visual system while changing only the compatibility label and the CTA destination.

The visible result has a clear headline, readable supporting copy, two distinct actions, a properly framed product visual, and compatibility information above the fold. There is no clipping or horizontal overflow at desktop or mobile widths.

## Required fidelity surfaces

- Fonts and typography: system UI typography renders consistently without external font requests. Heading weights, sizes, wrapping, and line heights create a clear hierarchy at 1280 px and 390 px. The mobile H1 remains readable at 42 px without clipping.
- Spacing and layout rhythm: desktop uses a consistent 1120 px content shell, balanced two-column hero, 20 px card gaps, and predictable section spacing. Mobile collapses to one column and gives both primary actions the full available width.
- Colors and visual tokens: the listing uses the inSitu red as the primary action/accent, Odoo plum for integration context, restrained neutrals for surfaces, and sufficient foreground/background contrast.
- Image quality and asset fidelity: all three visible images are authentic local inSitu Sales assets. Browser checks reported their natural dimensions as 1600 x 900, 755 x 780, and 1556 x 1121. No placeholder, generated, inline-SVG, or CSS-drawn product imagery is present.
- Copy and content: the page consistently positions inSitu Sales as operational software for wholesale distributors. DSD, presales, and B2B ecommerce each receive a dedicated value proposition, with inventory availability and customer-specific pricing presented as their common data foundation. The copy clearly scopes online/offline use to the mobile DSD and presales workflows rather than the B2B storefront. Odoo remains identified as the ERP system of record.

## Focused evidence

- `design-qa/implementation-mobile.png`: validates first-screen hierarchy, wrapping, full-width actions, image scale, and the absence of horizontal overflow at 390 px.
- `design-qa/implementation-selling-motions.png`: validates the equal-height DSD, presales, and B2B ecommerce cards at desktop width.
- `design-qa/implementation-inventory-pricing.png`: validates the online/offline mobile capability alongside inventory availability and customer-specific pricing, with authentic product imagery.
- `design-qa/implementation-sync-section.png`: validates legibility of the authentic synchronization map, the source-of-record explanation, and the security note at desktop width.

## Comparison history

### Iteration 1

- Earlier finding [P1]: the original HTML depended on host-provided Bootstrap, so direct preview rendered as raw headings, paragraphs, and oversized images with no usable marketplace hierarchy.
- Fix: added a fully namespaced, self-contained responsive design using local assets and no JavaScript or external stylesheet/font dependency.
- Earlier finding [P2]: an em dash in the first implementation rendered as mojibake in the direct-file capture.
- Fix: replaced the literal character with the HTML entity `&mdash;`.
- Post-fix evidence: `design-qa/qa-comparison-top.png`, `design-qa/implementation-mobile.png`, and `design-qa/implementation-sync-section.png` show the corrected text and stable layouts.

### Iteration 2

- Earlier finding [P1]: the approved prototype led with generic field operations, so DSD, presales, and B2B ecommerce were not immediately identifiable as the three primary selling motions.
- Fix: rewrote the hero, compatibility strip, value cards, data-coverage sections, synchronization story, CTA, and footer around those three motions.
- Earlier finding [P2]: inventory and pricing were present but competed with fulfillment and administration copy.
- Fix: moved inventory availability and customer-specific pricing into the hero and gave them a dedicated section across every order channel.
- Earlier finding [P2]: linking the website's Calendly CTA directly would invalidate the Odoo Apps description under the external-link rule.
- Fix: matched the website's “Book a Demo” label while using an allowed pre-addressed `mailto:` demo request.
- Post-fix evidence: `design-qa/qa-comparison-focus.png`, `design-qa/implementation-selling-motions.png`, `design-qa/implementation-inventory-pricing.png`, and `design-qa/implementation-mobile.png`.

### Iteration 3

- Earlier finding [P2]: the listing did not state that the mobile selling app supports both online and offline work.
- Fix: added online/offline order taking to the hero, the DSD card, and the shared product-data capability list while avoiding an offline claim for B2B ecommerce.
- Post-fix evidence: `design-qa/qa-comparison-offline.png`, `design-qa/implementation-selling-motions.png`, `design-qa/implementation-inventory-pricing.png`, and `design-qa/implementation-mobile.png`.

### Iteration 4

- Earlier finding [P1]: Calendly is not one of the external destinations permitted in an Odoo Apps description, so the requested booking link would be invalidated by the marketplace scan.
- Fix: preserved the “Book a Demo” label while changing both actions to a pre-addressed `mailto:` request, which Odoo explicitly allows.
- Earlier finding [P1]: the visible Odoo 16+ claim was not backed by version-specific manifests and backend XML.
- Fix: prepared matching 16.0, 17.0, 18.0, and 19.0 release branches and kept the visible proof strip explicit about the currently supported majors.
- Post-fix evidence: `design-qa/comparison-odoo16plus.png`, `design-qa/implementation-odoo16plus-native.png`, and `design-qa/implementation-odoo16plus-mobile.png`.

## Interaction and implementation checks

- The “See what synchronizes” action navigates to `#insitu-sync`, and the destination aligns at the top of the viewport.
- Both “Book a Demo” actions resolve to the same pre-addressed `mailto:sales@insitusales.com` demo request.
- All three images loaded successfully with non-zero natural dimensions and meaningful alt text.
- Browser console warnings/errors: none.
- Static addon validation: passed for 13 Python files, 11 XML files, 4 ACL entries, and required marketplace assets.
- Odoo 19 fresh install and transactional tests: passed with 0 failures and 0 errors.
- No scripts, remote HTTP assets, remote HTTP destinations, or `javascript:` links are present in the marketplace HTML.

## Findings

No actionable P0, P1, or P2 visual or interaction findings remain.

## Follow-up polish

- [P3] Verify the exact rendered container width inside an Odoo Apps staging listing, because the marketplace host may apply surrounding margins that are absent from the direct local preview.

## Implementation checklist

- [x] Preserve official inSitu Sales imagery.
- [x] Lead with DSD, presales, and B2B ecommerce.
- [x] Emphasize inventory availability and customer-specific pricing.
- [x] State that DSD and presales mobile workflows work online and offline.
- [x] Keep both “Book a Demo” actions within Odoo's allowed CTA destinations.
- [x] Show supported Odoo majors 16, 17, 18, and 19.
- [x] Make the HTML self-contained and responsive.
- [x] Verify desktop and mobile layouts.
- [x] Verify the primary in-page interaction.
- [x] Confirm image loading and console cleanliness.
- [x] Pass the addon validation script.

final result: passed
