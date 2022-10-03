HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def status_code(response):
    if response.status_code == 200:
        return OKGREEN + str(response.status_code) + ENDC
    if response.status_code == 422:
        return FAIL + str(response.status_code) + ENDC
    else:
        return WARNING + response.reason + ENDC


