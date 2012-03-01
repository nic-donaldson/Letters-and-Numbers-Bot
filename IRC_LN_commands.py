import socket
import re
def connect(server, port, nick, name):
    irc_sock = socket.socket()
    irc_sock.connect((server, port))
    

    irc_sock.send( 'NICK ' + nick + '\r\n')
    irc_sock.send( 'USER ' + nick + ' 0 * :' + name + '\r\n')

    return irc_sock

def join(irc_sock, channel):
    msgSend(irc_sock, 'JOIN ' + channel + '\r\n')    

def quitIRC(irc_sock, reason):
    print ("QUIT :" + reason + "\r\n"),
    msgSend(irc_sock, 'QUIT :' + reason + '\r\n')
    irc_sock.close()
    print "Exited"
    exit(0)

# A function to strip the newest command
# from the data should it exist
def msgRecv(sock, buf, data):
    lines = data.split("\n")
    if len(lines) > 1:
        response = lines[0]
        data = '\n'.join(lines[1:])
        return (response, data)
    else:
        try:
            data += sock.recv(buf)
            return ("", data)
        except socket.timeout:
            return ("", data)

def msgSend(sock, msg):
    sock.send(msg)

def IRCmsg(sock, msg, target):
    msgSend(sock, "PRIVMSG " + target + " :" + msg + '\r\n')
    print "PRIVMSG " + target + " :" + msg + '\r\n',

def msgFromUser(msg):
    try:
        msg = msg.split("!")
        if len(msg) <= 1:
            return False
        msg = msg[0].split(":")[1]
        if len(msg) >= 1:
            return True
        else:
            return False
    except:
        return False

# function to extract a users name from a msg
def getName(msg):
    if msgFromUser(msg):
        return msg.split("!")[0][1:]
    else:
        return ""

def msgGet(msg):
    if msgFromUser(msg):
        return ':'.join(msg.split(":")[2:]).strip()
    else:
        return ""
