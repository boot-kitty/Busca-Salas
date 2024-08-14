# Imports:
from colorama import Fore, Back, Style

# -------------------------------------------------------------------------------------------------

# Funciones:

def console_log(message:str, message_type="") -> None:

    if message_type == "warning":
        print(Fore.YELLOW + message + Style.RESET_ALL)

    elif message_type == "error":
        print(Fore.RED + message + Style.RESET_ALL)

    elif message_type == "success":
        print(Fore.GREEN + message + Style.RESET_ALL)
        
    else:
        print(message)