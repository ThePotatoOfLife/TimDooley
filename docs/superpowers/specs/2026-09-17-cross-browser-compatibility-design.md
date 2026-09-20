# Cross-Browser Compatibility Hardening Design

## Goal

Make the public TimDooley site robust across current Chrome/Edge, Firefox, Safari, iPhone/iPad Safari, Android Chrome, Samsung Internet, and other modern Chromium-based browsers without otherwise changing the site's appearance, content, information architecture, or intended interaction model.

## Non-negotiable constraint

This is a compatibility and resilience pass, not a redesign.

- Do not change visible copy or content unless a browser-specific failure makes a tiny compatibility label/message necessary.
- Do not change navigation structure or route meaning.
- Do not restyle the site for aesthetic reasons.
- Do not alter colors, typography, spacing, visual hierarchy, or interaction patterns except where a browser/device currently breaks, clips, overlaps, hides, or prevents use.
- Preserve current desktop behavior when it already works.
- Preserve the current TTS behavior and follow-reading semantics where the platform supports them.

## Supported platform contract

First-class support targets:

- Current Chromium family: Chrome, Edge, Samsung Internet, and Chromium-derived desktop/mobile browsers.
- Current Firefox on desktop and Android.
- Current Safari on macOS.
- Current Safari/WebKit on iPhone and iPad.
- Windows and macOS desktop/laptop form factors.
- Phones and tablets in portrait and landscape.
- Mouse, trackpad, touch, and keyboard input.

Legacy engines such as Internet Explorer are explicitly out of scope. Browsers missing optional modern APIs must still receive readable content, working links/navigation, and a usable core reader experience.

## Architecture

Compatibility is provided through progressive enhancement rather than a transpilation-heavy frontend rebuild.

1. **Shared CSS compatibility foundation**
   - Add stable fallbacks before advanced declarations.
   - Prefer intrinsic sizing, wrapping, `min-width: 0`, and overflow containment for shared layouts.
   - Use `vh` as fallback and `svh`/`dvh` where supported for browser chrome and mobile viewport behavior.
   - Add safe-area handling using `env(safe-area-inset-*)` where fixed/sticky UI can collide with notches or home indicators.
   - Keep touch controls practically tappable without changing desktop presentation.
   - Respect reduced motion and forced/high-contrast behavior where possible without changing the normal theme.

2. **Feature-detected JavaScript fallbacks**
   - Optional APIs must not be assumed to exist.
   - `IntersectionObserver`: use eager/loading or scroll-safe fallback behavior where observation is unavailable.
   - Clipboard: copy controls degrade to selectable text/address-bar behavior rather than throwing.
   - AbortController: retain cancellation where available; use safe non-cancellable operation where unavailable if the feature can still work.
   - CSS Custom Highlight API: retain DOM/range fallback highlighting already used by TTS.
   - Speech synthesis: controls should fail clearly and non-destructively if the browser lacks speech support or word-boundary events.

3. **Special-surface hardening**
   - Great Book / longform reader.
   - Shared TTS drawer and standalone TTS reader.
   - Main public page system.
   - Older two-pane/minimal layouts still exposed publicly.
   - World Map and other complex/interactive public surfaces, using graceful fallback where the underlying WebGL/browser capability is unavailable.

4. **Browser regression matrix**
   - Add browser-level checks using Playwright if a lightweight test dependency can be introduced without changing production runtime behavior.
   - Test Chromium, Firefox, and WebKit.
   - Include representative desktop, phone, and tablet viewport profiles.
   - Smoke-test homepage, Great Book, TTS reader, longform content, timeline, and World Map shell.
   - Check for uncaught page errors, horizontal document overflow, unreachable primary controls, broken sticky/fixed overlays, and core navigation failures.
   - TTS browser tests may mock speech synthesis for deterministic UI/state testing; they must not claim to validate operating-system voice quality.

## CSS compatibility policy

Advanced CSS remains allowed, but only as enhancement.

