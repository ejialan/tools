#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>


int is_dot_or_dotdot(const char* name)
{
    return (name[0] == '.' &&
            (name[1] == '\0' ||
                 (name[1] == '.' && name[2] == '\0')));
}



int
browse_dir(const char* path)
{
    DIR *dp;
    struct dirent *ep;

    dp = opendir (path);
    if (dp != NULL)
    {
        while (ep = readdir (dp))
        {
            if(!is_dot_or_dotdot(ep->d_name))
            {
                struct stat sb;
                puts (ep->d_name);
                if (lstat(ep->d_name, &sb) == 0)
                {
                    putchar(sb.st_mode);
                    putchar(' ');
                    puts (ep->d_name);
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
    printf("name max = %d", NAME_MAX);
    return browse_dir(argv[1]);
}
