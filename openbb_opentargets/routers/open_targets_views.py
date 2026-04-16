"""Views for the open_targets extension."""

# pylint: disable=import-outside-toplevel,too-few-public-methods

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure


class OpenTargetsViews:
    """open_targets Views."""

    @staticmethod
    def open_targets_target_associated_diseases(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Horizontal bar of diseases by overall association score."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        data = kwargs["obbject_item"]
        rows = sorted(
            data, key=lambda d: d.overall_score or 0, reverse=True
        )[:25]
        fig = OpenBBFigure()
        fig.add_bar(
            x=[d.overall_score for d in rows],
            y=[d.disease_name or d.disease_id for d in rows],
            orientation="h",
        )
        fig.update_layout(
            yaxis={"autorange": "reversed"},
            xaxis_title="Overall association score",
        )
        content = fig.show(external=True).to_plotly_json()
        return fig, content

    @staticmethod
    def open_targets_disease_associated_targets(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Horizontal bar of targets by overall association score."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        data = kwargs["obbject_item"]
        rows = sorted(
            data, key=lambda d: d.overall_score or 0, reverse=True
        )[:25]
        fig = OpenBBFigure()
        fig.add_bar(
            x=[d.overall_score for d in rows],
            y=[d.target_symbol or d.target_id for d in rows],
            orientation="h",
        )
        fig.update_layout(
            yaxis={"autorange": "reversed"},
            xaxis_title="Overall association score",
        )
        content = fig.show(external=True).to_plotly_json()
        return fig, content
