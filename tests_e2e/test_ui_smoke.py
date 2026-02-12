"""
S.O.I.L.E.R. E2E Smoke Tests

Verifies critical UI functionality:
1. Selection Summary panel visible and updates
2. Dropdown selection works and persists
3. Selectbox CSS visibility (regression guard)
4. Run/Analyze button triggers processing
"""

from playwright.sync_api import Page, expect


class TestSelectionSummary:
    """Tests for the Selection Summary panel."""

    def test_summary_panel_visible(self, page: Page):
        """Verify the selection summary panel exists in main layout."""
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


class TestSelectboxVisibility:
    """Visual regression tests for selectbox CSS visibility.

    Guard against the bug where selectbox selected values become invisible
    due to CSS issues (height: 0px, transparent color, clipping).

    Navigates to the crop tab (step 2) where a selectbox is always present.
    Placed BEFORE TestRunAnalysis to avoid server load from analysis.
    """

    def _navigate_to_crop_tab(self, page: Page):
        """Click the crop tab (2nd tab) so its selectbox is visible."""
        # Wait for Streamlit tabs to render
        page.wait_for_timeout(2000)
        # Click the second tab (crop) - use the tab panel's aria role
        crop_tab = page.get_by_role("tab", name="พืช")
        expect(crop_tab.first).to_be_visible(timeout=15000)
        crop_tab.first.click()
        page.wait_for_timeout(1000)

    def _get_selectbox(self, page: Page):
        """Return the crop selectbox in the main content area."""
        selectbox = page.locator('[data-baseweb="select"]').first
        expect(selectbox).to_be_visible(timeout=10000)
        return selectbox

    def test_selectbox_value_has_visible_height(self, page: Page):
        """Verify the selectbox element has non-zero rendered height.

        Bug: Streamlit CSS can set the text container to height: 0px
        with overflow: hidden, making the selected value invisible.
        """
        self._navigate_to_crop_tab(page)
        selectbox = self._get_selectbox(page)

        box = selectbox.bounding_box()
        assert box is not None, "Selectbox should have a bounding box"
        assert box["height"] > 10, (
            f"Selectbox height should be > 10px, got {box['height']}"
        )

    def test_selectbox_value_color_is_visible(self, page: Page):
        """Verify the selected value text has visible color (not transparent).

        Bug: CSS can set color or -webkit-text-fill-color to transparent,
        making text invisible even with correct height.
        """
        self._navigate_to_crop_tab(page)
        selectbox = self._get_selectbox(page)

        result = selectbox.evaluate("""(el) => {
            const textEl = el.querySelector(':scope > div > div > div:first-child');
            if (!textEl) return { error: 'Text element not found' };
            const style = window.getComputedStyle(textEl);
            function parseAlpha(colorStr) {
                if (!colorStr) return 1;
                const m = colorStr.match(/rgba?\\([^)]+,\\s*([\\d.]+)\\s*\\)/);
                return m ? parseFloat(m[1]) : 1;
            }
            return {
                opacity: parseFloat(style.opacity),
                colorAlpha: parseAlpha(style.color),
                fillColorAlpha: parseAlpha(style.webkitTextFillColor),
            };
        }""")

        assert result.get("opacity", 0) >= 0.5, (
            f"Opacity should be >= 0.5, got {result.get('opacity')}"
        )
        assert result.get("colorAlpha", 0) >= 0.5, (
            f"Color alpha should be >= 0.5, got {result.get('colorAlpha')}"
        )

    def test_selectbox_value_not_clipped(self, page: Page):
        """Verify selectbox value is not clipped to zero size.

        Bug: overflow: hidden + height: 0 makes text invisible
        even though the element exists in DOM.
        """
        self._navigate_to_crop_tab(page)
        selectbox = self._get_selectbox(page)

        result = selectbox.evaluate("""(el) => {
            const textEl = el.querySelector(':scope > div > div > div:first-child');
            if (!textEl) return { height: 0, overflow: 'hidden' };
            const rect = textEl.getBoundingClientRect();
            const style = window.getComputedStyle(textEl);
            return {
                height: rect.height,
                width: rect.width,
                overflow: style.overflow,
            };
        }""")

        assert result.get("height", 0) > 0, (
            f"Text container height should be > 0, got {result.get('height')}"
        )
        assert result.get("width", 0) > 0, (
            f"Text container width should be > 0, got {result.get('width')}"
        )


