import xarray as xr
import os
import glob
import yaml
import pooch
import holoviews as hv
import panel as pn
import panel.widgets as pnw
from pooch import Unzip
from bokeh.themes.theme import Theme

import hvplot.xarray

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
# pn.config.sizing_mode = "stretch_width"

theme = Theme(
    json={
        "attrs": {
            "figure": {"border_fill_color": "#f0f3f6"},
        }
    }
)
hv.renderer("bokeh").theme = theme

CSE_pooch_v03 = pooch.create(
    base_url="doi:10.5281/zenodo.10212339/",
    path=pooch.os_cache("CSE"),
    registry={
        "land.zip": "5c6fa81a541b6be59278f5ac5de0ddeff5ca48ffee1963293521168010b51cf8",
        "temperature.zip": "c5e20f83587f893187f934251e4627e42b3eef6208ad7a062800990c89b370e9",
        "precipitation.zip": "6c27b53d42a7b1df814b346b36e2d7b63920e3b2c649c8ce45e2b4ca84e3013f",
        "hydrology.zip": "7cd9ae348003d03ca63b0f08888e00c45c1d3b71250b2ba8fc32be06d1e88f7f",
        "energy.zip": "a98274119423af7425c5de82e809fea5dcd92250ffc9aaa641670247adfb04be",
        "air_pollution.zip": "ba208c2b057250f3741bbb3b89d9ff257e66230383542622d99107ade02a015d",
    },
)
temp_inds = [
    "hw_95_10",
    "hw_95_3",
    "hw_95_5",
    "hw_95_7",
    "hw_97_10",
    "hw_97_3",
    "hw_97_5",
    "hw_97_7",
    "hw_99_10",
    "hw_99_3",
    "hw_99_5",
    "hw_99_7",
    "tr20",
]

energy_inds = [
    "sdd_c_24p0",
    "sdd_c",
    "sdd_c_18p3",
    "sdd_c_20p0",
]

hydro_inds = [
    "dri_dis",
    "dri_qtot",
    "iavar_dis",
    "iavar_qtot",
    "seas_dis",
    "seas_qtot",
    "wsi",
]

precip_inds = ["cdd", "pr_r10", "pr_r20", "pr_r95p", "pr_r99p", "sdii"]

names = dict(
    dri_dis="Drought severity (discharge)",
    dri_qtot="Drought severity (runoff)",
    iavar_dis="Interannual variability (discharge)",
    iavar_qtot="Interannual variability (runoff)",
    seas_dis="Seasonality (discharge)",
    seas_qtot="Seasonality (runoff)",
    wsi="Water stress index",
    cdd="Consecutive dry days",
    pr_r10="Heavy precipitation days",
    pr_r20="Very heavy precipitation days",
    pr_r95p="Wet days",
    pr_r99p="Very wet days",
    sdii="Precipitation intensity index",
    hw_95_10="Heat wave events (95th percentile, 10 days)",
    hw_95_3="Heat wave events (95th percentile, 3 days)",
    hw_95_5="Heat wave events (95th percentile, 5 days)",
    hw_95_7="Heat wave events (95th percentile, 7 days)",
    hw_97_10="Heat wave events (97th percentile, 10 days)",
    hw_97_3="Heat wave events (97th percentile, 3 days)",
    hw_97_5="Heat wave events (97th percentile, 5 days)",
    hw_97_7="Heat wave events (97th percentile, 7 days)",
    hw_99_10="Heat wave events (99th percentile, 10 days)",
    hw_99_3="Heat wave events (99th percentile, 3 days)",
    hw_99_5="Heat wave events (99th percentile, 5 days)",
    hw_99_7="Heat wave events (99th percentile, 7 days)",
    tr20="Tropical nights",
    sdd_c_24p0="Cooling degree days (24°C)",
    # sdd_c="Cooling degree days (26°C)",
    sdd_c_18p3="Cooling degree days (18.3°C)",
    sdd_c_20p0="Cooling degree days (20°C)",
)


