#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>


int path_root_len = 0;

int 
append_str(char *dst, char *src)
{
    int len = strlen(src);
    memcpy(dst, src, len);
    dst[len] = '\0';
    return len;
}

int is_dot_or_dotdot(const char* name)
{
    return (name[0] == '.' &&
            (name[1] == '\0' ||
                 (name[1] == '.' && name[2] == '\0')));
}

int is_dot_git(const char* name)
{
    return name[0] == '.' &&
           name[1] == 'g' &&
           name[2] == 'i' &&
           name[3] == 't' &&
           name[4] == '\0';
}

/*
 * determin the file type
 * only file, directory and symbolic link is handled.
 * no plan to support other types.
 */
char file_type(const mode_t st_mode)
{
    if(S_ISREG(st_mode))
        return 'f';
    if(S_ISDIR(st_mode))
        return 'd';
    if(S_ISLNK(st_mode))
        return 'l';
    return '-';
}


int 
is_ignored(const char *path)
{
    return 0;
}

int
browse_dir(char* path, int len)
{
    struct dirent **ep;
    int entries;
    int i;

    if(is_ignored(path))
        return 0;

    if(path[len-1] != '/')
        len += append_str(path+len, "/");

    entries = scandir(path, &ep, 0, alphasort);
    if(entries < 0)
    {
        perror("Failed to scan directory");
        return -1;
    }

    for(i=0; i<entries; i++)
    {
        //puts(ep[i]->d_name);
        if(!is_dot_or_dotdot(ep[i]->d_name) && !is_dot_git(ep[i]->d_name))
        {
            struct stat sb;
            int child_len = len;
            child_len += append_str(path+child_len, ep[i]->d_name);

            if (lstat(path, &sb) == 0)
            {
                printf ("%c %d %d%d%d %d:%d %s\n", 
                         /* file type */
                         file_type(sb.st_mode),
                         /* file mode */
                         (S_IRWXU|S_IRWXG|S_IRWXO) & sb.st_mode, 
                         /* human readable file mode */
                         (sb.st_mode & S_IRWXU) >> 6, (sb.st_mode & S_IRWXG) >> 3, sb.st_mode & S_IRWXO, 
                         /* uid and gid */
                         sb.st_uid, sb.st_gid, path + path_root_len);
                if(S_ISDIR(sb.st_mode))
                     browse_dir(path, child_len);
            }
            else
            {
                //perror("Failed to stat file");
            }
        }
    }
    free(ep);

    return 0;
}


int
main (int argc, char**argv)
{
    char path[10240];
    int len = append_str(path, argv[1]);
    if(path[len-1] != '/')
        len += append_str(path+len, "/");
    path_root_len = len;
    return browse_dir(path, len);
}
