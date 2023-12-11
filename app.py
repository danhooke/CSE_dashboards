import dashboard_funcs as dfs
import xarray as xr
import os
import glob
import hvplot.xarray
import holoviews as hv
import panel as pn

# import bokeh
import panel.widgets as pnw
from pooch import Unzip

css = """
* {
  font-family: "Roboto", sans-serif;
  background: #f0f3f6;
  }
.bk-root .bk-btn-default {
  background: #f0f3f6;
  border-color: #f0f3f6;
  color: #f0f3f6;
  }
.bk-panel-models-layout-Column {
  background: #f0f3f6;
  }
.bk-layer.bk-events{
  background: #f0f3f6;
  }

"""
pn.extension(raw_css=[css])
from bokeh.themes.theme import Theme

theme = Theme(
    json={
        "attrs": {
            "figure": {"border_fill_color": "#f0f3f6"},
        }
    }
)
hv.renderer("bokeh").theme = theme


def make_ds(
    # type,
    ind,
    ssp="ssp2",
):
    """
    Make a dataset of the given indicator.
    """
    vars = ["abs", "diff", "score"]
    files = dfs.CSE_pooch_v03.fetch("precipitation.zip", processor=Unzip())
    fp = os.path.dirname(files[1])
    ds = xr.merge(
        [
            xr.concat(
                [
                    xr.open_dataarray(f).rename(f"{var}")
                    for f in glob.glob(fp + rf"\*{ind}*{var}*")
                ],
                dim="threshold",
            )
            for var in vars
        ]
    )
    ds = ds.rename({"diff": "difference"})
    return ds


input_ticker = pn.widgets.Select(name="Indicator", options=["cdd", "pr_r10"])
dfi = pn.bind(make_ds, input_ticker)  # .interactive(loc="left")
ind = "pr_r10"
ds = make_ds(ind)
info = dfs.get_info()
ind_min = info["indicators"]["precip"]["r10"]["ind_min"]
ind_max = info["indicators"]["precip"]["r10"]["ind_max"]
diff_min = info["indicators"]["precip"]["r10"]["diff_min"]
diff_max = info["indicators"]["precip"]["r10"]["diff_max"]
abs_cmap = info["indicators"]["precip"]["r10"]["ind_cmap"]
diff_cmap = info["indicators"]["precip"]["r10"]["diff_cmap"]
long_name = info["indicators"]["precip"]["r10"]["long_name"]
# template = pn.template.BootstrapTemplate(favicon=r"c:\Users\danho\OneDrive\Desktop\DH_dot_com\logo_v03.svg")
slider = pnw.DiscreteSlider(
    name="GMT change", options=[1.2, 1.5, 2.0, 2.5, 3.0, 3.5], value=1.2
)
abs_map = (
    ds.abs.interactive.sel(threshold=slider)
    .hvplot(
        title="Absolute",
        x="lon",
        y="lat",
        cmap=abs_cmap,
        clim=(ind_min, ind_max),
        width=400,
        xlabel="",
        ylabel="",
    )
    .hist()
)
diff_map = (
    ds.difference.interactive.sel(threshold=slider)
    .hvplot(
        title="Difference",
        x="lon",
        y="lat",
        cmap=diff_cmap,
        clim=(diff_min, diff_max),
        width=400,
        xlabel="",
        ylabel="",
    )
    .hist()
)
score_map = (
    ds.score.interactive.sel(threshold=slider)
    .hvplot(
        title="Score",
        x="lon",
        y="lat",
        cmap="magma_r",
        clim=(0, 3),
        width=400,
        xlabel="",
        ylabel="",
    )
    .hist()
)
new_dboard = pn.Column(
    pn.Row(
        pn.panel(
            '<span style="color:black; font-weight:800; font-size:24px">Hello</span>',
            width=400,
        )
    ),
    pn.Row(
        input_ticker,
        # dfi,
        # pn.pane.Markdown(dfi)
    ),
    abs_map.widgets(),
    pn.Row(abs_map.panel(), diff_map.panel()),
    pn.Row(score_map.panel()),
).servable()
