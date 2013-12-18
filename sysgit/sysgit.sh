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
  gcc -o /tmp/traversal dir.c
  gcc -o /tmp/restore dir.c
  gcc -o /tmp/clean dir.c
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

generate_ignore_list()
{
  git status --ignored | sed -n -e '/Ignored files:/,$ p' | sed -e '1,3d' | sed -e 's/^#[[:space:]]//' > ignore.list
}

backup_ownership_and_mode()
{
    log "backup_ownership_and_mode"
    # git will take care symbol links
    /tmp/traversal "." ignore.list `cat ignore.list | wc -l` > stat.list
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
    git clean -f
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
   generate_ignore_list
   backup_ownership_and_mode
   commit_repo
   log "Finsh to backup system."
elif [ "x$1" = "xrestore" ]; then
   log "Start to restore system."
   reset_repo
   restore_file_ownership
   restore_folder_ownership
   log "Finsh to restore system."
fi


