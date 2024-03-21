#
# phenoptr(Reports) Installation for Windows
# Christian Rickert, 2024-03-20
#

# install R 4.3.3 or later
# see: (Windows)  https://cran.r-project.org/bin/windows/base/old/

# install Rtools 4.3 or later
# see: (Windows)  https://cran.r-project.org/bin/windows/Rtools/

# install RStudio Desktop 2022.12.1 or later
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

# phenoptrReports
# see: https://akoyabio.github.io/phenoptrReports/

# install phenoptrReports plugin from GitHub
devtools::install_github("christianrickert/phenoptrReports")
