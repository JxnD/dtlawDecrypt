import logging
import string
import os, uuid
from azure.storage.blob import BlobServiceClient, __version__
from azure.core.exceptions import ResourceExistsError
import azure.functions as func

#decryption function found from https://gist.github.com/AO8/5994342bd9fac0d5ecea18c054d5cbe1
#block blob samples found from https://github.com/Azure/azure-sdk-for-python/blob/c80bd0e57eead32aad9ee1177f30332458050cdf/sdk/storage/azure-storage-blob/samples/blob_samples_hello_world.py#L27

connection_string = ''


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
             "Please enter some input using ?name=",
             status_code=200
        )

def decrypt(text, shift):
    """ when the shift is known """
    decrypted_text = list(range(len(text)))
    alphabet = string.ascii_lowercase
    first_half = alphabet[:shift]
    second_half = alphabet[shift:]
    shifted_alphabet = second_half + first_half
    
    for i, letter in enumerate(text.lower()):

        if letter in alphabet:
            index = shifted_alphabet.index(letter)
            original_letter = alphabet[index]
            decrypted_text[i] = original_letter 
        else:
            decrypted_text[i] = letter

    return "".join(decrypted_text)

def brute_force_decrypt(text):
    """ when the shift is unknown """
    for n in range(26):
        permutationlist.append(decrypt(text, n))


def block_blob_sample():

        # Instantiate a new BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Instantiate a new ContainerClient
        container_client = blob_service_client.get_container_client("caesarcontainer")

        try:
            # Create new Container in the service
            container_client.create_container()
        except ResourceExistsError as error:
                print(error)

        try:
            # Instantiate a new BlobClient
            blob_client = container_client.get_blob_client("caesaroutput" + str(uuid.uuid4()))
            #convert permutationlist to string that can be written to blob
            outputstring = '\n'.join([str(item) for item in permutationlist])
            
            # Upload content to block blob
            blob_client.upload_blob(outputstring, blob_type="BlockBlob")
        
        finally:
            return func.HttpResponse("blob write success")
# F qefkh qexq qefp fp x mobqqv dlla buxjmib lc qeb ibkdqe tb tfii kbba ql molzbpp



