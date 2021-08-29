#
# Premessa Installation for Windows
# Christian Rickert, 2021-08-29
#

# install R 4.0.5
# see: https://cran.r-project.org/bin/windows/base/

# install RStudio Desktop 1.4.1106
# see: https://www.rstudio.com/products/rstudio/download/#download

#
# WARNING: Do NOT install or update (from source) packages!
#

# set library location explicitly (customized library installation only)
#.libPaths( c(file.path("C:", "Program Files", "R", "R-4.0.5", "library", fsep=.Platform$file.sep)) )

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

# set current working directory
#setwd(file.path("C:", "Users", "HIMSR staff", "Desktop", "data", fsep=.Platform$file.sep))

# concatenate all FCS files in current folder (case-sensitive file names)
#concatenate_fcs_files(list.files(path = ".", pattern="\\.fcs$"), output.file = "concatenated.fcs")

# free unused memory
#gc()
