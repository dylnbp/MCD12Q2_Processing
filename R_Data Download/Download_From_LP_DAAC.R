# ------------------------------------------------------------------------------------------------ #
# Check for required packages, install if not previously installed
if ("sys" %in% rownames(installed.packages()) == FALSE) {install.packages("sys")}
if ("getPass" %in% rownames(installed.packages()) == FALSE) { install.packages("getPass")}
if ("httr" %in% rownames(installed.packages()) == FALSE) { install.packages("httr")}

# Load necessary packages into R
library(sys)
library(getPass)
library(httr)
# ---------------------------------SET UP ENVIRONMENT--------------------------------------------- #
# # IMPORTANT: Update the line below if you want to download to a different directory (ex: "c:/data/")
# dl_dir <- Sys.getenv("HOME")                                 # Set dir to download files to
# setwd(dl_dir)                                                # Set the working dir to the dl_dir
# usr <- file.path(Sys.getenv("USERPROFILE"))                  # Retrieve home dir (for netrc file)
# if (usr == "") {usr = Sys.getenv("HOME")}                    # If no user profile exists, use home
# netrc <- file.path(usr,'.netrc', fsep = .Platform$file.sep)  # Path to netrc file
# ------------------------------------------------------------------------------------------------- #

directory_name=getwd()
print(directory_name)

linksPath <- "MCD12Q2_V6_Links"
netrcPath <- "netrc_file"
downloadedData <- "Downloaded_MCD12Q2_V6_Data"
 
dl_dir <- paste(directory_name,"\\",downloadedData,sep="")   # Set dir to download files to
setwd(dl_dir)                                                
usr <- paste(directory_name,"\\",netrcPath,sep="")                 
netrc <- file.path(usr,'.netrc', fsep = .Platform$file.sep)  # Path to netrc file

# ------------------------------------CREATE .NETRC FILE------------------------------------------ #
# # If you already have a .netrc file with your Earthdata Login credentials stored in your home
# # directory, this portion will be skipped. Otherwise you will be prompted for your NASA Earthdata
# # Login Username/Password and a netrc file will be created to store your credentials (in home dir)
# if (file.exists(netrc) == FALSE || grepl("urs.earthdata.nasa.gov", readLines(netrc)) == FALSE) {
#   netrc_conn <- file(netrc)
#   
#   # User will be prompted for NASA Earthdata Login Username and Password below
#   writeLines(c("machine urs.earthdata.nasa.gov",
#                sprintf("login %s", getPass(msg = "Enter NASA Earthdata Login Username \n (or create an account at urs.earthdata.nasa.gov) :")),
#                sprintf("password %s", getPass(msg = "Enter NASA Earthdata Login Password:"))), netrc_conn)
#   close(netrc_conn)
# }
# ------------------------------------------------------------------------------------------------- #

linksFolderDir <- paste(directory_name,"\\",linksPath,sep="")
linksFile <- list.files(linksFolderDir, pattern=".txt")

linksFileName <- file.path(paste(linksFolderDir,"\\",linksFile,sep=""))
files <- readLines(linksFileName)

for (i in 1:length(files)) {
  filename <-  tail(strsplit(files[i], '/')[[1]], n = 1) # Keep original filename
  
  # Write file to disk (authenticating with netrc) using the current directory/filename
  response <- GET(files[i], write_disk(filename, overwrite = TRUE), progress(),
                  config(netrc = TRUE, netrc_file = netrc), set_cookies("LC" = "cookies"))
  
  # Check to see if file downloaded correctly
  if (response$status_code == 200) {
    print(sprintf("%s downloaded at %s", filename, dl_dir))
  } else {
    print(sprintf("%s not downloaded. Verify that your username and password are correct in %s", filename, netrc))
  }
}
