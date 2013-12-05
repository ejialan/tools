#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>

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
    DIR *dp;
    struct dirent *ep;

    if(is_ignored(path))
        return 0;

    dp = opendir (path);
    if (dp != NULL)
    {
	if(path[len] != '/')
	    len += append_str(path+len, "/");

        while (ep = readdir (dp))
        {
            //puts(ep->d_name);
            if(!is_dot_or_dotdot(ep->d_name) && !is_dot_git(ep->d_name))
            {
                struct stat sb;
                int child_len = len;
                child_len += append_str(path+child_len, ep->d_name);

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
				sb.st_uid, sb.st_gid, path);
                    if(S_ISDIR(sb.st_mode))
                         browse_dir(path, child_len);
                }
                else
                {
                    //printf("Failed to stat %s", path);
                }
            }
        }
       (void) closedir (dp);
    }
    else
       perror ("Couldn't open the directory");

    return 0;
}


int
main (int argc, char**argv)
{
    char path[10240];
    int len = 0;
    len += append_str(path, argv[1]);
    return browse_dir(path, len);
}
