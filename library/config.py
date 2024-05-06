source_dir = {
    #"default" : "C:/Users/GHBservice/Downloads",
    "default" : "C:/Downloads",
}

pre_destination_dir = "D:/_GHB"
# pre_destination_dir = "E:/my_work_OLD/_Git"

destination_dir = {
    "counter_service": pre_destination_dir + "/Python/DI2/download/counter_service",
    "mpay": pre_destination_dir + "/Python/DI2/download/mpay",
    "true": pre_destination_dir + "/Python/DI2/download/true",
    "lotus": pre_destination_dir + "/Python/DI2/download/lotus",
}

username = {
    "counter_service": "ghb",
    "mpay": "govebank",
    "true": "ghbadmin",
    "lotus" : "GHB0001",
    "baac" : "ghb"
}

password = {
    "counter_service": "ghbwyq444444",
    "mpay": "G0veB@nK",
    "true": "ghbpassword",
    "lotus" : "pASSWORD@36",
    "baac" : "Ghb@12345"
}

secret_code = {
    "lotus" : "3520000101"
}

WAIT_TIME = 10  # Maximum wait time in seconds
WAIT_INTERVAL = 1  # Interval between wait checks in seconds
WAIT_LONG_TIME = 30

WAIT_TIMES = {
    "1" : 1,
    "5" : 5,
    "10" : 10,
    "30" : 30,
}