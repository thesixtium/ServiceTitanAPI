import close
import servicetitan
import read_requests

def main():
    read_requests.read(close.ping())

if __name__ == '__main__':
    main()
