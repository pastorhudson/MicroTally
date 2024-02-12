[![Build and Release](https://github.com/pastorhudson/ProPresenter-PCO-Live-Auto-Control/actions/workflows/main.yml/badge.svg)](https://github.com/pastorhudson/ProPresenter-PCO-Live-Auto-Control/actions/workflows/main.yml)
# Title
### What is this?
This is a template for auto building python packages for windows mac and linux.

### Demo Video
Add video here


### Download
- #### The latest download is always [here](https://github.com/pastorhudson/ProPresenter-PCO-Live-Auto-Control/releases/latest)
- #### You can see the changelog [here](https://github.com/pastorhudson/ProPresenter-PCO-Live-Auto-Control/blob/v1.1.2/CHANGELOG.md)

### Setup

- Add versions to CHANGELOG.md like this:
```editorconfig
# Changelog
All notable changes to this project will be documented in this file.

## v1.0.0
### Changes
 - First Release
```

A config.ini is provided in the src/utils.py

```editorconfig
[app]
;Get your Planning Center application_id and secret at https://api.planningcenteronline.com/oauth/applications
application_id = pco_app_id
secret = pco_app_secret
;Default is localhost 127.0.0.1 this is for running the program on the same machine as ProPresenter
pro_presenter_ip = 127.0.0.1
pro_presenter_port = 50001
```

TO add a release put:
Release: vX.X.X in the commit message

Edit the workflow to change the executable name