def match_name(long_name):
    for s_name, l_name in names.items():
        if l_name == long_name:
            ind = s_name
    return ind


def make_ds(
    l_name,
):
    """
    Make a dataset of the given indicator.
    """
    ind = match_name(l_name)
    vars = ["abs", "diff", "score"]
    if ind in precip_inds:
        folder = "precipitation.zip"
    elif ind in temp_inds:
        folder = "temperature.zip"
    elif ind in energy_inds:
        folder = "energy.zip"
    elif ind in hydro_inds:
        folder = "hydrology.zip"
    files = CSE_pooch_v03.fetch(folder, processor=Unzip())
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


def get_info():
    """
    Read information from the yaml file into a dictionary.
    """
    with open("indicator_info.yml", "r") as f:
        return yaml.full_load(f)


info = get_info()


def get_plot_info(ind, info=info):
    ind = match_name(ind)
    if ind == "tr20":
        ind = "tr20"
    elif ind in temp_inds:
        ind = "hw"
    keys = info["indicators"].keys()
    for key in keys:
        sub_keys = info["indicators"][key].keys()
        for sub_key in sub_keys:
            short_name = info["indicators"][key][sub_key]["short_name"]
            if ind == short_name:
                ind_info = info["indicators"][key][sub_key]
    return ind_info


def make_score_map_test(ind, t):
    ds = make_ds(ind)
    ind_info = get_plot_info(ind)
    score_map = (
        ds["score"]
        .sel(threshold=t)
        .hvplot(
            x="lon",
            y="lat",
            xlabel="",
            ylabel="",
            width=600,
            cmap="magma_r",
            clim=(0, 6),
            title=ds.attrs["long_name"]
            + " risk score at "
            + str(t)
            + "°C (Data: Werning et al. 2023)",
        )
        .hist()
    )
    abs_map = (
        ds["abs"]
        .sel(threshold=t)
        .hvplot(
            x="lon",
            y="lat",
            xlabel="",
            ylabel="",
            width=600,
            cmap=ind_info["ind_cmap"],
            clim=(ind_info["ind_min"], ind_info["ind_max"]),
            title=ds.attrs["long_name"]
            + " absolute values at "
            + str(t)
            + "°C (Data: Werning et al. 2023)",
        )
        .hist()
    )
    diff_map = (
        ds["difference"]
        .sel(
            threshold=t,
            # stats="mean"
        )
        .hvplot(
            x="lon",
            y="lat",
            xlabel="",
            ylabel="",
            cmap=ind_info["diff_cmap"],
            clim=(ind_info["diff_min"], ind_info["diff_max"]),
            width=600,
            title=ds.attrs["long_name"]
            + " difference at "
            + str(t)
            + "°C (Data: Werning et al. 2023)",
        )
        .hist()
    )
    layout = pn.Column(
        pn.Row(abs_map, diff_map),
        pn.Row(
            score_map,
        ),
    )
    return layout


slider = pnw.DiscreteSlider(
    name="GMT change", options=[1.2, 1.5, 2.0, 2.5, 3.0, 3.5], value=1.2
)
input_ticker = pn.widgets.Select(
    name="Indicator",
    options=list(names.values()),
)


simple_map_test = pn.bind(make_score_map_test, ind=input_ticker, t=slider)
pn.Column(
    pn.Row(
        pn.panel(
            '<span style="color:black; font-weight:800; font-size:32px">Climate Impacts</span>',
        )
    ),
    pn.Row(
        pn.panel(
            '<span style="color:black; font-weight:600; font-size:24px">Data: </span><span style="color:black; font-weight:400; font-size:24px">Werning et al. (2023) </span><a href="https://zenodo.org/doi/10.5281/zenodo.7971429" target="_blank"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.7971429.svg" alt="DOI"/></a>'
        )
    ),
    input_ticker,
    slider,
    simple_map_test,
).servable()
