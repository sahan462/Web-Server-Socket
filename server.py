import socket
import os
import subprocess
import tempfile

directory = "htdocs"

# Function to read the content of a file
def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except Exception as e:
        print("Error reading file:", e)
        return None
    
    

# Function to generate an HTML file with links to files in the directory
def generate_index_file():
    try:
        # Get a list of files in the directory
        files = os.listdir(directory)

        # Create an HTML file for the index
        with open(os.path.join(directory, "index.php"), "w") as index_file:
            index_file.write("<!DOCTYPE html>\n<html>\n<head>\n")
            index_file.write("<title>Index of /</title>\n</head>\n<body>\n")
            index_file.write("<h1>htdocs/</h1>\n<hr>\n<ul>\n")

            # Generate links to the files
            for file in files:
                if file != "index.php" and os.path.isfile(os.path.join(directory, file)):
                    index_file.write(f'<li><a href="{file}">{file}</a></li>\n')

            index_file.write("</ul>\n<hr>\n</body>\n</html>\n")
    except Exception as e:
        print("Error generating index file:", e)


    
    
# Function to generate a temporary PHP script file with additional PHP code and parameters
def generate_temp_file(basic_file_path, query_string, request_method):
    try:
        # Read the content of the basic PHP script file
        with open(basic_file_path, 'r') as basic_file:
            basic_content = basic_file.read()

        # Create a temporary PHP script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', dir=directory, delete=False) as temp_script:
            # Prepare the parameters from the query string
            parameters = query_string.split("&")

            # Initialize content string for PHP array initialization
            content = ""

            # Loop through query parameters and format as PHP array elements
            for pair in parameters:
                key, value = pair.split("=")
                content += f"'{key}' => '{value}',"

            # Write PHP code to the temporary script file
            temp_script.write(f'<?php $_{request_method} = array({content});?>')  # Set $_GET/$_POST values
            temp_script.write("\n")  # Add a newline
            temp_script.write(basic_content)  # Append the original PHP script content
            temp_script.write("\n")  # Add a newline

        # Return the path of the temporary script file
        return temp_script.name
    except Exception as e:
        # Handle any exceptions and print an error message
        print("Error generating temporary PHP script:", e)
        return None




# Function to execute a PHP script and return its output
def execute_php_script(script_path, query_string):
    try:
        # Prepare the PHP command for execution
        php_command = ['php', script_path, query_string]

        # Create a subprocess to execute the PHP script
        php_process = subprocess.Popen(
            php_command,
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.PIPE  # Capture standard error
        )

        # Capture the output (HTML content) from the PHP script
        php_output, php_errors = php_process.communicate()

        # Decode the PHP script's output from bytes to a UTF-8 string
        return php_output.decode('utf-8')
    
    except Exception as e:
        # Handle any exceptions and print an error message
        print("Error executing PHP script:", e)
        return None



# Function to send an error response
def send_error_response(client_socket, status, message):

    response = f"HTTP/1.1 {status}\r\nContent-Type: text/html\r\n\r\n<h1>{status}</h1><p>{message}</p>"
    client_socket.send(response.encode('utf-8'))



# Function to start an HTTP server
def httpserver(host, port):

    # Create a socket to listen on the specified host and port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print("Server is listening on port %s" % port)

    while True:
        # Accept incoming connections
        conn, addr = s.accept()
        
        # Receive and decode the HTTP request
        request = conn.recv(4096).decode('utf-8')
        request_lines = request.split('\r\n')
        request_method, request_path, _ = request_lines[0].split()

        if(request_path == "/"):
            generate_index_file()
            request_path = "index.php"

        query_string = ""
        if '?' in request_path:
            request_path, query_string = request_path.split('?')

        # Check if the requested file is a PHP script
        if request_path.endswith('.php'):

            # Handle GET request
            if request_method == 'GET':

                php_request_path = os.path.join(directory, request_path.lstrip('/'))

                if os.path.exists(php_request_path):
                    
                    if (len(query_string) > 0):
                        php_request_path = generate_temp_file(php_request_path, query_string, request_method)
                        output = execute_php_script(php_request_path, query_string)
                        os.remove(php_request_path)
                    else:
                        output = execute_php_script(php_request_path, query_string)

                    if output is not None:
                        # Send the PHP script's output as the response
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{output}"
                        conn.send(response.encode('utf-8'))

                    else:
                        # Handle PHP script execution error
                        send_error_response(conn, '500 Internal Server Error', 'Error executing PHP script')

                else:

                    send_error_response(conn, '404 Not Found', 'File not found')

            # Handle POST request
            elif request_method == 'POST':
                
                query_string = request_lines[-1]

                php_request_path = os.path.join(directory, request_path.lstrip('/'))

                if os.path.exists(php_request_path):
                    
                    if (len(query_string) > 0):
                        php_request_path = generate_temp_file(php_request_path, query_string, request_method)
                        output = execute_php_script(php_request_path, query_string)
                        os.remove(php_request_path)
                    else:
                        output = execute_php_script(php_request_path, query_string)

                    if output is not None:
                        # Send the PHP script's output as the response
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{output}"
                        conn.send(response.encode('utf-8'))

                    else:
                        # Handle PHP script execution error
                        send_error_response(conn, '500 Internal Server Error', 'Error executing PHP script')

            else:
                send_error_response(conn, '405 Method Not Allowed', 'Method not allowed')

        else:
            # Check if the requested file is a static HTML file
            if request_path.endswith('.html'):
                static_file_path = os.path.join(directory, request_path.lstrip('/'))
                
                if os.path.exists(static_file_path):
                    # Read the content of the static HTML file
                    static_content = read_file_content(static_file_path)
                    if static_content is not None:
                        # Send the static file's content as the response
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{static_content}"
                        conn.send(response.encode('utf-8'))
                else:
                    # Handle 404 error for static files
                    send_error_response(conn, '404 Not Found', 'Static file not found')


        # Close the connection
        conn.close()




# Define the host and port for the HTTP server
host = "127.0.0.1"
port = 2728

# Start the HTTP server
httpserver(host, port)
