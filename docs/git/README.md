# Git

Git is great, but I forget the more obscure spells all the time.

### Delete remote branch

	git push origin :mybranch

### Replace `master` branch with something else

	git branch -m master oldmaster
	git branch -m mybranch master
	git checkout master
	git push -f origin master
	git branch --set-upstream-to origin/master


## Create a Twisted Patch

Create issue/feature branch:

	git checkout -b fix_9999

Do stuff, add, commit .. lets say `615d4a` is last commit before patch

	git log -n 2

then

	git diff 615d4a > fix_9999.patch

To check that the patch applies

	git checkout trunk
	patch -p1 < fix_9999.patch

	
## Changing Repo Origin

	git remote remove goeddea
	
	git config remote.origin.url git@bitbucket.org:oberstet/sixtdemo.git
	git push -u origin --all
	git push -u origin --tags
	
	git remote add goeddea git@bitbucket.org:goeddea/sixtdemo.git
	git fetch --all
	git merge goeddea


## Freshing up submodules - recursively

git submodule update --init --recursive


## Forwarding a submodule

cd SOMEREPO/SUBMODULE
git checkout master
git pull
cd ..
git add .
git commit -m "forward submodule SUBMODULE"
git push
git submodule update --init --recursive


## History of a file

Show history of a file following file renames:

	git log --follow -p crossbar/adminwebmodule/oraconnects.py

## Cleaning up history

### Removing files from history

The following will remove all files matching the given patterns from the repo history by rewriting history:

Clone the repo

	git clone --no-hardlinks WebMQ __WebMQ
    cd __WebMQ

Remove all tags

	git tag -d <TAG>

Filter

	git filter-branch -f --prune-empty --index-filter "git rm -rf --cached --ignore-unmatch '*.js' '*.jgz' '*.html' '*.css' '*.svg' '*.png' '*.jpg' '*.ttf' '*.woff' '*.eot' '*.md' '*.vsd' '*.pdf' '*.xlsx' '*.cpp' '*.h' '*.ino' '*.exe' '*.json' '*.ico' '*.pyc' 'LICENSE.txt' 'README' 'dropin.cache' 'appliance' 'webmqlas' 'test' 'demo' 'docs'" -- --all

	git filter-branch -f --prune-empty --index-filter "git rm -rf --cached --ignore-unmatch '*.js' '*.html' '*.css'"  -- --all

Cleanup

	git gc --prune
    rm -rf .git/refs/original/

### Removing branches from history


## Git on Windows

### Schlüssel erzeugen

SSH Schlüsselpaar erzeugen. Dazu Git Bash öffnen und folgendes Kommando eingeben:

	ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

Hierbei die Email Adresse anpassen sowie eine sichere Passphrase eingeben. Alles andere auf "Default lassen" (einfach RETURN drücken).

### SSH Agent

SSH Agent aktivieren

Die Datei ".bashrc" aus dem Folder hier in diesen Ordner auf Windows ablegen:

	C:\Benutzer\<Windows Nutzername>\

Dann alle Git Bash Fenster schliessen und ein neues Git Bash öffnen. Der  Nutzer wird dann _einmalig_ (pro Systemboot) aufgefordert seine Passphrase einzugeben. Nachfolgend gehen alle Git Zugriffe ohne Passphrase (aber dennoch sicher).

### Public Key bei GitHub

Public Key bei GitHub eintragen.

### Git Konfiguration

Git Bash öffnen und:

	git config --global user.name "Tobias Oberstein"
	git config --global user.email "tobias.oberstein@tavendo.de"
	git config --global push.default simple
	git config --global --bool pull.rebase true

### Repos klonen

Git Bash öffnen, und das jeweilige Repo klonen:

	git clone git@github.com:crossbario/crossbarexamples.git

Die Repo Klone sollten auf Eurer _lokalen_ Platte liegen, _nicht_ auf Netzwerklaufwerken.