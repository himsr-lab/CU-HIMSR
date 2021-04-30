#
# Premessa Installation for Windows
# Christian Rickert, 2021-04-29
#

# install R 4.0.4
# see: https://cran.r-project.org/bin/windows/base/

# install RStudio Desktop 1.4.1106
# see: https://www.rstudio.com/products/rstudio/download/#download

#
# WARNING: Do NOT install or update (from source) packages!
#

# install devtools package
install.packages("devtools")

# install Biocmanager
# see: http://bioconductor.org/install/
install.packages("BiocManager")

# install Bioconductor core packages
BiocManager::install()

# install flowCore package
BiocManager::install(c("flowCore"))

# install Premessa
# see: https://github.com/ParkerICI/premessa
devtools::install_github("ParkerICI/premessa")

# run Premessa
library(premessa)
paneleditor_GUI()
