#!/bin/sh

precheck()
{
  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
}

generategitignore()
{
    :
}

init_repo()
{
    cd /
    git init /
    git add /
    git commit -m 'init commit'
}

backup_empty_folder()
{
    find / -type d -empty  2>/dev/null | grep -v '.git' > /tmp/emtyfolder.list
    while read line
    do
        egrep -v "$line" /tmp/emtyfolder.list > /tmp/emtyfolder.list.tmp
        mv /tmp/emtyfolder.list.tmp /tmp/emtyfolder.list
    done < /.gitignore
    cat /tmp/emtyfolder.list | xargs -I {} stat -c '%a %U:%G %n' {} > /emptyfolder.list
    :
}

backup_ownership()
{
    #stat -c '%a %U:%G %n'
    cd /
    git ls-tree -r --name-only HEAD | xargs -I {} stat -c '%a %U:%G %n' {} | awk '{if ($2 != "root:root") print $0 }' > /stat.list
    :
}

commit_repo()
{
    cd /
    git add /
    git commit --amend -m 'init commit'
}

################################################
######## rollbacl functions ####################
################################################
reset_repo()
{
    git clean -f -d
    git reset --hard HEAD
}

restore_owner()
{
    while read mode owner file
    do
        #stat -c '%a %U:%G %n'
        curowner=`stat -c '%U:%G' $file`
        if [ "x$curowner" != "x$owner" ]; then
            chown $owner $file
        fi
    done < /stat.list
}

restore_empty_folder()
{
    while read mode owner folder
    do
        if [ ! -d $folder ]; then
            mkdir -p "$folder"
            chmod $mode "$folder"
            chown $owner "$folder"
        fi
    done < emptyfolder.list
}

if [ "x$1" = "xbackup" ]; then
   init_repo
   backup_empty_folder
   backup_ownership
   commit_repo
elif [ "x$1" = "xrestore" ]; then
   #reset_repo
   restore_owner
   restore_empty_folder
fi

backup_ownership

