import os

# Get the username of the current user
# user = os.getlogin()

source_dir = {
    "default" : "C:/Users/GHBservice/Downloads"
    # "default": f"C:/Users/{user}/Downloads"
    # "default" : "C:/Downloads"
}


def destination_dir(input_date, biller):
    # pre_destination_dir = f"E:/my_work_OLD/_Git/Python/DI2/download/{input_date}/"

    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    pre_destination_dir = os.path.join(parent_dir, 'download', input_date, '')

    destination_dirs = {
        "counter_service": pre_destination_dir + "counter_service",
        "mpay": pre_destination_dir + "mpay",
        "true": pre_destination_dir + "true",
        "lotus": pre_destination_dir + "lotus",
        "lotus-tims": pre_destination_dir + "lotus-tims",
        "baac": pre_destination_dir + "baac",
        "thaipost": pre_destination_dir + "thaipost"
    }

    default_path = pre_destination_dir + "default"
    return destination_dirs.get(biller, default_path)

username = {
    "counter_service": "ghb",
    "mpay": "govebank",
    "true": "ghbadmin",
    "lotus" : "GHB0001",
    "lotus-tims" : "ac70344",
    "baac" : "ghb"
}

password = {
    "counter_service": "ghbwyq444444",
    "mpay": "G0veB@nK",
    "true": "ghbpassword",
    "lotus" : "pASSWORD@37",
    "lotus-tims" : "Password18",
    "baac" : "Ghb@12345"
}

secret_code = {
    "lotus" : "3520000101"
}

############# SFTP Serv U ##############################
env = "PROD"

# Dictionary holding configuration for different environments
SERV_U_CONFIGS = {
    "UAT": {
        "ip": "172.29.66.17",
        "username": "AS400CMS",
        "password": "GHB#123",
        "port": "22"
    },
    "PROD": {
        "ip": "172.29.81.38",
        "username": "parut.s",
        "password": "GHB#123",
        "port": "22"
    }
}

# Get the configuration based on the environment, defaulting to UAT if not found
SERV_U_CONFIG = SERV_U_CONFIGS.get(env.upper(), SERV_U_CONFIGS["UAT"])


# PRE_SERV_U_PATH = "/U5/DCR"
PRE_SERV_U_PATH = "/DCR"

SERV_U_PATH = {
    "counter_service": PRE_SERV_U_PATH + "/CST/IN/",
    "mpay": PRE_SERV_U_PATH + "/AMP/IN/",
    "true": PRE_SERV_U_PATH + "/TRUE/IN/",
    "lotus" : PRE_SERV_U_PATH + "/TESCO/IN/",
    "baac" : PRE_SERV_U_PATH + "/BAAC/IN/",
    "thaipost" : PRE_SERV_U_PATH + "/CAT/IN/",
}

############# !! SFTP Serv U ##############################

############# FTP ThaiPost ##############################
FTP_THAIPOST_CONFIG = {
    "ip": "ftp.payatpost.com",
    "username": "ghbank",
    "password": "ghbAnk",
    "port": "21"
}

FTP_THAIPOST_PATH = "/"

############# !!FTP ThaiPost ##############################


WAIT_TIME = 10  # Maximum wait time in seconds
WAIT_INTERVAL = 1  # Interval between wait checks in seconds
WAIT_LONG_TIME = 30

WAIT_TIMES = {
    "1" : 1,
    "5" : 5,
    "10" : 10,
    "30" : 30,
}