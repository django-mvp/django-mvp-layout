"""Views for the test pages."""

from django.views.generic import TemplateView

from tests.page_context import NESTED, preview_context

# How the sized page bounds its layout, by the URL's size: the styles of the
# box the layout is in, and of the layout itself. A dialog is capped the way
# daisyUI caps its modal box, and lays its content out as a flex column.
SIZES = {
    "none": ("", ""),
    "height": ("", "height: 320px"),
    "max-height": ("", "max-height: 320px"),
    "dialog": (
        "max-height: 360px; padding: 24px; box-sizing: border-box;"
        " overflow-y: auto; display: flex; flex-direction: column",
        "",
    ),
}


class LayoutPage(TemplateView):
    """Render a test page, with what the pages that need it read from the URL."""

    def get_context_data(self, **kwargs):
        """Add what a page reads from the URL, and enough rows to make one heavy."""
        context = super().get_context_data(**kwargs)
        context["view"] = self.request.GET.get("view")
        context["rows"] = range(1900)
        context["tall"] = "tall" in self.request.GET
        context["narrow"] = "narrow" in self.request.GET
        context["box_style"], context["layout_style"] = SIZES[
            self.request.GET.get("size", "none")
        ]
        return context


class ComponentPage(TemplateView):
    """Render a component test page with what the prototype's demo page showed."""

    def get_context_data(self, **kwargs):
        """Add the playground's preview and the nested page's data."""
        context = super().get_context_data(**kwargs)
        context.update(preview_context(self.request.GET))
        context.update(NESTED)
        if self.template_name.endswith("playground.html"):
            # The preview gets the page's full width, and the reference starts
            # closed and remembers its own state.
            context.update(
                page_width="max-w-none",
                aside_persist="demo-reference",
                aside_closed=True,
            )
        return context
