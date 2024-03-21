#
# Premessa Installation for Windows
# Christian Rickert, 2024-03-21
#

# install R 4.3.3 for Windows
# see: https://cran.r-project.org/bin/windows/base/

# install Rtools43 for Windows
# see: https://cran.r-project.org/bin/windows/Rtools/rtools43/rtools.html

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
#concatenate_fcs_files(list.files(path = ".", pattern="\\.fcs$"), output.file = "concatenated.FCS")

# free unused memory
#gc()
