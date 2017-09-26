#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stdarg.h>
#include <ctype.h>

// global variables nicely grouped
struct {
    int port; // listening port
    char buffer[32]; // temporary buffer for input
    char password[32]; // required password
    char secret[1024]; // the secret to reveal
} globals;

// report error message & exit
void die( const char * errorMessage, ...) {
    fprintf( stderr, "Error: ");
    va_list args;
    va_start( args, errorMessage);
    vfprintf( stderr, errorMessage, args);
    fprintf( stderr, "\n");
    va_end( args);
    exit(-1);
}

// read a line of text from file descriptor into provided buffer
void readLineFromFd( int fd, char * buff) {
    char * ptr = buff;
    while(1) {
        // try to read in the next character from fd, exit loop on failure
        if( read( fd, ptr, 1) < 1) break;
        // character stored, now advance ptr
        ptr ++;
        // if last character read was a newline, exit loop
        if( * (ptr - 1) == '\n') break;
    }
    // rewind ptr to the last read character
    ptr --;
    // trim trailing spaces (including new lines, telnet's \r's)
    while(ptr > buff && isspace(* ptr)) ptr --;
    // terminate the string
    * (ptr + 1) = '\0';
}

// write a string to file descriptor
int writeStrToFd( int fd, char * str) {
   return write( fd, str, strlen( str));
}

int main( int argc, char ** argv)
{
    // parse command line arguments
    if( argc != 4) die( "Usage: server port password secret");
    char * end = NULL;
    globals.port = strtol( argv[1], & end, 10);
    if( * end != 0) die( "bad port %s", argv[1]);
    strncpy( globals.password, argv[2], sizeof( globals.password));
    globals.password[ sizeof(globals.password)-1] = 0;
    strncpy( globals.secret, argv[3], sizeof( globals.secret));
    globals.secret[sizeof(globals.secret)-1] = 0;

    // create a listenning socket on a given port
    struct sockaddr_in servaddr;
    int listenSockFd = socket(AF_INET, SOCK_STREAM, 0);
    if( listenSockFd < 0) die("socket() failed");
    bzero( (char *) & servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htons(INADDR_ANY);
    servaddr.sin_port = htons(globals.port);
    if( bind(listenSockFd, (struct sockaddr *) & servaddr, sizeof(servaddr)) < 0)
        die( "Could not bind listening socket: %s", strerror( errno));

    // listen for a new connection
    if( listen(listenSockFd, 3) != 0)
        die( "Could not listen for incoming connections.");

    while(1) {
        printf( "Waiting for a new connection...\n");
        // accept a new connection
        int connSockFd = accept(listenSockFd, NULL, NULL);
        if( connSockFd < 0) die( "accept() failed: %s", strerror(errno));
        printf( "Talking to someone.\n");
        // sey hello to the other side
        writeStrToFd( connSockFd, "Secret Server 1.0\n");
        // read response from socket
        readLineFromFd( connSockFd, globals.buffer);
        // check if it was a correct password
        if( strcmp( globals.buffer, globals.password) == 0) {
            // password was correct, reveal the secret
            printf( "Someone used the correct password.\n");
            writeStrToFd( connSockFd, "The secret is: ");
            writeStrToFd( connSockFd, globals.secret);
            writeStrToFd( connSockFd, "\n");
        }
        else {
            // password was incorrect, don't reveal the secret
            printf( "Someone used an incorrect password.\n");
            writeStrToFd( connSockFd, "I am not talking to you, bye!\n");
        }
        // close the connection
        close( connSockFd);
    }

    // this will never be called
    close( listenSockFd);
    return 0;
}
