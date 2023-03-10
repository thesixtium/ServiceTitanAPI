from datetime import datetime

def log(information):
    status = information[0]
    message = information[1]
    with open("log.txt", "a") as text_file:
        string = "[{}]\t{}\t{}\n".format(
            status,
            str(datetime.now()),
            message
        )
        text_file.write(string)
        print(string, end="")
