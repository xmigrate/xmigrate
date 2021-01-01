import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def logger(message, type):
    if type == "debug":
        logging.debug(message)
    elif type == "warning":
        logging.warning(message)
    elif type == "info":
        logging.info(message)
    elif type == "error":
        logging.error(message)
    elif type == "critical":
        logging.critical(message)
    

