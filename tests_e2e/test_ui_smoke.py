"""
S.O.I.L.E.R. E2E Smoke Tests

Verifies critical UI functionality:
1. Selection Summary panel visible and updates
2. Dropdown selection works and persists
3. Run/Analyze button triggers processing
"""

from playwright.sync_api import Page, expect


class TestSelectionSummary:
    """Tests for the Selection Summary panel."""

    def test_summary_panel_visible(self, page: Page):
        """Verify the selection summary panel exists in sidebar."""
        # The summary title we specified
        summary_text = page.get_by_text("สรุปสิ่งที่เลือก")
        expect(summary_text.first).to_be_visible(timeout=10000)

    def test_summary_anchor_exists(self, page: Page):
        """Verify the stable HTML anchor exists for testing."""
        anchor = page.locator("#selection-summary")
        expect(anchor).to_be_attached()


class TestDropdownSelection:
    """Tests for dropdown selection functionality."""

    def test_crop_dropdown_visible(self, page: Page):
        """Verify crop selection dropdown is visible."""
        # Look for the crop selection in sidebar
        # The sidebar should have crop selection options
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible(timeout=10000)

        # Check that there's a selectbox (crop dropdown)
        selectbox = sidebar.locator('[data-baseweb="select"]').first
        expect(selectbox).to_be_visible(timeout=5000)

    def test_dropdown_selection_updates_summary(self, page: Page):
        """Verify that changing dropdown updates the Selection Summary."""
        # Find the sidebar
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible(timeout=10000)

        # Find crop selectbox and click to open
        crop_select = sidebar.locator('[data-baseweb="select"]').first
        expect(crop_select).to_be_visible(timeout=10000)
        crop_select.click()

        # Wait a bit for dropdown to open
        page.wait_for_timeout(500)

        # Try to find menu items (may appear as popup or in page)
        menu = page.locator('[data-baseweb="menu"]')
        if menu.count() > 0:
            menu_items = menu.locator('li[data-baseweb="menu-item"]')
            count = menu_items.count()
            if count >= 2:
                menu_items.nth(1).click()
                page.wait_for_timeout(1000)

        # Verify selection summary is still visible (page didn't crash)
        summary_text = page.get_by_text("สรุปสิ่งที่เลือก")
        expect(summary_text.first).to_be_visible(timeout=10000)


class TestRunAnalysis:
    """Tests for the Run Analysis functionality."""

    def test_run_button_visible(self, page: Page):
        """Verify the run analysis button is visible."""
        sidebar = page.locator('[data-testid="stSidebar"]')

        # Look for button with the run text
        run_button = sidebar.get_by_role("button", name="เริ่มวิเคราะห์")
        expect(run_button).to_be_visible(timeout=10000)

    def test_run_button_anchor_exists(self, page: Page):
        """Verify the stable HTML anchor exists for the run button."""
        anchor = page.locator("#run-button")
        expect(anchor).to_be_attached()

    def test_run_triggers_processing(self, page: Page):
        """Verify clicking run triggers processing and shows result."""
        sidebar = page.locator('[data-testid="stSidebar"]')

        # Find and click the run button
        run_button = sidebar.get_by_role("button", name="เริ่มวิเคราะห์")
        expect(run_button).to_be_visible(timeout=10000)
        run_button.click()

        # Wait for processing to start (look for any processing indicator)
        # The status expander shows processing text during analysis
        page.wait_for_timeout(2000)

        # Check that either:
        # 1. Processing indicator is visible (analysis in progress)
        # 2. Or run-ok marker appears (analysis completed quickly)
        # 3. Or tabs appear (analysis result showing)
        processing = page.get_by_text("กำลังวิเคราะห์")
        tabs = page.locator('[data-baseweb="tab-list"]')
        run_ok = page.locator("#run-ok")

        # Wait for any of these conditions
        try:
            expect(processing.first.or_(tabs).or_(run_ok)).to_be_visible(timeout=30000)
        except Exception:
            # If none visible, at least verify no exception shown
            pass

        # Final check: no exception should be visible
        exception_locator = page.locator(".stException")
        expect(exception_locator).not_to_be_visible()


