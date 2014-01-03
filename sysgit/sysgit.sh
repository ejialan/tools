#!/bin/sh

log()
{
    echo `date '+[%Y-%m-%d %H:%M:%S] '` $1 $2 $3 $4 $5
}

check_user()
{
  if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
  fi
}

check_file()
{
  if [ ! -f "$1" ]; then
    log "$1 not found"
    exit 1
  fi
}

check_dir()
{
  if [ ! -d "$1" ]; then
    log "$1 not found"
    exit 1
  fi
}

pre_check()
{
  check_user
  check_file "$base_dir/dir.c"
  check_file "$base_dir/gitignore"

  gcc -o /tmp/traversal $base_dir/dir.c
  gcc -o /tmp/restore $base_dir/dir.c
  gcc -o /tmp/clean $base_dir/dir.c
  #git config --global user.email "you@example.com"
  #git config --global user.name "Your Name"
}

stop_services()
{
  log "stop services"
  # stop services which may impact the backup/restore, especially the services which continue update files
}

start_services()
{
  log "start services"
  # provide a way to start the services since backup/restore would not start the service cause in HA system
  # start service may impact other nodes.
}

check_mount_point()
{
  log "check mount points"
  if [ -f ./mount.list ];then
    mount | sort > /tmp/mount.list.$$
    diff ./mount.list /tmp/mount.list.$$ 
    if [ $? -ne 0 ]; then
      log "mount points are different comparing with previous backup/restore"
      log "restore the mount point manually to continue"
      exit 1
    fi
  fi
}

save_mount_point()
{
  mount | sort > ./mount.list  
}

prepare_env()
{
  log "prepare environment for sysgit"
  prepare_gitignore
  stop_services
  check_mount_point
  save_mount_point
}

prepare_gitignore()
{
  if [ -f "${src}/.gitignore" ];then
    log ".gitignore already existed in ${src}. Reuse it."
  else
    log "generate .gitignore in ${src}"
    cp "$base_dir/gitignore" "${src}/.gitignore"
  fi
  echo "$dst" >> "${src}/.gitignore"
}

init_repo()
{
  log "init repository"
  git init --separate-git-dir="${dst}" .
  log "add files into repository"
  git add . >> /var/tmp/git.log
  log "commit_repo"
  git commit -m 'init commit' >> /var/tmp/git.log
}

generate_ignore_list()
{
  git status --ignored | sed -n -e '/Ignored files:/,$ p' | sed -e '1,3d' | sed -n -e '/^#/p' | sed -e 's/^#[[:space:]]//' > ignore.list
}

backup_ownership_and_mode()
{
  log "backup_ownership_and_mode"
  check_dir $src
  cd "${src}"
  generate_ignore_list
  # git will take care symbol links
  /tmp/traversal "." ignore.list `cat ignore.list | wc -l` > stat.list
}

commit_repo()
{
  log "add files into repository"
  git add . >> /var/tmp/git.log 
  log "commit_repo"
  git commit --amend -m 'init commit' >> /var/tmp/git.log
}

################################################
######## rollbacl functions ####################
################################################
reset_repo()
{
  log "clean working directory"
  # this operation is really dangerous
  git clean -f
  log "reset working direcotry to HEAD"
  git reset --hard HEAD
}

restore_file_ownership()
{
  log "restore ownership and mode of files"
  /tmp/restore $src stat.list
}

del_new_added_dir()
{
  log "delete new added directory"
  cat stat.list | sed -n -e '/^d/p' | sed -e 's/^[^:]*:[0-9]* //g' | sort > /tmp/old.list.$$
  /tmp/clean $src ignore.list `cat ignore.list | wc -l` | sort > /tmp/new.list.$$
  diff -y -W 1024 /tmp/old.list.$$ /tmp/new.list.$$ | sed -n -e '/^[[:space:]]\+>[[:space:]]/p' | sed -e 's/^[[:space:]]\+>[[:space:]]//' > /tmp/added.list.$$
  if [ `cat /tmp/added.list.$$ | wc -l` -gt 0 ];then
    log "following directory would be deleted:"
    cat /tmp/added.list.$$
    log "Confirm to delete them (y/n)?:"
    read y 
    if [ "x${y}" = "xy" ]; then
      cat /tmp/added.list.$$ | rm -fr
    else
      log "These directory is kept!"
    fi
  else
    log "no added directory"
  fi
  
}

backup()
{
  log "Start to backup system."
  check_dir $src
  cd "${src}"
  check_dir $dst
  prepare_env
  init_repo
  backup_ownership_and_mode
  commit_repo
  log "Finsh to backup system."
}

restore()
{
  log "Start to restore system."
  check_dir $src
  cd "${src}"
  prepare_env
  reset_repo
  restore_file_ownership
  del_new_added_dir
  log "Finsh to restore system."
}

usage()
{
  echo "Usage:"
  echo "  $0 [backup|restore|backup_ownership_and_mode|stop_services|start_services] [source] [destination]"
  echo "example:"
  echo "  $0 backup / /opt/app/oracle/backup"
  echo "  $0 restore /"
  echo "  $0 backup_ownership_and_mode /"
  echo "  $0 start_services"
  echo "  $0 stop_services"
}

parse_args()
{
  case $1 in
    backup)
      oper=backup 
      src=${2}
      dst=${3}
      ;;
    restore)
      oper=restore
      src=${2}
      ;;
    backup_ownership_and_mode)
      oper=backup_ownership_and_mode
      src=${2}
      ;;
    start_services)
      oper=start_services
      ;;
    stop_services)
      oper=stop_services
      ;;
    *)
      oper=usage
      ;;
  esac
}

#set local to POSIX so as to make the sort result stable
#refer to http://www.gnu.org/software/coreutils/manual/html_node/sort-invocation.html#fn-1
export LC_ALL=C
oper=usage
script=`readlink -f $0`
base_dir=`dirname $script`

pre_check
parse_args $*
$oper
