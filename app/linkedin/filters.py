from utils.logger import logger


class LinkedInFilters:
    """
    All filters are applied through LinkedIn's "All filters" side panel,
    using the STABLE input IDs discovered via live DOM inspection:

        Date posted     -> input#advanced-filter-timePostedRange-<code>
        Experience level-> input#advanced-filter-experience-<1-6>
        Remote/Workplace-> input#advanced-filter-workplaceType-<1-3>
        Sort by         -> input#advanced-filter-sortBy-<DD|R>
        Easy Apply      -> toggle switch, located by its label text
                            (its id has a random "ember" suffix that
                            changes per session, so we can't hardcode it)

    Using explicit IDs avoids a real bug the old text-based approach had:
    "Internship" appears as a label in BOTH the Experience Level section
    AND the Job Type section, so text-only matching could click the wrong
    checkbox.
    """

    def __init__(self, browser):
        self.browser = browser

    # -----------------------
    # ID Maps (from live DOM inspection)
    # -----------------------

    DATE_POSTED_IDS = {
        "Any time": "advanced-filter-timePostedRange-",
        "Past month": "advanced-filter-timePostedRange-r2592000",
        "Past week": "advanced-filter-timePostedRange-r604800",
        "Past 24 hours": "advanced-filter-timePostedRange-r86400",
    }

    EXPERIENCE_IDS = {
        "Internship": "advanced-filter-experience-1",
        "Entry level": "advanced-filter-experience-2",
        "Associate": "advanced-filter-experience-3",
        "Mid-Senior level": "advanced-filter-experience-4",
        "Director": "advanced-filter-experience-5",
        "Executive": "advanced-filter-experience-6",
    }

    # Year-range -> LinkedIn experience label(s)
    EXPERIENCE_YEAR_MAP = {
        "0-1": ["Internship", "Entry level"],
        "0-2": ["Internship", "Entry level"],
        "1-3": ["Entry level", "Associate"],
        "2-5": ["Associate", "Mid-Senior level"],
        "5-10": ["Mid-Senior level"],
        "10+": ["Director", "Executive"],
    }

    REMOTE_IDS = {
        "On-site": "advanced-filter-workplaceType-1",
        "Remote": "advanced-filter-workplaceType-2",
        "Hybrid": "advanced-filter-workplaceType-3",
    }

    SORT_IDS = {
        "Most recent": "advanced-filter-sortBy-DD",
        "Most relevant": "advanced-filter-sortBy-R",
    }

    # -----------------------
    # Debug Helper
    # -----------------------

    def _debug_dump_checkbox_inputs(self, context_name):

        logger.warning(f"[{context_name}] Dumping checkbox/radio/switch inputs and their labels...")

        try:
            inputs = self.browser.page.locator(
                'input[type="checkbox"], input[type="radio"], [role="switch"]'
            )

            count = inputs.count()

            logger.warning(f"[{context_name}] Found {count} checkbox/radio/switch inputs (max 80)")

            for i in range(min(count, 80)):

                try:
                    el = inputs.nth(i)

                    input_id = el.get_attribute("id") or ""
                    name_attr = el.get_attribute("name") or ""
                    aria = el.get_attribute("aria-label") or ""

                    label_text = ""

                    if input_id:
                        label_loc = self.browser.page.locator(f'label[for="{input_id}"]')
                        if label_loc.count() > 0:
                            try:
                                label_text = label_loc.first.inner_text(timeout=500).strip().replace("\n", " ")
                            except Exception:
                                pass

                    if not label_text and not aria:
                        continue

                    logger.warning(
                        f"  [{i}] id='{input_id}' name='{name_attr}' aria-label='{aria}' label='{label_text}'"
                    )

                except Exception:
                    continue

        except Exception as e:
            logger.warning(f"[{context_name}] Checkbox dump failed: {e}")

        self.browser.take_screenshot(f"debug-{context_name}")

    # -----------------------
    # Click helper : normal click, fallback to force click
    # -----------------------

    def _safe_click(self, locator, label=""):

        try:
            locator.click(timeout=5000)
            return True

        except Exception:
            logger.warning(f"Normal click failed for '{label}', retrying with force click...")

            try:
                locator.click(force=True, timeout=5000)
                return True

            except Exception as e:
                logger.error(f"Force click also failed for '{label}': {e}")
                return False

    # -----------------------
    # Open the "All filters" side panel (skips if already open)
    # -----------------------

    def _open_all_filters_panel(self):

        # If "Show results" (panel-only button) is already visible, panel is open
        show_results = self.browser.page.get_by_role("button", name="Show results", exact=False).first

        if show_results.count() > 0 and show_results.is_visible():
            return True

        all_filters_btn = self.browser.page.locator(
            'button[aria-label*="Show all filters" i]:visible'
        ).first

        if all_filters_btn.count() == 0:
            all_filters_btn = self.browser.page.get_by_role(
                "button", name="All filters", exact=False
            ).first

        if all_filters_btn.count() == 0:
            logger.error("Could not locate 'All filters' button.")
            return False

        if not self._safe_click(all_filters_btn, "All filters"):
            logger.error("Could not open 'All filters' panel.")
            return False

        self.browser.wait(1500)

        return True

    # -----------------------
    # Select a checkbox/radio input by its exact ID
    # -----------------------

    def _select_by_id(self, full_id, label_for_log=""):

        input_el = self.browser.page.locator(f'input[id="{full_id}"]').first

        if input_el.count() == 0:
            logger.error(f"Input id '{full_id}' not found ({label_for_log}).")
            return False

        try:
            input_el.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pass

        return self._safe_click(input_el, label_for_log or full_id)

    # -----------------------
    # Click "Show results" to apply + close the panel
    # -----------------------

    def _click_show_results(self):

        candidates = [
            self.browser.page.get_by_role("button", name="Show results", exact=False).first,
            self.browser.page.get_by_role("button", name="results", exact=False).first,
            self.browser.page.locator('button:visible:has-text("Show")').first,
            self.browser.page.get_by_role("button", name="Apply", exact=False).first,
            self.browser.page.get_by_role("button", name="Done", exact=False).first,
        ]

        for candidate in candidates:
            try:
                if candidate.count() > 0 and candidate.is_visible():
                    if self._safe_click(candidate, "Show results"):
                        return True
            except Exception:
                continue

        logger.warning("Could not find/click 'Show results'. Panel may not have closed cleanly.")
        return False

    # =====================================================
    # Public Filter Methods
    # =====================================================

    def date_posted(self, option="Past 24 hours"):

        logger.info(f"Applying Filter : Date Posted ({option})")

        full_id = self.DATE_POSTED_IDS.get(option)

        if full_id is None:
            logger.error(f"Unknown date_posted option '{option}'. Valid: {list(self.DATE_POSTED_IDS)}")
            return

        if not self._open_all_filters_panel():
            return

        if self._select_by_id(full_id, option):
            self._click_show_results()
            self.browser.wait(2000)
            logger.success(f"Date Posted Filter Applied : {option}")

    def experience(self, level="0-2"):

        if level in self.EXPERIENCE_YEAR_MAP:
            labels = self.EXPERIENCE_YEAR_MAP[level]
        elif isinstance(level, list):
            labels = level
        else:
            labels = [level]

        logger.info(f"Applying Filter : Experience Level ({level} -> {labels})")

        if not self._open_all_filters_panel():
            return

        applied_any = False

        for label in labels:

            full_id = self.EXPERIENCE_IDS.get(label)

            if full_id is None:
                logger.warning(f"Unknown experience label '{label}'. Skipping.")
                continue

            if self._select_by_id(full_id, label):
                applied_any = True

            self.browser.wait(300)

        if applied_any:
            self._click_show_results()
            self.browser.wait(2000)
            logger.success(f"Experience Level Filter Applied : {labels}")

    def remote(self, mode="Remote"):

        logger.info(f"Applying Filter : Workplace Type ({mode})")

        full_id = self.REMOTE_IDS.get(mode)

        if full_id is None:
            logger.error(f"Unknown remote mode '{mode}'. Valid: {list(self.REMOTE_IDS)}")
            return

        if not self._open_all_filters_panel():
            return

        if self._select_by_id(full_id, mode):
            self._click_show_results()
            self.browser.wait(2000)
            logger.success(f"Workplace Type Filter Applied : {mode}")

    def easy_apply(self):

        logger.info("Applying Filter : Easy Apply")

        # Try the standalone pill first (LinkedIn shows this inconsistently)
        pill = self.browser.page.locator(
            'button[aria-label="Easy Apply filter."]:visible'
        ).first

        if pill.count() > 0:
            if self._safe_click(pill, "Easy Apply"):
                self.browser.wait(2000)
                logger.success("Easy Apply Filter Applied")
                return

        # Fall back to the "All filters" panel toggle.
        # Its id has a random "ember" suffix, so locate by label text instead.

        if not self._open_all_filters_panel():
            return

        toggle_label = self.browser.page.locator(
            'label:visible:has-text("Toggle Easy Apply filter")'
        ).first

        if toggle_label.count() == 0:
            self._debug_dump_checkbox_inputs("easy-apply-modal")
            logger.error("Could not locate Easy Apply toggle inside 'All filters' panel. Skipping.")
            return

        if self._safe_click(toggle_label, "Easy Apply (toggle)"):
            self._click_show_results()
            self.browser.wait(2000)
            logger.success("Easy Apply Filter Applied (via All filters panel)")

    def sort_by(self, order="Most recent"):

        logger.info(f"Applying Sort : {order}")

        full_id = self.SORT_IDS.get(order)

        if full_id is None:
            logger.error(f"Unknown sort order '{order}'. Valid: {list(self.SORT_IDS)}")
            return

        if not self._open_all_filters_panel():
            return

        if self._select_by_id(full_id, order):
            self._click_show_results()
            self.browser.wait(2000)
            logger.success(f"Sort Applied : {order}")

    # =====================================================
    # Convenience : apply multiple filters in a single panel session
    # (faster than calling each method separately, since the panel
    # only needs to be opened once)
    # =====================================================

    def apply_filters(self, date_posted=None, experience=None, remote=None, easy_apply=False, sort_by=None):

        logger.info("Applying multiple filters in a single panel session...")

        if not self._open_all_filters_panel():
            return

        if date_posted:
            full_id = self.DATE_POSTED_IDS.get(date_posted)
            if full_id:
                if self._select_by_id(full_id, date_posted):
                    logger.success(f"  -> Date Posted set : {date_posted}")
                self.browser.wait(300)
            else:
                logger.error(f"  -> Unknown date_posted option '{date_posted}'")

        if experience:
            labels = self.EXPERIENCE_YEAR_MAP.get(experience, experience if isinstance(experience, list) else [experience])
            for label in labels:
                full_id = self.EXPERIENCE_IDS.get(label)
                if full_id:
                    if self._select_by_id(full_id, label):
                        logger.success(f"  -> Experience Level set : {label}")
                    self.browser.wait(300)
                else:
                    logger.error(f"  -> Unknown experience label '{label}'")

        if remote:
            full_id = self.REMOTE_IDS.get(remote)
            if full_id:
                if self._select_by_id(full_id, remote):
                    logger.success(f"  -> Workplace Type set : {remote}")
                self.browser.wait(300)
            else:
                logger.error(f"  -> Unknown remote mode '{remote}'")

        if easy_apply:
            toggle_label = self.browser.page.locator(
                'label:visible:has-text("Toggle Easy Apply filter")'
            ).first
            if toggle_label.count() > 0:
                if self._safe_click(toggle_label, "Easy Apply (toggle)"):
                    logger.success("  -> Easy Apply toggle set : ON")
                self.browser.wait(300)
            else:
                logger.warning("  -> Easy Apply toggle NOT FOUND in panel. Skipped.")
                self._debug_dump_checkbox_inputs("apply-filters-easy-apply")

        if sort_by:
            full_id = self.SORT_IDS.get(sort_by)
            if full_id:
                if self._select_by_id(full_id, sort_by):
                    logger.success(f"  -> Sort By set : {sort_by}")
                self.browser.wait(300)
            else:
                logger.error(f"  -> Unknown sort order '{sort_by}'")

        self._click_show_results()

        self.browser.wait(2000)

        logger.success("All requested filters applied.")