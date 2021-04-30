#
# phenoptr(Reports) Installation for Windows
# Christian Rickert, 2021-04-29
#

# install R 4.0.5
# see: https://cran.r-project.org/bin/windows/base/

# install Rtools 40
# see: https://cran.r-project.org/bin/windows/Rtools/

# install RStudio Desktop 1.4.1106
# see: https://www.rstudio.com/products/rstudio/download/#download

#
# WARNING: Do NOT install or update (from source) packages!
#

# install devtools package
if ( !require("devtools") )
  install.packages("devtools")

# phenoptr
# see: https://akoyabio.github.io/phenoptr/

# install phenoptr plugin from GitHub
# hint: new stable versions are located in the @master branch,
# and new development versions are located in the @9000 branch
devtools::install_github("akoyabio/phenoptr@master")
#devtools::install_github("akoyabio/phenoptr@9000")

# install tiff package for phenoptr
# see: https://github.com/akoyabio/tiff/tree/master#installation
devtools::install_github("akoyabio/tiff@master")

# install rtree package for phenoptr
# see: https://github.com/akoyabio/rtree/tree/master#installation
devtools::install_github("akoyabio/rtree@BH_1.75")

# phenoptrReports
# see: https://akoyabio.github.io/phenoptrReports/

# install phenoptrReports plugin from GitHub
# hint: new stable versions are located in the @master branch,
# and new development versions are located in the @9000 branch
devtools::install_github("akoyabio/phenoptrReports@master")
#devtools::install_github("akoyabio/phenoptrReports@9000")
