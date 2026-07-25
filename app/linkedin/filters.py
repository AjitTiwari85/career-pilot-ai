from utils.logger import logger


class LinkedInFilters:
    """
    All filters live inside LinkedIn's "All filters" side panel and are
    selected via their STABLE input IDs (discovered via live DOM inspection):

        Date posted      -> input#advanced-filter-timePostedRange-<code>
        Experience level -> input#advanced-filter-experience-<1-6>
        Remote/Workplace -> input#advanced-filter-workplaceType-<1-3>
        Sort by          -> input#advanced-filter-sortBy-<DD|R>
        Easy Apply       -> toggle input, id has a random "ember" suffix
                             (matched by prefix + label text instead)

    IDs are used instead of visible text because "Internship" appears as a
    label in BOTH the Experience Level section AND the Job Type section,
    so text-only matching could click the wrong checkbox.
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

    # Year-range shortcuts -> LinkedIn experience label(s)
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

    # =====================================================
    # Reusable low-level helpers
    # =====================================================

    def _safe_click(self, locator, label=""):
        """Click with automatic fallback to force-click on failure."""

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

    def _open_all_filters_panel(self):
        """Opens the 'All filters' side panel. No-op if already open AND usable."""

        # Don't just trust "Show results" visibility — a stale/partial panel
        # (e.g. after a previous failed close) can still show that button
        # while missing actual filter inputs. Confirm a real filter input
        # (Date Posted's "Any time" option, always present) exists too.
        show_results = self.browser.page.get_by_role("button", name="Show results", exact=False).first
        sample_input = self.browser.page.locator('input[id^="advanced-filter-timePostedRange-"]').first

        if show_results.count() > 0 and show_results.is_visible() and sample_input.count() > 0:
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

        self.browser.wait(2200)
        return True

    def _select_by_id(self, full_id, label_for_log=""):
        """Selects a checkbox/radio input inside the panel by its exact ID."""

        input_el = self.browser.page.locator(f'input[id="{full_id}"]').first

        if input_el.count() == 0:
            logger.error(f"Input id '{full_id}' not found ({label_for_log}).")
            return False

        try:
            input_el.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pass

        return self._safe_click(input_el, label_for_log or full_id)

    def _find_easy_apply_toggle(self):
        """
        Easy Apply's toggle id has a random 'ember' suffix that changes per
        session, so match by id-prefix + associated label text instead.
        """

        # Use a tag-agnostic selector: LinkedIn's toggle may be a real
        # <input>, or a <div>/<span role="switch">, so don't restrict to
        # "input[...]" — match ANY element whose id has this prefix.
        candidates = self.browser.page.locator('[id^="adToggle_ember"]')

        for i in range(candidates.count()):

            try:
                el = candidates.nth(i)
                input_id = el.get_attribute("id") or ""

                if not input_id:
                    continue

                label_loc = self.browser.page.locator(f'label[for="{input_id}"]')

                if label_loc.count() == 0:
                    continue

                label_text = label_loc.first.inner_text(timeout=500).strip()

                if "easy apply" in label_text.lower():
                    return el

            except Exception:
                continue

        return None

    def _click_show_results(self):
        """
        Clicks 'Show results' (or closest equivalent) to apply + close the panel.

        LinkedIn sometimes renders duplicate/hidden panel instances, so
        `.first` can resolve to a non-clickable hidden element and time out
        even though a real, visible button exists elsewhere on the page.
        We iterate through ALL matches (not just .first) for each candidate
        selector and click the first one that's actually visible.

        If every attempt fails, we force-close the panel via Escape as a
        fallback — otherwise the next filter method would see this stale
        "still open" panel and skip re-opening it fresh, silently failing
        to find that filter's inputs (since the panel content can be in a
        partial/loading state).
        """

        selectors = [
            ("role", "Show results"),
            ("role", "results"),
            ("css", 'button:visible:has-text("Show")'),
            ("role", "Apply"),
            ("role", "Done"),
        ]

        for kind, value in selectors:

            try:
                locator = (
                    self.browser.page.get_by_role("button", name=value, exact=False)
                    if kind == "role"
                    else self.browser.page.locator(value)
                )

                count = locator.count()

                for i in range(count):
                    candidate = locator.nth(i)
                    try:
                        if candidate.is_visible():
                            if self._safe_click(candidate, "Show results"):
                                return True
                    except Exception:
                        continue

            except Exception:
                continue

        logger.warning(
            "Could not find/click 'Show results'. Forcing panel closed via Escape "
            "so the next filter opens a fresh panel instead of a stale one."
        )

        try:
            self.browser.page.keyboard.press("Escape")
            self.browser.wait(500)
        except Exception:
            pass

        return False

    def _debug_dump_checkbox_inputs(self, context_name):
        """Diagnostic: lists every checkbox/radio/switch input + its label. Used on failure."""

        logger.warning(f"[{context_name}] Dumping checkbox/radio/switch inputs and their labels...")

        try:
            inputs = self.browser.page.locator(
                'input[type="checkbox"], input[type="radio"], [role="switch"]'
            )

            for i in range(min(inputs.count(), 80)):
                try:
                    el = inputs.nth(i)
                    input_id = el.get_attribute("id") or ""
                    label_text = ""

                    if input_id:
                        label_loc = self.browser.page.locator(f'label[for="{input_id}"]')
                        if label_loc.count() > 0:
                            label_text = label_loc.first.inner_text(timeout=500).strip().replace("\n", " ")

                    if label_text:
                        logger.warning(f"  [{i}] id='{input_id}' label='{label_text}'")

                except Exception:
                    continue

        except Exception as e:
            logger.warning(f"[{context_name}] Checkbox dump failed: {e}")

        self.browser.take_screenshot(f"debug-{context_name}")

    # =====================================================
    # Core : apply one or more (id, log_label) pairs in a single panel session
    # Every public filter method below is just a thin wrapper around this.
    # =====================================================

    def _apply_ids(self, id_label_pairs, success_summary):
        """
        id_label_pairs : list of (full_id, log_label) tuples to select.
        Opens the panel (if needed), selects each id, clicks Show results once.
        """

        if not self._open_all_filters_panel():
            return False

        applied_any = False

        for full_id, log_label in id_label_pairs:
            if self._select_by_id(full_id, log_label):
                applied_any = True
            self.browser.wait(300)

        if applied_any:
            self._click_show_results()
            self.browser.wait(2000)
            logger.success(success_summary)

        return applied_any

    # =====================================================
    # Public Filter Methods (one per filter, short & focused)
    # =====================================================

    def date_posted(self, option="Past 24 hours"):

        logger.info(f"Applying Filter : Date Posted ({option})")

        full_id = self.DATE_POSTED_IDS.get(option)

        if full_id is None:
            logger.error(f"Unknown date_posted option '{option}'. Valid: {list(self.DATE_POSTED_IDS)}")
            return

        self._apply_ids([(full_id, option)], f"Date Posted Filter Applied : {option}")

    def experience(self, level="0-2"):

        labels = self.EXPERIENCE_YEAR_MAP.get(level, level if isinstance(level, list) else [level])

        logger.info(f"Applying Filter : Experience Level ({level} -> {labels})")

        pairs = [
            (self.EXPERIENCE_IDS[label], label)
            for label in labels
            if label in self.EXPERIENCE_IDS
        ]

        if not pairs:
            logger.warning(f"No valid experience labels found for '{level}'.")
            return

        self._apply_ids(pairs, f"Experience Level Filter Applied : {labels}")

    def remote(self, mode="Remote"):

        logger.info(f"Applying Filter : Workplace Type ({mode})")

        full_id = self.REMOTE_IDS.get(mode)

        if full_id is None:
            logger.error(f"Unknown remote mode '{mode}'. Valid: {list(self.REMOTE_IDS)}")
            return

        self._apply_ids([(full_id, mode)], f"Workplace Type Filter Applied : {mode}")

    def sort_by(self, order="Most recent"):

        logger.info(f"Applying Sort : {order}")

        full_id = self.SORT_IDS.get(order)

        if full_id is None:
            logger.error(f"Unknown sort order '{order}'. Valid: {list(self.SORT_IDS)}")
            return

        self._apply_ids([(full_id, order)], f"Sort Applied : {order}")

    def easy_apply(self):

        logger.info("Applying Filter : Easy Apply")

        # LinkedIn sometimes shows this as a standalone pill outside the panel
        pill = self.browser.page.locator('button[aria-label="Easy Apply filter."]:visible').first

        if pill.count() > 0:
            if self._safe_click(pill, "Easy Apply"):
                self.browser.wait(2000)
                logger.success("Easy Apply Filter Applied")
                return

        # Fallback : find it inside the "All filters" panel
        if not self._open_all_filters_panel():
            return

        toggle = self._find_easy_apply_toggle()

        if toggle is None:
            self._debug_dump_checkbox_inputs("easy-apply-modal")
            logger.error("Could not locate Easy Apply toggle. Skipping.")
            return

        if self._safe_click(toggle, "Easy Apply (toggle)"):
            self._click_show_results()
            self.browser.wait(2000)
            logger.success("Easy Apply Filter Applied (via All filters panel)")

    # =====================================================
    # Convenience : apply multiple filters in ONE panel session
    # (faster than calling each method separately)
    # =====================================================

    def apply_filters(self, date_posted=None, experience=None, remote=None, easy_apply=False, sort_by=None):

        logger.info("Applying multiple filters in a single panel session...")

        if not self._open_all_filters_panel():
            return

        pairs = []

        if date_posted and date_posted in self.DATE_POSTED_IDS:
            pairs.append((self.DATE_POSTED_IDS[date_posted], f"Date Posted: {date_posted}"))

        if experience:
            labels = self.EXPERIENCE_YEAR_MAP.get(experience, experience if isinstance(experience, list) else [experience])
            for label in labels:
                if label in self.EXPERIENCE_IDS:
                    pairs.append((self.EXPERIENCE_IDS[label], f"Experience: {label}"))

        if remote and remote in self.REMOTE_IDS:
            pairs.append((self.REMOTE_IDS[remote], f"Remote: {remote}"))

        if sort_by and sort_by in self.SORT_IDS:
            pairs.append((self.SORT_IDS[sort_by], f"Sort: {sort_by}"))

        for full_id, log_label in pairs:
            if self._select_by_id(full_id, log_label):
                logger.success(f"  -> {log_label} set")
            self.browser.wait(300)

        if easy_apply:
            toggle = self._find_easy_apply_toggle()
            if toggle is not None:
                if self._safe_click(toggle, "Easy Apply (toggle)"):
                    logger.success("  -> Easy Apply toggle set : ON")
                self.browser.wait(300)
            else:
                logger.warning("  -> Easy Apply toggle NOT FOUND in panel. Skipped.")
                self._debug_dump_checkbox_inputs("apply-filters-easy-apply")

        self._click_show_results()
        self.browser.wait(2000)

        logger.success("All requested filters applied.")