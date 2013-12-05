#!/bin/sh


log()
{
    echo `date '+[%Y-%m-%d %H:%M:%S] '` $1 $2 $3 $4 $5
}

pre_check()
{
  #git config --global user.email "you@example.com"
  #git config --global user.name "Your Name"
  if [ ! -d "${src}" ]; then
    echo "${src} is not a dirctory"
    exit 1
  fi

  if [ ! -d "${dst}" ]; then
    echo "${dst} is not a dirctory"
    exit 1
  fi
}


prepare_env()
{
  gcc dir.c
  prepare_gitignore
}

prepare_gitignore()
{
  if [ -f "${src}/.gitignore" ];then
    log ".gitignore already existed in ${src}. Reuse it."
  else
    log "generate .gitignore"
    cp gitignore "${src}/.gitignore"
  fi
}

init_repo()
{
    git init --separate-git-dir="${dst}" .
    git add .
    git commit -m 'init commit'
}

backup_ownership_and_mode()
{
    log "backup_ownership_and_mode"
    # git will take care symbol links
    ./a.out  > /tmp/folder.list
    while read line
    do
        egrep -v "$line" /tmp/folder.list > /tmp/folder.list.tmp
        mv /tmp/folder.list.tmp /tmp/folder.list
    done < ./.gitignore
    cat /tmp/folder.list | xargs -I {} stat -c '%a %u:%g %n' {} > ./folder.list
}

backup_file_ownership()
{
    log "backup_file_ownership"
    #stat -c '%a %U:%G %n'
    git ls-tree -r --name-only HEAD | xargs -I {} stat -c '%u:%g %n' {} | awk '{if ($1 != "0:0") print $0 }' > ./stat.list
}

commit_repo()
{
    git add .
    git commit --amend -m 'init commit'
}

################################################
######## rollbacl functions ####################
################################################
reset_repo()
{
    # this operation is really dangerous
    #git clean -f -d
    git reset --hard HEAD
}

restore_file_ownership()
{
    while read owner file
    do
        #stat -c '%a %U:%G %n'
        curowner=`stat -c '%u:%g' $file`
        if [ "x$curowner" != "x$owner" ]; then
            chown $owner $file
        fi
    done < ./stat.list
}

restore_folder_ownership()
{
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
    done < ./folder.list
}

src=${2:-/}
dst=${3:-/}

pre_check
prepare_env

cd "${src}"

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


