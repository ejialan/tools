#!/bin/sh

precheck()
{
    :
}

generategitignore()
{
    :
}

init_repo()
{
    :
}

backup_empty_folder()
{
    find / -type d -empty  2>/dev/null | egrep -v '/proc' | xargs -I {} stat -c '%a %U:%G %n' {} > /emptyfolder.list
    :
}

backup_ownership()
{
    #stat -c '%a %U:%G %n'
    git status / | grep 'new file' | awk '{print $4}' | xargs -I {} stat -c '%a %U:%G %n' {} > /stat.list
    :
}

commit_repo()
{
    :
}

