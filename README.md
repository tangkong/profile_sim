# SSRL beamline 1-5 simulation startup scripts
Template for beamline Bluesky collection profile. To use, clone this repository and make modifications as necessary

## Installation Instructions
### Customize bash
Copy contents of /bin into user's /bin or ~/.bashrc file.  This will set the ipython profile to auto-run bluesky and the associated configuration files included in this repo

### Load ipython profiles
Copy all folders into ~/.ipython 

### Starting ipython profile 
`ipython --profile=sim`

or if .bashrc alias has been configured correctly

`sim`
