#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>

#define MAX(a,b) (((a)>(b))?(a):(b))

struct ign_file
{
  char* buf;
  int len;
  int is_dir;
};

struct path_buf
{
  char* buf;
  int prefix_len;
  int len;
  int cap;
};

struct ign_file* ign_files;
int nr_ign_files = 0;

void
reset_path(struct path_buf *path, int len)
{
  path->len = len;
  path->buf[len] = '\0';
}

void 
ensure_cap(struct path_buf *path, int extra)
{
  if(path->len + extra > path->cap)
  {
    int add = MAX(2*extra, 1024);
    path->buf = realloc(path->buf, path->cap + add);
    path->cap += add;
  }
}

void 
print_path(struct path_buf *path)
{
  if(path->len>0)
    printf("len = %d, cap = %d, str = %s\n", path->len, path->cap, path->buf);
}

void 
_append_str(struct path_buf *path, const char *src)
{
    int len = strlen(src);
    ensure_cap(path, len);

    memcpy(path->buf + path->len, src, len);
    path->len += len;
    path->buf[path->len] = '\0';
}

void
append_path_seperator(struct path_buf *path)
{
  if(path->buf[path->len-1] != '/')
    _append_str(path, "/");
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
  int i = 0;
  int len = strlen(path);

  for(i=0; i<nr_ign_files; i++)
  {
      if(len == ign_files[i].len
          && strcmp(path, ign_files[i].buf) == 0 )
        return 1;
  }

  return 0;
}

void load_ignore_list(const char* path, int linenr)
{
  char *line = NULL;
  size_t linecap = 0;
  ssize_t linelen;
  int i = 0;

  FILE *fp = fopen(path, "r");
  if(!fp)
  {
    perror("failed to open file");
    exit(1);
  }

  ign_files = (struct ign_file*)calloc(linenr, sizeof(struct ign_file));
  nr_ign_files = linenr;

  while ((linelen = getline(&line, &linecap, fp)) > 0)
  {
    if(line[linelen-1] == '\n')
    {
      line[linelen-1] = '\0';
      linelen--;
    }

    ign_files[i].buf = line; 
    ign_files[i].len = linelen; 
    ign_files[i].is_dir = line[linelen-1] == '/' ? 1 : 0;

    line = NULL;
    linecap = 0;
    i++;
  }
}

int
browse_dir(struct path_buf *path)
{
    struct dirent **ep;
    int entries;
    int i;
    int current_path_len;

    append_path_seperator(path);

    current_path_len = path->len;

    entries = scandir(path->buf, &ep, 0, alphasort);
    if(entries < 0)
    {
        perror("Failed to scan directory");
        return -1;
    }

    for(i=0; i<entries; i++)
    {
        //puts(ep[i]->d_name);
        reset_path(path, current_path_len);
        if(!is_dot_or_dotdot(ep[i]->d_name) && !is_dot_git(ep[i]->d_name))
        {
            struct stat sb;
            _append_str(path, ep[i]->d_name);

            if (lstat(path->buf, &sb) == 0)
            {
              if(file_type(sb.st_mode) == 'd')
              {
                append_path_seperator(path);
              }

              if(is_ignored(path->buf + path->prefix_len))
                continue;

              printf ("%c %d %d%d%d %d:%d %s\n", 
                         /* file type */
                         file_type(sb.st_mode),
                         /* file mode */
                         (S_IRWXU|S_IRWXG|S_IRWXO) & sb.st_mode, 
                         /* human readable file mode */
                         (sb.st_mode & S_IRWXU) >> 6, (sb.st_mode & S_IRWXG) >> 3, sb.st_mode & S_IRWXO, 
                         /* uid and gid */
                         sb.st_uid, sb.st_gid, path->buf + path->prefix_len);
              if(S_ISDIR(sb.st_mode))
                 browse_dir(path);
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
tranversal_dir ( const char* path, int argc, const char **argv)
{
  return 0;
}

int 
restore_dir ( const char* path, int argc, const char **argv)
{
  return 0;
}

int 
clean_dir ( const char* path, int argc, const char **argv)
{
  return 0;
}

struct cmd_struct
{
  const char* cmd;
  int (*fn)(const char*, int, const char**);
};

struct cmd_struct commands[] = {
  {"tranversal", tranversal_dir},
  {"restore", restore_dir},
  {"clean", clean_dir}
};

int
main (int argc, char**argv)
{
  struct path_buf path = {
    NULL, 0, 0, 0
  };
  _append_str(&path, argv[1]);
  append_path_seperator(&path);
  path.prefix_len = path.len;

  load_ignore_list(argv[2], atoi(argv[3]));
  return browse_dir(&path);
}
