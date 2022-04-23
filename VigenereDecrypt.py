import logging
import string
import os, uuid
import itertools
from azure.storage.blob import BlobServiceClient, __version__
from azure.core.exceptions import ResourceExistsError
import azure.functions as func

#block blob samples found from https://github.com/Azure/azure-sdk-for-python/blob/c80bd0e57eead32aad9ee1177f30332458050cdf/sdk/storage/azure-storage-blob/samples/blob_samples_hello_world.py#L27
#vigenere decryption found from https://github.com/d819r197/BruteForceDecryption/blob/master/VigenereCipher.py

connection_string = ''
permutationlist = []


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        # Call decryption function with input of httptrigger
        brute_force_decrypt(name)
        # append output from decryption function to blob storage
        block_blob_sample()   
        return func.HttpResponse("The permutations have been successfully saved")
            
    else:
        return func.HttpResponse(
             "Please enter some input using ?name=ciphertext or &name=ciphertext",
             status_code=200
        )

def charToInt(cIn):
    cLower = cIn.lower()
    return ord(cLower) - 97


def intToChar(iIn):
    return chr(iIn + 97)


def decrypt(cypherText, key):
    keyLen = len(key)
    keyIndex = 0
    plainText = ""
    for c in cypherText:
        letter = intToChar((charToInt(c) - charToInt(key[keyIndex])) % 26)
        plainText += letter
        keyIndex += 1
        if keyIndex == keyLen:
            keyIndex = 0
    return plainText


def importDict(path, size):
    dict = []
    file = open(path, "r")
    fileLines = file.readlines()

    for line in fileLines:
        # print("Adding Key: "+ line[0:len(line)-1] +" of Size: " + str(len(line)-1))
        if len(line) - 1 == size:
            dict.append(str(line[0:len(line) - 1]).lower())
    return dict



def brute_force_decrypt(ciphertext):
    dictPath = "dict.txt"
    ct = ciphertext
    keyLen = int(3)
    fwLen = int(4)
    dict = importDict(dictPath, int(fwLen))
    brokenCT = [ct[i:i + fwLen] for i in range(0, len(ct), fwLen)]
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
                "v", "w", "x", "y", "z"]
    alphabetCombos = [alphabet] * keyLen
    possibleKeys = list(itertools.product(*alphabetCombos))
    firstCypher = brokenCT[0]
    for key in possibleKeys:
        pt = decrypt(firstCypher, key)
        if pt in dict:
            fullPT = decrypt(ct, key)
            permutationlist.append(fullPT)

    return permutationlist


def block_blob_sample():

        # Instantiate a new BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Instantiate a new ContainerClient
        container_client = blob_service_client.get_container_client("vigenerecontainer")

        try:
            # Create new Container in the service
            container_client.create_container()
        except ResourceExistsError as error:
                print(error)

        try:
            # Instantiate a new BlobClient
            blob_client = container_client.get_blob_client("vigenereoutput" + str(uuid.uuid4()))
            #convert permutationlist to string that can be written to blob
            outputstring = '\n'.join([str(item) for item in permutationlist])
            
            # Upload content to block blob
            blob_client.upload_blob(outputstring, blob_type="BlockBlob")
        
        finally:
            return func.HttpResponse("blob write success")




