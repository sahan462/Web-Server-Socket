import socket
import os
import subprocess
import urllib
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
    
# Function to generate a temporary PHP script file with additional PHP code and parameters
def generate_temp_file(basic_content, query_string):
    try:
        # Parse the query string into a dictionary of parameters
        params = dict(urllib.parse.parse_qsl(query_string))

        # Create a temporary PHP script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', dir=directory, delete=False) as temp_script:
            # Write the PHP code to extract parameters from the dictionary
            php_code = ""
            for key, value in params.items():
                php_code += f"${key} = '{value}';\n"

            # Combine the PHP code, basic content, and additional PHP code
            complete_php_script = f"{php_code}\n{basic_content}"

            # Write the complete PHP script to the temporary file
            temp_script.write(complete_php_script)

        # Return the path of the temporary script file
        return temp_script.name
    except Exception as e:
        print("Error generating temporary PHP script:", e)
        return None



# Function to execute a PHP script and return its output
def execute_php_script(script_path, query_string):
    print("script", script_path)
    print("query string", query_string)
    try:
        # Use PHP to execute the temporary script with the query string
        php_command = ['php', script_path, query_string]
        php_process = subprocess.Popen(
            php_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Capture the output (HTML content) from PHP
        php_output, php_errors = php_process.communicate()


        return php_output.decode('utf-8')
    except Exception as e:
        print("Error executing PHP script:", e)
        return None

# Function to send an error response
def send_error_response(client_socket, status, message):

    response = f"HTTP/1.1 {status}\r\nContent-Type: text/html\r\n\r\n<h1>{status}</h1><p>{message}</p>"
    client_socket.send(response.encode('utf-8'))

# Function to start an HTTP server
def httpserver(host, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print("Server is listening on port %s" % port)

    while True:
        conn, addr = s.accept()
        
        request = conn.recv(4096).decode('utf-8')
        request_lines = request.split('\r\n')
        request_method, request_path, _ = request_lines[0].split()

        query_string = ""
        if '?' in request_path:
            request_path, query_string = request_path.split('?')
    

        # Check if the requested file is a PHP script
        if request_path.endswith('.php'):

            # Handle GET request
            if request_method == 'GET':
                
                php_request_path = os.path.join(directory, request_path.lstrip('/'))

                if os.path.exists(php_request_path):
                    output = execute_php_script(php_request_path, query_string)
                    print("script_path:", php_request_path)

                    if output is not None:
                        # Send the PHP script's output as the response
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{output}"
                        conn.send(response.encode('utf-8'))

                    else:
                        # Handle PHP script execution error
                        send_error_response(conn, '500 Internal Server Error', 'Error executing PHP script')

                else:

                    send_error_response(conn, '404 Not Found', 'File not found')
            
            elif request_method == 'POST':
                pass
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
