#include "kernel/types.h"
#include "user/user.h"

#define JOBS 6
#define HIGH_PRIORITY 0
#define LOW_PRIORITY 2

struct start_token {
  int tick;
};

struct result {
  int job;
  int pid;
  int priority;
  int start_tick;
  int end_tick;
  uint64 checksum;
};

static uint64
burn(int rounds, int salt)
{
  volatile uint64 value = 1469598103934665603ULL ^ (uint64)salt;
  for (int i = 0; i < rounds; i++) {
    value ^= (uint64)(i + salt);
    value *= 1099511628211ULL;
  }
  return value;
}

static uint64
run_workload(char *workload, int job)
{
  uint64 checksum = 0;
  if (strcmp(workload, "cpu") == 0) {
    checksum = burn(80000000, job + 1);
  } else if (strcmp(workload, "io") == 0) {
    for (int i = 0; i < 30; i++) {
      checksum ^= burn(15000, job + i + 1);
      pause(1);
    }
  } else if (strcmp(workload, "mixed") == 0) {
    for (int i = 0; i < 10; i++) {
      checksum ^= burn(5000000, job + i + 1);
      pause(1);
    }
  } else {
    printf("unknown workload %s\n", workload);
    exit(2);
  }
  return checksum;
}

static void
write_exact(int fd, void *buffer, int size)
{
  if (write(fd, buffer, size) != size) {
    printf("schedbench write failed\n");
    exit(3);
  }
}

static void
read_exact(int fd, void *buffer, int size)
{
  if (read(fd, buffer, size) != size) {
    printf("schedbench read failed\n");
    exit(4);
  }
}

int
main(int argc, char **argv)
{
  if (argc != 3) {
    printf("usage: schedbench cpu|io|mixed repeat\n");
    exit(1);
  }
  char *workload = argv[1];
  int repeat = atoi(argv[2]);
  int ready_pipe[2];
  int start_pipe[2];
  int result_pipe[2];
  if (pipe(ready_pipe) < 0 || pipe(start_pipe) < 0 || pipe(result_pipe) < 0) {
    printf("schedbench pipe failed\n");
    exit(1);
  }

  for (int job = 0; job < JOBS; job++) {
    int pid = fork();
    if (pid < 0) {
      printf("schedbench fork failed\n");
      exit(1);
    }
    if (pid == 0) {
      int priority = job < JOBS / 2 ? HIGH_PRIORITY : LOW_PRIORITY;
      if (setpriority(priority) < 0) {
        printf("schedbench setpriority failed\n");
        exit(5);
      }
      char ready = 'R';
      write_exact(ready_pipe[1], &ready, 1);
      struct start_token token;
      read_exact(start_pipe[0], &token, sizeof(token));
      struct result result;
      result.job = job;
      result.pid = getpid();
      result.priority = priority;
      result.start_tick = token.tick;
      result.checksum = run_workload(workload, job);
      result.end_tick = uptime();
      write_exact(result_pipe[1], &result, sizeof(result));
      exit(0);
    }
  }

  for (int job = 0; job < JOBS; job++) {
    char ready;
    read_exact(ready_pipe[0], &ready, 1);
  }
  struct start_token token = {.tick = uptime()};
  for (int job = 0; job < JOBS; job++)
    write_exact(start_pipe[1], &token, sizeof(token));

  int max_end = token.tick;
  for (int completed = 0; completed < JOBS; completed++) {
    struct result result;
    read_exact(result_pipe[0], &result, sizeof(result));
    if (result.end_tick > max_end)
      max_end = result.end_tick;
    printf("GRESULT workload=%s repeat=%d job=%d pid=%d priority=%d "
           "start=%d end=%d turnaround=%d checksum=%ld\n",
           workload, repeat, result.job, result.pid, result.priority,
           result.start_tick, result.end_tick,
           result.end_tick - result.start_tick, result.checksum);
  }
  for (int job = 0; job < JOBS; job++) {
    int status = -1;
    if (wait(&status) < 0 || status != 0) {
      printf("schedbench child failure\n");
      exit(6);
    }
  }
  printf("GBENCH_DONE workload=%s repeat=%d jobs=%d makespan=%d\n",
         workload, repeat, JOBS, max_end - token.tick);
  exit(0);
}
