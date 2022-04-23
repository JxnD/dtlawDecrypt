import logging
import string
import os, uuid
from unicodedata import name
from azure.storage.blob import BlobServiceClient, __version__
from azure.core.exceptions import ResourceExistsError
from pycipher import ColTrans
import azure.functions as func

#decryption function found from https://github.com/hywhuangyuwei/columnar-transposition-cipher-brute-force-decipher
#block blob samples found from https://github.com/Azure/azure-sdk-for-python/blob/c80bd0e57eead32aad9ee1177f30332458050cdf/sdk/storage/azure-storage-blob/samples/blob_samples_hello_world.py#L27

connection_string = ''
permutationlist = []
dicFilename = 'dict.txt'
maxKeyLength = 6
ranked = []

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
        sortoutput(name)
        # append output from decryption function to blob storage
        block_blob_sample()   
        return func.HttpResponse("The permutations have been successfully saved")
            
    else:
        return func.HttpResponse(
             "Please enter some input using ?name=",
             status_code=200
        )

def bruteForceDecipher(cipherText, perms, dic):
    '''
    params: cipherText, permutations, dictionary

    return: decipher result with score by brute force method
    '''
    index = 0
    ranked = []

    # seach all possible keys
    for key in perms:
        index += 1
        if (index % 10000 == 0):
            print(index, 'th', end=' ')
            print('Key:', key)

        # input: key, cipherText
        # output: plainText
        plainText = ColTrans(key).decipher(cipherText)

        # get a `score` for the key
        # score = the number of words exist both in the plainText and in the dictionary
        score = 0
        wordFound = []
        for word in dic:
            _cnt = plainText.count(word)
            if _cnt > 0:
                score += _cnt
                wordFound.append(word.lower())
        ranked.append([score, plainText, ','.join(wordFound)])

    return ranked

def getAllPermutation(n):
    '''
    params: n

    return: a list of all permutations of n, each item is a string
    '''
    global _perms

    def perm(n, begin, end):
        global _perms
        if begin >= end:
            _perms += n
        else:
            i = begin
            for num in range(begin, end):
                n[num], n[i] = n[i], n[num]
                perm(n, begin + 1, end)
                n[num], n[i] = n[i], n[num]
    a = []
    for i in range(1, n+1):
        a.append(i)
    perm(a, 0, n)
    res = []
    temp = 1
    for w in range(1, n+1):
        temp *= w
    for j in range(0, temp):
        tmp = _perms[j*n:j*n+n]
        tmp = list(map(str, tmp))
        tmp = ''.join(tmp)
        res.append(tmp)

    return res

def importWords(filename):
    '''
    input: filename of dictionary

    output: a list containing all words IN UPPER CASE in the dictionary
    '''
    dic = []
    with open(filename, 'r') as file:
        line = file.readline()
        while line:
            line = line[:-1].upper()
            dic.append(line)
            line = file.readline()
        return dic



dic = importWords(dicFilename)
_perms = []

def sortoutput(name):
    global ranked
    for i in range(1, maxKeyLength+1):
        perms = getAllPermutation(i)
        ranked += bruteForceDecipher(name, perms, dic)

    ranked = sorted(ranked, key=lambda item: item[0], reverse=True)
    for i in range(50):
        permutationlist.append(ranked[i][1].lower())

def block_blob_sample():

        # Instantiate a new BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Instantiate a new ContainerClient
        container_client = blob_service_client.get_container_client("coltrancontainer")

        try:
            # Create new Container in the service
            container_client.create_container()
        except ResourceExistsError as error:
                print(error)

        try:
            # Instantiate a new BlobClient
            blob_client = container_client.get_blob_client("coltranoutput" + str(uuid.uuid4()))
            #convert permutationlist to string that can be written to blob
            outputstring = '\n'.join([str(item) for item in permutationlist])
            
            # Upload content to block blob
            blob_client.upload_blob(outputstring, blob_type="BlockBlob")
        
        finally:
            return func.HttpResponse("blob write success")


## 'TNHTSAEYOXPOHETELETREIITTISRTOEMETLGWINDPCSHKAHIPTGDALFENHWLEOOS'


