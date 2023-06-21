#Importing the modules
from cryptography.fernet import Fernet
import os

#Creating a class with encryption and decryption methods
class Want_to_crypt:
    def __init__(self, file_name):
        self.file_name = file_name

    #Create new file new
    def new_name(self, flag):
        
        #Splitting the file name and file extension
        split_up = os.path.splitext(self.file_name)
        
        file_name = split_up[0]
        file_extension = split_up[1]
        
        #Checking if we want to crypt or decrypt
        if flag == 1:
            file_name = file_name + '_encrypted'
            return file_name + file_extension
        
        if flag == 2:
            if '_encrypted' in file_name:
                file_name = file_name.replace('_encrypted', "")
                file_name = file_name + '_decrypted'
            else:
                file_name = file_name + '_decrypted'
            return file_name + file_extension
            
        raise ValueError('Flag can only have value of 1 or 2!')
            
        
    #Encryption
    def encrypt(self, path):
        
        #Creating a the key
        key = Fernet.generate_key()
        
        #Creating a file with the key in specific folder
        key_filepath = os.path.join(path, 'key' + '_' + self.file_name + '.key')
        with open(key_filepath, 'wb') as filekey:
            filekey.write(key)
            
        fernet = Fernet(key)
        
        #Check if the audio file can be open
        try:
            f = open(os.path.join(path, self.file_name))
            print('File for encrypt can be opened!')
            f.close()
        except: raise IOError('File for encrypt cannot be opened!')
        
        #Read our audio file
        with open(os.path.join(path, self.file_name), 'rb') as file:
            original_audio = file.read()
            
        #Encrypt the data
        encrypted = fernet.encrypt(original_audio)

        #Create the encrypted file in specific folder
        with open(os.path.join(path, self.new_name(1)), 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
            
            
    #Decryption
    def decrypt(self, path, key_file):

        #Checking if the key file can be open
        try:
            f = open(os.path.join(path, key_file))
            print('Key for decrypt can be opened!')
            f.close()
        except: raise IOError('Key for decrypt cannot be opened!')
        
        with open(os.path.join(path, key_file), 'rb') as key_data:
            key = key_data.read()
        
        fernet = Fernet(key)
        
        #Check if the encrypted file can be open
        try:
            f = open(os.path.join(path, self.file_name))
            print('File for decrypt can be opened!')
            f.close()
        except: raise IOError('File for decrypt cannot be opened!')

        #Read the encrypted file
        with open(os.path.join(path, self.file_name), 'rb') as encrypted_file:
            encrypted = encrypted_file.read()
            
        #Decrypt the data
        decrypted = fernet.decrypt(encrypted)

        #Create the decrypted file
        with open(os.path.join(path, self.new_name(2)), 'wb') as decrypted_file:
            decrypted_file.write(decrypted)
