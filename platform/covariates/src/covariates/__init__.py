"""Àlááfìa covariate stack.

MODEL-support layer. Assembles auxiliary predictors at LGA level (774
rows, keyed to the geography spine) for small-area estimation of the
survey indicators.

Tier A — derived from data already in the repo (GRID3 settlements +
building footprints, GRID3 health facilities, spine geometry). No
downloads. ~20 predictors: settlement/building density, built-up
fraction, urbanisation, facility access, geometry, crude accessibility.

Tier B — raster zonal statistics (WorldPop population + age structure,
night-lights, travel time). Needs the `raster` extra; wired but optional.
"""

__version__ = "0.1.0"
