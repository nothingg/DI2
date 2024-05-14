

source_dir = {
    # "default" : "C:/Users/GHBservice/Downloads",
    "default" : "C:/Downloads"
}

# pre_destination_dir = "D:/_GHB"
pre_destination_dir = "E:/my_work_OLD/_Git"

destination_dir = {
    "counter_service": pre_destination_dir + "/Python/DI2/download/counter_service",
    "mpay": pre_destination_dir + "/Python/DI2/download/mpay",
    "true": pre_destination_dir + "/Python/DI2/download/true",
    "lotus": pre_destination_dir + "/Python/DI2/download/lotus",
    "lotus-tims": pre_destination_dir + "/Python/DI2/download/lotus-tims",
    "baac": pre_destination_dir + "/Python/DI2/download/baac",
}

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
env = "UAT"

# Dictionary holding configuration for different environments
SERV_U_CONFIGS = {
    "UAT": {
        "ip": "172.29.66.17",
        "username": "AS400CMS",
        "password": "GHB#123",
        "port": "22"
    },
    "PROD": {
        "ip": "172.29.66.18",
        "username": "u_prod",
        "password": "1234",
        "port": "22"
    }
}

# Get the configuration based on the environment, defaulting to UAT if not found
SERV_U_CONFIG = SERV_U_CONFIGS.get(env.upper(), SERV_U_CONFIGS["UAT"])


PRE_SERV_U_PATH = "/U5/DCR"

SERV_U_PATH = {
    "counter_service": PRE_SERV_U_PATH + "/CST/IN/",
    "mpay": "govebank",
    "true": "ghbadmin",
    "lotus" : "GHB0001",
    "lotus-tims" : "ac70344",
    "baac" : "ghb"
}

############# !! SFTP Serv U ##############################

WAIT_TIME = 10  # Maximum wait time in seconds
WAIT_INTERVAL = 1  # Interval between wait checks in seconds
WAIT_LONG_TIME = 30

WAIT_TIMES = {
    "1" : 1,
    "5" : 5,
    "10" : 10,
    "30" : 30,
}