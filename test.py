# APS

import os
from dotenv import load_dotenv
import subprocess

#to trigger secret scanning
user = 'test'
password = 'Password1234'

google_api_token = "AIzaSyAQfxPJiounkhOjODEO5ZieffeBv6yft2Q"
gh_PAT = "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"


def dangerous(user_input):
    # BAD: user input is passed directly to shell=True, which is dangerous!
    subprocess.call(f"echo {user_input}", shell=True)

# main
if __name__ == '__main__':

    print('hello Github world')

    user_input = input("Enter something: ")
    dangerous(user_input)
