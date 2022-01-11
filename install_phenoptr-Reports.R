#
# phenoptr(Reports) Installation for Windows
# Christian Rickert, 2022-01-11
#

# install R 4.1.2 or later
# see: https://cran.r-project.org/bin/windows/base/

# install Rtools 4.0.0 or later
# see: https://cran.r-project.org/bin/windows/Rtools/

# install RStudio Desktop 2021.09.2+382 or later
# see: https://www.rstudio.com/products/rstudio/download/#download

#
# WARNING: Do NOT install or update (from source) packages!
#          Select "3: None" (type "3" and hit Enter/Return)
#          when prompted to update to more recent packages.

# install devtools package
install.packages("devtools")

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
devtools::install_github("akoyabio/phenoptrReports@main")
#devtools::install_github("akoyabio/phenoptrReports@9000")
