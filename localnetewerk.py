import socket


def IPGenerator():
    q = ( (a,b,c,d) for a in range(255) for b in range(255) for c in range(255) for d in range(255) )
    for w,e,r,t in q:
        yield f"{w}.{e}.{r}.{t}"
    

def main():
    hostname = socket.gethostname()
    localIp = socket.gethostbyname(hostname)
    print(hostname,localIp)
    pass


if __name__ == "__main__":
    main()