- `backdrop-filter`: base background/border must look acceptable without blur.
- `color-mix()`: provide an ordinary color/background before the enhanced mixed color.
- `:has()`: content and navigation cannot depend on it; selectors using it may add decoration only.
- `position: sticky`: content must remain reachable if sticky positioning is ineffective.
- `100vh`: avoid relying on it as the sole mobile viewport height when dynamic browser chrome is relevant.
- Tables, code blocks, media, long URLs, and navigation rows must not force whole-page horizontal overflow.

## Mobile layout policy

- No page-level horizontal scrolling at common phone widths unless the surface itself is intentionally pannable (for example a map or a wide data table inside its own overflow container).
- Fixed/sticky controls must not cover the current reading line or become unreachable behind mobile browser chrome.
- Input fields must remain usable when the on-screen keyboard opens.
- Touch interactions must not require hover.
- Portrait and landscape orientations should preserve access to primary controls.
- iPhone/iPad safe areas must be respected for controls positioned near viewport edges.

## TTS compatibility policy

- Speech playback is feature-detected.
- Missing/poor `boundary` events may reduce exact word-follow precision, but must not break speech playback or the page.
- Follow-reading remains user-toggleable at all times.
- Turning follow off must stop future viewport-follow behavior immediately.
- The drawer's internal reading copy must never compete with real-page following.
- Great Book lazy-loading must remain compatible with TTS whole-book reading.
- Browser compatibility changes must preserve the fixes merged in PRs #233, #236, #238, #239, #241, and #243.

## World Map / graphics compatibility policy

- Detect required graphics/runtime capabilities before booting advanced map behavior.
- Unsupported advanced rendering should present a stable fallback state rather than a blank/broken page or uncaught exception.
- Touch gestures and resize/orientation changes must not strand controls outside the viewport.
- Compatibility work must not change map data, visual styling, political boundaries, content, or layer semantics.

## Testing strategy

Use test-driven changes for each compatibility issue.

Static/source tests should verify:

- fallbacks precede optional CSS enhancements;
- viewport/safe-area rules exist where relevant;
- feature detection exists for optional browser APIs;
- no compatibility change removes the existing TTS contracts;
- no compatibility patch introduces page-level overflow patterns known to break mobile layouts.

Browser smoke tests should verify:

- pages load without uncaught JavaScript exceptions;
- main content is visible;
- core navigation can be activated by keyboard and pointer;
- document width does not exceed viewport width on standard content pages;
- responsive layouts collapse as intended;
- TTS UI opens and can toggle follow in a mocked speech environment;
- Great Book reader can load its initial/current content;
- timeline/reader controls remain reachable;
- World Map shell either boots successfully or reaches an intentional fallback state.

## Delivery strategy

Implement in focused, reviewable stages on a dedicated branch:

1. Add compatibility regression tests/audit checks first and verify they fail on known gaps.
2. Add shared CSS/browser foundation with no intentional visual change.
3. Harden Great Book and longform loading/follow behavior for optional browser APIs.
4. Harden shared and standalone TTS compatibility.
5. Harden public interactive/special surfaces, especially World Map and timeline/clipboard behavior.
6. Add/finish Playwright browser matrix and run Chromium, Firefox, WebKit, phone, and tablet smoke coverage.
7. Run the repository's existing quality suite plus the new compatibility suite.
8. Review the final diff specifically for unintended visual/content changes before merge.

## Definition of done

- The site remains visually and structurally the same under its existing supported desktop presentation.
- Core content/navigation works on the first-class browser/platform matrix.
- Major public reader surfaces remain usable on phone/tablet/desktop.
- Optional features degrade safely when an API is missing.
- No uncaught compatibility exceptions on tested smoke pages.
- No unintended whole-page horizontal overflow on standard content pages at representative mobile widths.
- Existing TTS regression tests remain green.
- New compatibility checks are part of CI so future changes cannot silently reintroduce the same classes of bugs.
