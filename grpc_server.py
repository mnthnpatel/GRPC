# import grpc
# from concurrent import futures
# import file_transfer_pb2
# import file_transfer_pb2_grpc
# import logging

# logging.basicConfig(filename='grpc_server.log', level=logging.DEBUG,
#                     format='%(asctime)s %(levelname)s: %(message)s')


# class FileTransferServicer(file_transfer_pb2_grpc.FileTransferServicer):
#     # def UploadFile(self, request_iterator, context):
#     #     try:
#     #         with open("uploaded_file", "wb") as f:  # Replace with your desired file path
#     #             for chunk in request_iterator:
#     #                 f.write(chunk.content)
#     #         return file_transfer_pb2.FileUploadStatus(message="File uploaded successfully", success=True)
#     #     except Exception as e:
#     #         return file_transfer_pb2.FileUploadStatus(message=f"File upload failed: {e}", success=False)
#     # def UploadFile(self, request_iterator, context):
#     #     try:
#     #         # Initialize filename variable to store the received filename
#     #         filename = None

#     #         # Iterate through the request_iterator to get the filename and content
#     #         for chunk in request_iterator:
#     #             if not filename:
#     #                 filename = chunk.filename  # First chunk contains filename
#     #             with open(filename, "ab") as f:  # Append to file
#     #                 f.write(chunk.content)
#     #         return file_transfer_pb2.FileUploadStatus(message="File uploaded successfully", success=True)
#     #     except Exception as e:
#     #         return file_transfer_pb2.FileUploadStatus(message=f"File upload failed: {e}", success=False)

#     def UploadFile(self, request, context):
#         filename = request.filename
#         print(filename)
#         content = request.content

#         # Process the received file chunk
#         try:
#             # Example: Save the file chunk to disk
#             with open(f"/home/cmanthan/leo/{filename}", "ab") as f:
#                 f.write(content)

#             # Print server-side log
#             print(
#                 f"Received chunk with {len(content)} bytes for file: {filename}")

#             return file_transfer_pb2.FileUploadStatus(message=f"Chunk for {filename} received", success=True)

#         except Exception as e:
#             print(f"Error processing file chunk: {e}")
#             return file_transfer_pb2.FileUploadStatus(message=f"Error processing chunk for {filename}", success=False)

#         def UploadFile(self, request_iterator, context):
#         filename = None
#         try:
#             print("123456")
#             chunks = list(request_iterator)
#             #print("chunks........... ",chunks)
#             print("12345")
#             for file_chunk in request_iterator:
#                 print("inside for looop")
#                 print("filename............. ", file_chunk.filename)
#                 # Set the filename from the first chunk
#                 if filename is None:
#                     filename = file_chunk.filename
#                     if not filename:
#                         raise ValueError("Filename not provided in the first chunk")
#                     print(f"Receiving file: {filename}")

#                 # Process file content chunks
#                 content = file_chunk.content
#                 if content:
#                     print(f"Received chunk with {len(content)} bytes")
#                     with open(f"/home/cmanthan/leo/{filename}", "ab") as f:
#                         f.write(content)

#             return file_transfer_pb2.FileUploadStatus(message=f"File {filename} received", success=True)

#         except Exception as e:
#             print(f"Error processing file chunks: {e}")
#             return file_transfer_pb2.FileUploadStatus(message=f"Error processing file: {e}", success=False)


# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     file_transfer_pb2_grpc.add_FileTransferServicer_to_server(
#         FileTransferServicer(), server)
#     server.add_insecure_port('[::]:50051')  # Use the port you prefer
#     server.start()
#     logging.info("Server started. Listening on port 50051.")
#     server.wait_for_termination()


# if __name__ == "__main__":
#     serve()
import grpc
from concurrent import futures
import file_transfer_pb2
import file_transfer_pb2_grpc
import logging

logging.basicConfig(filename='grpc_server.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')


class FileTransferServicer(file_transfer_pb2_grpc.FileTransferServicer):
    def UploadFile(self, request_iterator, context):
        try:
            # chunks = list(request_iterator)
            # print("chunk_filename....... ",chunks.filename)
            # with open(chunks.filename, "wb") as f:  # Replace with your desired file path
            for chunk in request_iterator:
                print("filename........... ", chunk.filename)
                with open(f"/home/cmanthan/leo/{chunk.filename}", "ab") as f:
                    f.write(chunk.content)
            return file_transfer_pb2.FileUploadStatus(message="File uploaded successfully", success=True)
        except Exception as e:
            return file_transfer_pb2.FileUploadStatus(message=f"File upload failed: {e}", success=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_transfer_pb2_grpc.add_FileTransferServicer_to_server(
        FileTransferServicer(), server)
    server.add_insecure_port('[::]:50051')  # Use the port you prefer
    server.start()
    logging.info("Server started. Listening on port 50051.")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
