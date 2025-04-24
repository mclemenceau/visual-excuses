# Visual Excuses

Once a package is uploaded to the Ubuntu archive (dput) it triggers a series of tests and rebuilds across multiple packages in the archive.
Said package won't be able to migrate until it has build properly and all its dependencies have had successful tests

This is a very simple view but this is what we call package migration.

When a package doesn't migrate, one would wonder why? what is its excuse?

Browsing and looking at https://people.canonical.com/~ubuntu-archive/proposed-migration/update_excuses.html can give excellent insight and help resolve the problem right away but in a lot of case, it could take a long time to find why a package is not migrating due the amount of packages trying to migrate at the same time and blocking each others

Wouldn't it be great to have a visual representation of these excuses?

## introducing visual-excuses

This tool leverage the excuses database located here https://people.canonical.com/~ubuntu-archive/proposed-migration/update_excuses.yaml.xz

This tool also uses the package per team mapping relevant to Canonical's internal teams which could help to show excuses per team. The content comes from http://reqorts.qa.ubuntu.com/reports/m-r-package-team-mapping.html


Finally this python program leverage pyvis python library
https://github.com/WestHealth/pyvis
https://pyvis.readthedocs.io/en/latest/

## Installation

visual is available as a snap and installing it should be as simple as
```
$> snap install visual-excuses
```

Otherwise it can also be installer as a standard pip python package

```
$> git clone https://github.com/mclemenceau/visual-excuses.git
$> cd visual-excuses
$> pip3 install .
```

## Usage
First let's look at the help menu and all the options available
```
$> visual-excuses --help
usage: visual-excuses [-h] [--inspect INSPECT] [--name NAME] [--component COMPONENT] [--team TEAM] [--ftbfs] [--min-age MIN_AGE] [--max-age MAX_AGE] [--limit LIMIT] [--reverse] [--json]

Ubuntu Excuses (Proposed Migration) Viewer

options:
  -h, --help            show this help message and exit
  --inspect INSPECT     Get details about a specific package
  --name NAME           Regex to filter package names (case-insensitive)
  --component COMPONENT
                        Archive component (main, restricted, universe, multivere)
  --team TEAM           Show only packages subscribed by this Ubuntu team
  --ftbfs               Show only FTBFS packages
  --min-age MIN_AGE     Only include packages at least this many days old
  --max-age MAX_AGE     Only include packages no older than this many days
  --limit LIMIT         Limit the number of results shown
  --reverse             Show excuses from older to more recent
  --json                Output in JSON format
```
Then here is a couple different ways to call visual-excuses
``` bash
# To show all the excuses
$> visual-excuses

# To only show the excuses in main
$> visual-excuses --component main

# To only show the excuses in universe for the last 7 days
$> visual-excuses --component universe --max-age=7

# To only show the excuses affecting the Foundations team
$> visual-excuses --team foundations-bugs
```

## Legend
Control are fairly intuitive with the mouse to zoom in and out of the picture

 - **Arrows** : go in the direction of the problem, follow the arrow to find the reason a package isn't migrating

 - **Orange items**: represents autopkgtest failures related excuses. Moving the mouse over the dot will show the exact failure and allow to click on hyperlink to go there.
 
 - **Yellow (ish) items** means another package autopkgtest failure is blocking the migration.

 - **Beige items** Blocked by another item, follow the arrow.
 
 - **White items** means the reason why it isn't migrating is unknown.
 
 - **Red items**: missing builds. moving the mouse over the dot will show which architecture are missings

 - Note: These colors choices may not always be ideal, might have to change them in the future.
 
## Pictures

Everything
![Everything](images/everything.png)

Team view
![Team view](images/team.png)

A dependencie cluster around tree-sitter
![cluster](images/cluster.png)
