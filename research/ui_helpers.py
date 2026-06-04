"""Small UI helpers shared across the Streamlit pages."""

import streamlit as st
import streamlit.components.v1 as components


def scroll_to_top(view_key=None):
    """Scroll the main content area back to the top of the page.

    Streamlit keeps the browser scroll position across `st.switch_page` and
    `st.rerun`, so a student who scrolled down to reach a button lands on the
    *next* page still scrolled down. Calling this near the top of a page resets
    the scroll so they see the top again.

    If ``view_key`` is given, the scroll only fires when that key changes since
    the last call. Pass a key that identifies the current view (e.g. the
    question number) so in-place reruns — like a form validation error — don't
    yank the page away from where the student is typing. Pass nothing to scroll
    on every render.
    """
    if view_key is not None:
        if st.session_state.get("_scroll_view") == view_key:
            return
        st.session_state["_scroll_view"] = view_key

    components.html(
        """
        <script>
            const scroll = () => {
                const doc = window.parent.document;
                const els = [
                    doc.querySelector('section.main'),
                    doc.querySelector('[data-testid="stMain"]'),
                    doc.querySelector('[data-testid="stAppViewContainer"]'),
                    doc.scrollingElement,
                    doc.documentElement,
                    doc.body,
                ];
                for (const el of els) {
                    if (el) { try { el.scrollTo({top: 0, left: 0}); } catch (e) {} }
                }
                try { window.parent.scrollTo(0, 0); } catch (e) {}
            };
            scroll();
            setTimeout(scroll, 50);
        </script>
        """,
        height=0,
    )
