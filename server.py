import socket
import os
import subprocess


def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except Exception as e:
        print("Error reading file:", e)
        return None



def execute_php_script(script_content, query_string):
    try:
        # Create a temporary PHP script file
        temp_script_path = "temp.php"
        with open(temp_script_path, 'w') as temp_script_file:
            temp_script_file.write(script_content)

        # Use PHP to execute the temporary script with the query string
        php_command = ['php', temp_script_path, query_string]
        php_process = subprocess.Popen(
            php_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Capture the output (HTML content) from PHP
        php_output, php_errors = php_process.communicate()

        # Remove the temporary PHP script file
        os.remove(temp_script_path)

        return php_output.decode('utf-8')
    except Exception as e:
        print("Error executing PHP script:", e)
        return None



def send_error_response(client_socket, status, message):
    response = f"HTTP/1.1 {status}\r\nContent-Type: text/html\r\n\r\n<h1>{status}</h1><p>{message}</p>"
    client_socket.send(response.encode('utf-8'))

def httpserver(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print("Server is listening on port %s" % port)

    while True:
        conn, addr = s.accept()
        #print("Connection from:", addr)
        
        request = conn.recv(4096).decode('utf-8')
        request_lines = request.split('\r\n')
        request_method, request_path, _ = request_lines[0].split()

        #print("Request:", request)
        #print("Request Method:", request_method)
        #print("Request Path:", request_path)

        # Handle GET request
        if request_method == 'GET':
            # Check if the requested file is a PHP script
            if request_path.endswith('.php'):
                script_path = os.path.join("htdocs", request_path.lstrip('/'))
                query_string = ''  # Initialize the query string as empty
                if '?' in script_path:
                    script_path, query_string = script_path.split('?')
                if os.path.exists(script_path):
                    script_content = read_file_content(script_path)
                    output = execute_php_script(script_content, query_string)
                    print("script_path:", script_path)
                    if output is not None:
                        # Send the PHP script's output as the response
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{output}"
                        conn.send(response.encode('utf-8'))
                    else:
                        # Handle PHP script execution error
                        send_error_response(conn, '500 Internal Server Error', 'Error executing PHP script')
                else:
                    send_error_response(conn, '404 Not Found', 'File not found')
            else:
                # Handle serving static files here
                # You need to send the file content as the response
                # Ensure you handle 404 errors for static files as well
                pass

        elif request_method == 'POST':
            pass
        else:
            send_error_response(conn, '405 Method Not Allowed', 'Method not allowed')

        # Close the connection
        conn.close()

host = "127.0.0.1"
port = 2728
httpserver(host, port)
