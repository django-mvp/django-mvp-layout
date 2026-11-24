"""Views for the test pages."""

from django.views.generic import TemplateView


class LayoutPage(TemplateView):
    """Render a test page, with what the pages that need it read from the URL."""

    def get_context_data(self, **kwargs):
        """Add what a page reads from the URL, and enough rows to make one heavy."""
        context = super().get_context_data(**kwargs)
        context["view"] = self.request.GET.get("view")
        context["rows"] = range(3000)
        context["tall"] = "tall" in self.request.GET
        return context
