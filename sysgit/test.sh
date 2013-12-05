#!/bin/sh

prepare_test_env()
{
    rm -fr drill_dir
    mkdir -p drill_dir/src
    mkdir -p drill_dir/dst
    cd drill_dir/src

    echo "bar/" > .gitignore

    echo "original content" > file

    mkdir dir
    touch dir/foo

    mkdir empty_dir

    ln -s file slink
    
    mkdir bar
    touch bar/sys.log
}

backup()
{
    :
}

update_test_env()
{
    :
}


restore()
{
    :
}

verify_test_env()
{
    :
}

prepare_test_env
backup
update_test_env
restore
verify_test_env
