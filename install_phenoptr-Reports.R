#
# phenoptr(Reports) Installation for Windows
# Christian Rickert, 2023-11-13
#

# install R 4.1.0 or later
# see: (Windows)  https://cran.r-project.org/bin/windows/base/old/

# install Rtools 4.0 or later
# see: (Windows)  https://cran.r-project.org/bin/windows/Rtools/

# install RStudio Desktop 2022.07.0 or later
# see: https://posit.co/download/rstudio-desktop/

#
# WARNING: Do NOT install or update (from source) packages!
#          Select "3: None" (type "3" and hit Enter/Return)
#          when prompted to update to more recent packages.

# install devtools package
install.packages("devtools")

# phenoptr
# see: https://akoyabio.github.io/phenoptr/

# install phenoptr plugin from GitHub
devtools::install_github("christianrickert/phenoptr")

# install tiff package for phenoptr
# see: https://github.com/s-u/tiff
install.packages("tiff")

# install rtree package for phenoptr
# see: https://github.com/akoyabio/rtree/tree/master#installation
devtools::install_github("akoyabio/rtree@master")

# phenoptrReports
# see: https://akoyabio.github.io/phenoptrReports/

# install phenoptrReports plugin from GitHub
devtools::install_github("christianrickert/phenoptrReports")
