import grpc
import paramiko
import file_transfer_pb2 as file_transfer_pb2
import file_transfer_pb2_grpc as file_transfer_pb2_grpc
import os
import logging
import time
import speedtest


class CloudService:
    @classmethod
    def connect(cls, hostname, port, username, password):
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username)

        # Authenticate using keyboard-interactive
        def keyboard_interactive_handler(title, instructions, prompts):
            responses = []
            for prompt, _ in prompts:
                if 'Type the string above:' in prompt:
                    captcha = prompt[prompt.find(
                        '( ') + 2:prompt.find(' )')].replace('|', '').replace(' ', '')
                    responses.append(captcha)
                elif 'Password: ' in prompt:
                    responses.append(password)
                else:
                    continue
            return responses

        transport.auth_interactive(username, keyboard_interactive_handler)

        if transport.is_authenticated():
            return transport
        else:
            return None

    @classmethod
    def check_files_and_install_grpc(cls, ssh, files_present_directory, local_directory, virtual_env_path):
        required_files = ["file_transfer_pb2.py",
                          "file_transfer_pb2_grpc.py", "grpc_server.py"]

        # Upload each file from local_directory to remote_directory if not found
        for file in required_files:
            stdin, stdout, stderr = ssh.exec_command(
                f"test -f {files_present_directory}/{file} && echo 'Found' || echo 'Not Found'")
            output = stdout.read().decode().strip()
            if output != "Found":
                print(
                    f"{file} not found in {files_present_directory} on the remote server. Uploading...")
                sftp = ssh.open_sftp()
                sftp.put(f"{local_directory}/{file}",
                         f"{files_present_directory}/{file}")
                sftp.close()
                print(f"{file} uploaded successfully.")
            else:
                print(
                    f"{file} is present in {files_present_directory} on the remote server.")

        # Check if gRPC is installed in the specified virtual environment and install if necessary
        # grpcio                  1.65.0
        # grpcio-tools            1.65.0

        stdin, stdout, stderr = ssh.exec_command(
            f"{virtual_env_path}/bin/pip show grpcio grpcio-tools")
        output = stdout.read().decode()
        if "grpcio" not in output or "grpcio-tools" not in output:
            print(
                "gRPC is not installed in the specified virtual environment. Installing now...")
            stdin, stdout, stderr = ssh.exec_command(
                f"{virtual_env_path}/bin/pip install grpcio grpcio-tools==1.65.0")
            stdout.channel.recv_exit_status()  # Wait for the command to complete
            print("gRPC installed successfully in the specified virtual environment.")
        else:
            print("gRPC is already installed in the specified virtual environment.")

        # Execute grpc_server.py if it exists
        # stdin, stdout, stderr = ssh.exec_command(f"test -f {remote_directory}/grpc_server.py && echo 'Found' || echo 'Not Found'")
        # output = stdout.read().decode().strip()
        # if output == "Found":
        #     print("Executing grpc_server.py on remote server...")
        #     stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_directory}/grpc_server.py")
        #     print("grpc_server.py executed on remote server.")
        # else:
        #     print("grpc_server.py not found in remote directory. Skipping execution.")

    @classmethod
    def upload_file(cls, transport, hostname, grpc_port, local_file_path):
        try:
            # Start gRPC file transfer

            with grpc.insecure_channel(f"localhost:{grpc_port}") as channel:
                stub = file_transfer_pb2_grpc.FileTransferStub(channel)

                def file_chunks():
                    filename = os.path.basename(local_file_path)
                    print(f"Sending filename: {filename}")
                    yield file_transfer_pb2.FileChunk(filename=filename, content=b'')

                    with open(local_file_path, "rb") as f:
                        # Adjust chunk size as needed
                        while chunk := f.read(1024 * 1024):
                            print(
                                f"Sending chunk with size: {len(chunk)} bytes")
                            yield file_transfer_pb2.FileChunk(filename=filename, content=chunk)
                # filename = os.path.basename(local_file_path)
                # print(filename)

                # with open(local_file_path, "rb") as f:
                #     chunk_size = 1024 * 1024  # 1 MB chunks (adjust as needed)
                #     chunk = f.read(chunk_size)
                #     while chunk:
                #         # Prepare FileChunk message
                #         chunk_message = file_transfer_pb2.FileChunk(
                #             content=chunk,
                #             # filename=filename
                #         )
                #         response = stub.UploadFile(chunk_message)
                #         # Print progress or handle response as needed
                #         print(f"Uploaded {len(chunk)} bytes")
                #         chunk = f.read(chunk_size)

                def get_internet_speed():
                    st = speedtest.Speedtest()
                    st.get_best_server()
                    download_speed = st.download() / 1_000_000  # Convert to Mbps
                    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
                    return download_speed, upload_speed

                # download_speed, upload_speed = get_internet_speed()
                # print(f"Internet Speed - Download: {download_speed:.2f} Mbps, Upload: {upload_speed:.2f} Mbps")

                start_time = time.time()
                response = stub.UploadFile(file_chunks())
                end_time = time.time()
                print(
                    f"Upload status: {response.message}, Success: {response.success}")
                print(f"Execution time: {end_time - start_time} seconds")

                # if response.success:
                #     # Move uploaded file to specified remote directory
                #     ssh = paramiko.SSHClient()
                #     ssh._transport = transport
                #     sftp = ssh.open_sftp()
                #     sftp.put(local_file_path, f"{remote_directory}/{local_file_path.split('/')[-1]}")
                #     sftp.close()
                #     ssh.close()
                #     print(f"File '{local_file_path}' uploaded to '{remote_directory}' on the remote server.")

                #     # Check for required files in the remote directory after upload
                #     CloudService.check_files_and_install_grpc(ssh, remote_directory)

                return response.success

                # print("Okay...!!", response.success)

        except Exception as e:
            print(f"Error: {e}")
            return False


if __name__ == "__main__":
    hostname = 'hostname'  # Your Host Name Here...
    ssh_port = 22  # SSH port on your cloud server
    grpc_port = 50051  # gRPC port on your cloud server
    username = 'username'  # Username
    password = 'password'  # Password
    local_file_path = 'D:/Extra/Technical/TestFiles'
    # local_file_path = 'D:/Extra/Technical/GRPC'
    virtual_env_path = '/home/cmanthan/miniconda3/envs/leo_env'
    files_present_directory = '/home/cmanthan/leo'
    # Specify the remote directory where you want to upload
    upload_file_path = '/home/cmanthan/leo'

    try:
        transport = CloudService.connect(
            hostname, ssh_port, username, password)

        if not transport:
            print("Failed to connect to cloud server.")
        else:
            print("Connected to cloud server successfully!")

            ssh = paramiko.SSHClient()
            ssh._transport = transport

            # List files in the directory
            files_to_upload = os.listdir(local_file_path)
            print(files_to_upload)

            # Check for required files in the remote directory and install gRPC if necessary
            CloudService.check_files_and_install_grpc(
                ssh, files_present_directory, local_file_path, virtual_env_path)
            for file in files_to_upload:
                file_path = os.path.join(local_file_path, file)
                # Upload file using gRPC and move it to specified remote directory
                upload_success = CloudService.upload_file(
                    transport, hostname, grpc_port, file_path)
                if upload_success:
                    print(
                        f"File '{file}' uploaded successfully using gRPC.")
                else:
                    print(f"Failed to upload file '{file}' using gRPC.")

        # Close the SSH client
        ssh.close()

    except Exception as e:
        print(f"Connection error: {e}")

    finally:
        if transport:
            transport.close()
