#---------------------------------------------------------- 
# Import User-defined, Standard, and Third-part Modules
#----------------------------------------------------------
import os, sys
import socket      
import datetime
from zipfile import ZipFile

#---------------------------------------------------------- 
# Zips Files in a Directory
#----------------------------------------------------------
def zipfiles(directory, dst):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
            
    with ZipFile(dst,'w') as zp:
        for file in file_paths:
            zp.write(file)
            
#---------------------------------------------------------- 
# Reads Zipped Files  a Directory
#----------------------------------------------------------            
def read_zip(zipname):
    """Reads Zipped File From Disk"""
    
    with open(zipname,'rb') as fp:
        fp.read()
        
#---------------------------------------------------------- 
# Writes Zipped Files to a Directory
#----------------------------------------------------------            
def write_zip(zipname, zippeddata):
    """Reads Zipped File From Disk"""
    
    with open(zipname, 'wb') as zp:
        zp.write(zippeddata)
        
#---------------------------------------------------------- 
# Gives Info About Zipped Files in a Directory
#----------------------------------------------------------
def get_zipinfo(src):
    """Gets Info About A Zipped File"""
  
    with ZipFile(src, 'r') as zip:
        for info in zip.infolist():
            print(info.filename)
            print('\tModified:\t' + str(datetime.datetime(*info.date_time)))
            print('\tSystem:\t\t' + str(info.create_system) + '(0 = Windows, 3 = Unix)')
            print('\tZIP version:\t' + str(info.create_version))
            print('\tCompressed:\t' + str(info.compress_size) + ' bytes')
            print('\tUncompressed:\t' + str(info.file_size) + ' bytes')
            
#---------------------------------------------------------- 
# Reads and sends zipped Data over Internet using sockets 
#----------------------------------------------------------
def send_zipped(namezipped):
    """Sends Zipped Data"""
    HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'                                                    
    PORT = int(sys.argv[2] if len(sys.argv) > 2 else 55555) 
    RECV_BYTES = 1024**2
    BYTEORDER_LENGTH = 8                                         
    CLIENT_SOCKET = socket.socket()    
    
    #0. Client Establishes connection with server
    CLIENT_SOCKET.connect((HOST, PORT)) 
    
    file_size = os.path.getsize(namezipped)
    
    file_byte_size = file_size.to_bytes(
                              BYTEORDER_LENGTH, 'big')
    
    # 1. Client sends "filesize" to server  
    CLIENT_SOCKET.send(file_byte_size)

    # 3. Client recieves "filesize rceived ACK"  
    msg = CLIENT_SOCKET.recv(ECV_BYTES).decode(FORMAT)                    
    
    # 5. Client sends "filename"   
    CLIENT_SOCKET.send("alem.zip".encode(FORMAT)) 

    # 7. Client recieves "filename rceived ACK"           
    msg = CLIENT_SOCKET.recv(ECV_BYTES).decode(FORMAT)                    
      
    
    # 9. Client sends "zipped Data" 
    with open(namezipped,'rb') as zp:
        CLIENT_SOCKET.send(zp.read())

    # 11. Client recieves "data rceived ACK"  
    msg = CLIENT_SOCKET.recv(ECV_BYTES).decode(FORMAT)
 
    CLIENT_SOCKET.close()
    
#---------------------------------------------------------- 
# Receives and writes zipped Data using sockets 
#----------------------------------------------------------
def recv_zipped(namezipped):
    """Receives Zipped Data"""
    HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'                                                    
    PORT = int(sys.argv[2] if len(sys.argv) > 2 else 55555) 
    RECV_BYTES = 1024**2
    BYTEORDER_LENGTH = 8                                         
    SERV_SOCKET = socket.socket()                                  
    SERV_SOCKET.setsockopt(socket.SOL_SOCKET, 
                           socket.SO_REUSEADDR, 1)                                                   
    SERV_SOCKET.bind((HOST, PORT))                                                                                      
    SERV_SOCKET.listen(1)
    
    while True:
        conn, addr = SERV_SOCKET.accept()                                          
        print(f"\033[33m[*] Listening as {HOST}:{PORT}\033[m")                                                    
        print(f"\033[32m[!] Client connected {addr}\033[m")

        # 2. Server receives size of zipped data from client
        file_byte_size = conn.recv(BYTEORDER_LENGTH)
        file_size= int.from_bytes(file_byte_size, 'big')

        # 4. Server sends ACK: 'File size received'
        conn.send("File size received.".encode(FORMAT))
        
        # 6. Server receives filename
        filename = conn.recv(RECV_BYTES).decode(FORMAT)

        # 8. Server sends ACK = Filename Recieve
        conn.send("Filename received.".encode(FORMAT))

        # 10. Server recieves Data.zip
        # Until the expected amount of data's received , keep receiving
        packet = b""  # Use bytes, not str, to accumulate
        t1 = time.perf_counter()
        while len(packet) < file_size:
             # if remaining bytes are more than the defined chunk size
            if(file_size - len(packet)) > RECV_BYTES : 
                # read SIZE bytes
                buffer = conn.recv(RECV_BYTES )  
            else:
                # read remaining number of bytes
                buffer = conn.recv(file_size - len(packet))  

            if not buffer:
                raise Exception("Incomplete file received")
            packet += buffer
    
        filename = '.\\dstzip\\'+filename
        with open(filename, 'wb') as zp:
            zp.write(packet)
    
        print(f"time: {time.perf_counter()-t1}")

        # 12. Server sends ACK = Filename Recieved
        conn.send("File data received".encode(FORMAT))
        conn.close()
    SERV_SOCKET.close()
#---------------------------------------------------------- 
#                    ~END~ 
#----------------------------------------------------------