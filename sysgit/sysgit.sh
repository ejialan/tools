#!/bin/sh

log()
{
    echo `date '+[%Y-%m-%d %H:%M:%S] '` $1 $2 $3 $4 $5
}

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

backup_folder_ownership()
{
    log "backup_folder_ownership"
    # git will take care symbol links
    cd /
    find / -type d 2>/dev/null | grep -v '.git' > /tmp/folder.list
    while read line
    do
        egrep -v "$line" /tmp/folder.list > /tmp/folder.list.tmp
        mv /tmp/folder.list.tmp /tmp/folder.list
    done < /.gitignore
    cat /tmp/folder.list | xargs -I {} stat -c '%a %u:%g %n' {} > /folder.list
}

backup_file_ownership()
{
    log "backup_file_ownership"
    #stat -c '%a %U:%G %n'
    cd /
    git ls-tree -r --name-only HEAD | xargs -I {} stat -c '%u:%g %n' {} | awk '{if ($1 != "0:0") print $0 }' > /stat.list
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
    cd /
    # this operation is really dangerous
    #git clean -f -d
    git reset --hard HEAD
}

restore_file_ownership()
{
    cd /
    while read owner file
    do
        #stat -c '%a %U:%G %n'
        curowner=`stat -c '%u:%g' $file`
        if [ "x$curowner" != "x$owner" ]; then
            chown $owner $file
        fi
    done < /stat.list
}

restore_folder_ownership()
{
    cd /
    while read mode owner folder
    do
        if [ ! -d $folder ]; then
            mkdir -p "$folder"
            chmod $mode "$folder"
            chown $owner "$folder"
        else
            curmode=`stat -c '%a %u:%g' $folder`
            if [ x"$curmode" != x"$mode $owner" ]; then
               chmod $mode "$folder"
               chown $owner "$folder"
            fi
        fi
    done < /folder.list
}

if [ "x$1" = "xbackup" ]; then
   log "Start to backup system."
   init_repo
   backup_folder_ownership
   backup_file_ownership
   commit_repo
   log "Finsh to backup system."
elif [ "x$1" = "xrestore" ]; then
   log "Start to restore system."
   reset_repo
   restore_file_ownership
   restore_folder_ownership
   log "Finsh to restore system."
fi


