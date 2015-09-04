Container Spielwiese
====================

Tests mit vagga und vagrant-lxc

Ziel:
-----

- nginx Webserver zum Laufen bringen
- Webroot und Config aus diesem git repo verwenden
- Fehler diagnostizieren können (log), wenn man die Config bewusst kaputtmacht

Status:
-------

- vagrant-lxc geht prinzipiell, was noch fehlt wäre nicht so interessant
- vagga ist hartnäckiger, lässt sich irgendwie nicht durch virtualbox shared folder hindurch gescheit verwenden :(

Loslegen:
---------

    apt-get install vagrant virtualbox
    cd vagrant-lxc
    cat README
    cd ../vagga
    cat README
