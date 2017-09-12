import os
import git
import logging
if __name__ == "__main__":
    g = git.cmd.Git(".")
    while True: 
        logging.error("\033[31mRELOADING SERVER\033[0m")
        status = os.system("python app.py")
        if status: break
        g.pull()
        #os.system("git pull https://github.com/cs196illinois/fall-2017-website.git") 