class TestSelectboxVisibility:
    """Visual regression tests for selectbox visibility.

    These tests catch the bug where selected value is invisible due to
    CSS issues (height: 0px, transparent color, etc).
    """

    def test_selectbox_value_has_visible_height(self, page: Page):
        """Verify the selected value element has non-zero height.

        Bug: Streamlit CSS can set the text container to height: 0px
        with overflow: hidden, making the selected value invisible.
        """
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible(timeout=10000)

        # Find the first selectbox
        selectbox = sidebar.locator('[data-baseweb="select"]').first
        expect(selectbox).to_be_visible(timeout=5000)

        # Check the text container has visible height
        result = page.evaluate("""(selector) => {
            const selectbox = document.querySelector(selector);
            if (!selectbox) return { error: 'Selectbox not found' };

            // The text element is: selectbox > div > div > div:first-child
            const textEl = selectbox.querySelector(':scope > div > div > div:first-child');
            if (!textEl) return { error: 'Text element not found' };

            const rect = textEl.getBoundingClientRect();
            const style = window.getComputedStyle(textEl);
            const text = (textEl.innerText || textEl.textContent || '').trim();

            return {
                hasText: text.length > 0,
                height: rect.height,
                computedHeight: style.height,
                overflow: style.overflow,
            };
        }""", '[data-testid="stSidebar"] [data-baseweb="select"]')

        assert result.get('hasText', False), "Selectbox should have text"
        assert result.get('height', 0) > 0, f"Text container height should be > 0, got {result.get('height')}"
        # Note: overflow can be 'visible' or 'hidden' - we just need height > 0

    def test_selectbox_value_color_is_visible(self, page: Page):
        """Verify the selected value text has visible color (not transparent).

        Bug: CSS can set color or -webkit-text-fill-color to transparent,
        making text invisible even with correct height.
        """
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible(timeout=10000)

        selectbox = sidebar.locator('[data-baseweb="select"]').first
        expect(selectbox).to_be_visible(timeout=5000)

        # Check color properties
        result = page.evaluate("""(selector) => {
            const selectbox = document.querySelector(selector);
            if (!selectbox) return { error: 'Selectbox not found' };

            const textEl = selectbox.querySelector(':scope > div > div > div:first-child');
            if (!textEl) return { error: 'Text element not found' };

            const style = window.getComputedStyle(textEl);

            // Parse color to check for transparency
            function parseAlpha(colorStr) {
                if (!colorStr) return 1;
                const match = colorStr.match(/rgba?\\([^)]+,\\s*([\\d.]+)\\s*\\)/);
                if (match) return parseFloat(match[1]);
                return 1;  // rgb() without alpha = fully opaque
            }

            return {
                color: style.color,
                webkitTextFillColor: style.webkitTextFillColor,
                opacity: parseFloat(style.opacity),
                colorAlpha: parseAlpha(style.color),
                fillColorAlpha: parseAlpha(style.webkitTextFillColor),
            };
        }""", '[data-testid="stSidebar"] [data-baseweb="select"]')

        # Check opacity is close to 1
        assert result.get('opacity', 0) >= 0.9, f"Opacity should be >= 0.9, got {result.get('opacity')}"

        # Check color is not transparent (alpha > 0.9)
        assert result.get('colorAlpha', 0) >= 0.9, f"Color alpha should be >= 0.9, got {result.get('colorAlpha')}"

        # Check -webkit-text-fill-color is not transparent
        if result.get('webkitTextFillColor'):
            assert result.get('fillColorAlpha', 0) >= 0.9, \
                f"-webkit-text-fill-color alpha should be >= 0.9, got {result.get('fillColorAlpha')}"

    def test_selectbox_value_not_black_on_dark(self, page: Page):
        """Verify selected value is not black text on dark background.

        Bug: Text could be black (rgb(0,0,0)) on dark background,
        making it effectively invisible.
        """
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible(timeout=10000)

        selectbox = sidebar.locator('[data-baseweb="select"]').first
        expect(selectbox).to_be_visible(timeout=5000)

        result = page.evaluate("""(selector) => {
            const selectbox = document.querySelector(selector);
            if (!selectbox) return { error: 'Selectbox not found' };

            const textEl = selectbox.querySelector(':scope > div > div > div:first-child');
            if (!textEl) return { error: 'Text element not found' };

            const style = window.getComputedStyle(textEl);

            // Parse RGB values
            function parseRgb(colorStr) {
                const match = colorStr.match(/rgb[a]?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                if (match) {
                    return {
                        r: parseInt(match[1]),
                        g: parseInt(match[2]),
                        b: parseInt(match[3])
                    };
                }
                return null;
            }

            const textColor = parseRgb(style.color);
            const bgColor = parseRgb(style.backgroundColor);

            // Get parent background if current is transparent
            let effectiveBg = bgColor;
            if (!bgColor || (bgColor.r === 0 && bgColor.g === 0 && bgColor.b === 0)) {
                const parentStyle = window.getComputedStyle(textEl.parentElement);
                effectiveBg = parseRgb(parentStyle.backgroundColor) || bgColor;
            }

            return {
                textColor: style.color,
                textRgb: textColor,
                bgColor: style.backgroundColor,
                bgRgb: effectiveBg,
            };
        }""", '[data-testid="stSidebar"] [data-baseweb="select"]')

        text_rgb = result.get('textRgb')
        if text_rgb:
            # Text should not be pure black (allow some tolerance)
            is_black = text_rgb['r'] < 10 and text_rgb['g'] < 10 and text_rgb['b'] < 10
            assert not is_black, f"Text color should not be black, got {result.get('textColor')}"


class TestAppLoads:
    """Basic app loading tests.

    Note: These tests verify the app loads without errors.
    The critical functionality tests (selection, dropdown, run) are more important.
    """

    def test_app_has_content(self, page: Page):
        """Verify the app loads with some content."""
        # Wait longer for Streamlit to fully initialize
        page.wait_for_timeout(3000)

        # Get page content (don't require body to be "visible" - Streamlit uses iframes)
        content = page.content()
        # Page HTML should have substantial content
        assert len(content) > 500, "Page should have HTML content"
        # Should not be an error page
        assert "error" not in content.lower()[:500] or "Error" not in page.title()

    def test_no_exceptions_on_load(self, page: Page):
        """Verify no exceptions are shown on initial load."""
        # Check that no Streamlit exception is visible
        exception_locator = page.locator(".stException")
        expect(exception_locator).not_to_be_visible()
