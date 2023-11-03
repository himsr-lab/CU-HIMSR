#
# phenoptr(Reports) Installation for Windows
# Christian Rickert, 2023-11-03
#

# install R 4.1.3 (later version not supported)
# see: (Windows)  https://cran.r-project.org/bin/windows/base/old/

# install Rtools 4.0 or later
# see: (Windows)  https://cran.r-project.org/bin/windows/Rtools/

# install RStudio Desktop 2022.12 or later
# see: https://www.rstudio.com/products/rstudio/download/#download

#
# WARNING: Do NOT install or update (from source) packages!
#          Select "3: None" (type "3" and hit Enter/Return)
#          when prompted to update to more recent packages.

# install devtools package
install.packages("devtools")

# install httpuv binary for Windows
install.packages("httpuv", type = "win.binary")

# install archived CRAN package spatstat.core
# see: https://github.com/akoyabio/phenoptr/issues/21#issuecomment-1366595082
spatstat_core_url <- "https://cran.r-project.org/src/contrib/Archive/spatstat.core/spatstat.core_2.4-4.tar.gz"
spatstat_core_pkgFile <- "spatstat.core_2.4-4.tar.gz"
download.file(url = spatstat_core_url, destfile = spatstat_core_pkgFile)
install.packages(pkgs=spatstat_core_pkgFile, type="source", repos=NULL)

# phenoptr
# see: https://akoyabio.github.io/phenoptr/

# install phenoptr plugin from GitHub
# hint: versions compatible with inForm version 2.5 (or earlier)
# are located in the main branch, while versions compatible
# with inForm 2.6 (or later) are located in the 9000 branch
#devtools::install_github("akoyabio/phenoptr@main")
devtools::install_github("akoyabio/phenoptr@9000")

# install tiff package for phenoptr
# see: https://github.com/s-u/tiff
install.packages("tiff")

# install rtree package for phenoptr
# see: https://github.com/akoyabio/rtree/tree/master#installation
devtools::install_github("akoyabio/rtree@master")

# phenoptrReports
# see: https://akoyabio.github.io/phenoptrReports/

# install phenoptrReports plugin from GitHub
# hint: new stable versions are located in the main branch,
# and new development versions are located in the @9000 branch
#devtools::install_github("akoyabio/phenoptrReports@main")
devtools::install_github("akoyabio/phenoptrReports@9000")