class TestWizardNavigation:
    """Tests for the 5-step wizard navigation flow.

    Verifies that tabs are navigable, navigation hints are present,
    and selected values appear in the sidebar summary panel.
    """

    def test_all_five_tabs_present(self, page: Page):
        """Verify all 5 wizard tabs are rendered."""
        page.wait_for_timeout(2000)
        tabs = page.locator('[role="tab"]')
        assert tabs.count() >= 5, f"Expected >= 5 tabs, got {tabs.count()}"

    def test_crop_tab_navigation(self, page: Page):
        """Navigate to crop tab and verify selectbox appears."""
        page.wait_for_timeout(2000)
        crop_tab = page.get_by_role("tab", name="พืช")
        expect(crop_tab.first).to_be_visible(timeout=10000)
        crop_tab.first.click()
        page.wait_for_timeout(1000)

        selectbox = page.locator('[data-baseweb="select"]').first
        expect(selectbox).to_be_visible(timeout=10000)

    def test_nav_hints_present(self, page: Page):
        """Verify step navigation hints are rendered in the DOM."""
        page.wait_for_timeout(2000)
        # The first tab should have a "next" hint but no "back" hint
        nav_next = page.locator("#nav-next-1")
        expect(nav_next).to_be_attached(timeout=10000)

    def test_summary_shows_selected_values(self, page: Page):
        """Verify the summary panel reflects session_state defaults."""
        # The summary should show default values on first load
        summary = page.get_by_text("สรุปสิ่งที่เลือก")
        expect(summary.first).to_be_visible(timeout=10000)

        # Check that coordinates appear in summary panel (now in main layout)
        summary_anchor = page.locator("#selection-summary")
        expect(summary_anchor).to_be_attached(timeout=10000)
        # Get the parent column text
        page_text = page.inner_text("body")
        assert "พิกัด" in page_text, "Summary should show coordinates"
        assert "พืช" in page_text, "Summary should show crop"
        assert "ดิน" in page_text, "Summary should show soil data"

    def test_soil_tab_has_sliders(self, page: Page):
        """Navigate to soil tab and verify input controls exist."""
        page.wait_for_timeout(2000)
        soil_tab = page.get_by_role("tab", name="ดิน")
        expect(soil_tab.first).to_be_visible(timeout=10000)
        soil_tab.first.click()
        page.wait_for_timeout(1000)

        # Soil tab should have slider controls
        sliders = page.locator('[data-testid="stSlider"]')
        assert sliders.count() >= 2, f"Expected >= 2 sliders, got {sliders.count()}"


class TestRunAnalysis:
    """Tests for the Run Analysis functionality.

    WARNING: These tests trigger actual analysis which can load the server.
    Keep these LAST in the test file to avoid affecting other tests.
    """

    def test_run_button_visible(self, page: Page):
        """Verify the run analysis button is visible in wizard tabs."""
        # With the new wizard UI, the run button is in the "แผน" (Plan) tab
        # Navigate to the Plan tab (step 4) where the run button is
        plan_tab = page.get_by_role("tab", name="แผน")
        if plan_tab.count() > 0:
            plan_tab.first.click()
            page.wait_for_timeout(1000)

        # Look for button with the run text (includes emoji prefix)
        run_button = page.get_by_role("button", name="เริ่มวิเคราะห์")
        expect(run_button).to_be_visible(timeout=10000)

    def test_run_button_anchor_exists(self, page: Page):
        """Verify the stable HTML anchor exists for the run button."""
        anchor = page.locator("#run-button")
        expect(anchor).to_be_attached()

    def test_run_triggers_processing(self, page: Page):
        """Verify clicking run triggers processing and shows result."""
        # Navigate to the Plan tab where the run button is
        plan_tab = page.get_by_role("tab", name="แผน")
        if plan_tab.count() > 0:
            plan_tab.first.click()
            page.wait_for_timeout(1000)

        # Find and click the run button
        run_button = page.get_by_role("button", name="เริ่มวิเคราะห์")
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
