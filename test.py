# APS

import os
from dotenv import load_dotenv

#to trigger secret scanning
user = 'test'
password = 'Password1234'

google_api_token = "AIzaSyAQfxPJiounkhOjODEO5ZieffeBv6yft2Q"
gh_PAT = "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"

def insecure_eval(user_input):
    # BAD: using eval on untrusted input
    result = eval(user_input)
    return result

# main
if __name__ == '__main__':

    print('hello Github world')

    user_input = input("Enter something: ")
    print(insecure_eval(user_input))
