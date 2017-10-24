


/**
 * FastClient Class
 * 
 * FastClient implements a basic reliable FTP client application based on UDP data transmission and selective repeat protocol
 * 
 */
public class FastClient {

 	/**
        * Constructor to initialize the program 
        * 
        * @param server_name    server name or IP
        * @param server_port    server port
        * @param window         window size
	* @param timeout	time out value
        */
	

	public void send(String file_name) {
		

	}

    /**
     * A simple test driver
     * 
     */
	public static void main(String[] args) {
		int window = 10; //segments
		int timeout = 100; // milli-seconds (don't change this value)
		
		String server = "localhost";
		String file_name = "";
		int server_port = 0;
		
		// check for command line arguments
		if (args.length == 4) {
			// either provide 3 parameters
			server = args[0];
			server_port = Integer.parseInt(args[1]);
			file_name = args[2];
			window = Integer.parseInt(args[3]);
		}
		else {
			System.out.println("wrong number of arguments, try again.");
			System.out.println("usage: java FastClient server port file windowsize");
			System.exit(0);
		}

		
		FastClient fc = new FastClient(server, server_port, window, timeout);
		
		System.out.printf("sending file \'%s\' to server...\n", file_name);
		fc.send(file_name);
		System.out.println("file transfer completed.");
	}

}
