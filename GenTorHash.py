from stem.process import launch_tor_with_config
from stem.control import Controller

from subprocess import Popen, PIPE
import logging



def genTorPassHash(password):
    """ Launches a subprocess of tor to generate a hashed <password> """
    logging.info("Generating a hashed password")
    torP = Popen(
            ['tor', '--hush', '--hash-password', str(password)],
            stdout=PIPE,
            bufsize=1
            )
    try:
        with torP.stdout:
            for line in iter(torP.stdout.readline, b''):
                line = line.strip('\n')
                if "16:" not in line:
                    logging.debug(line)
                else:
                    passhash = line
        torP.wait()
        logging.info("Got hashed password")
        return passhash
    except Exception:
        raise


password = input('password: ')
password_hash = genTorPassHash(password)
print(password, "\n")
print(password_hash)