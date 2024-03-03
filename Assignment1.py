from __future__ import annotations

from typing import Any
from functools import wraps


class BaseCliHelperException(Exception):
    """This is a generic Cli Helper exception."""


class CommandNotSupported(BaseCliHelperException):
    """This exception is to be raised when Cli Helper encounters a non-supported command."""


class CliHelperSigStop(BaseCliHelperException):
    """This exception is to be raised whenever we need to immediately stop the bot."""


class CommandOperationalError(BaseCliHelperException):
    """This exception is raised whenever we try to do an operation that is not allowed."""


def input_error(error_msg_base):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (CommandOperationalError, CommandNotSupported) as e:
                return f"{error_msg_base}: {e}"

        return wrapper
    return decorator


class CliHelperBot:
    _users_cache = {}

    def __init__(self):
        self.supported_commands = {
            "close": self.stop,
            "exit": self.stop,
            "hello": self.say_hello,
            "add": self.add_contact,
            "change": self.change_contact,
            "phone": self.get_contact,
            "all": self.print_all_contacts
        }

    def stop(self, message: str):
        """Stop the bot execution.

        Args:
            message: Explanation why bot needs to stop

        Raises:
            CliHelperSigStop: with explanation message
        """
        raise CliHelperSigStop(message)

    @staticmethod
    def parse_input(user_input: str) -> (str, list[Any]):
        command, *args = user_input.split()
        command = command.casefold()

        if command in ["close", "exit"]:
            args = [f"Command '{command}' received. Good buy!"]

        return command, args

    @staticmethod
    def say_hello(*args: str) -> str:
        """Outputs a hello message for user."""
        command_output = ""
        if args:
            command_output += (
                "Warning: Command doesn't expect any arguments. "
                f"Received: {' '.join(args)}\n"
            )

        return command_output + "How can I help you?"

    @input_error(error_msg_base="Command 'add' failed")
    def add_contact(self, *args: str) -> str:
        """Add contact into _users_cache.

        Args:
            args: List with username and phone of user to add.

        Returns:
            Command output.

        Raises:
            CommandOperationalError: if wrong arguments or user already exist
        """
        if len(args) != 2:
            raise CommandOperationalError(
                "command expects an input of two arguments: username and phone, separated by a space. "
                f"Received: {' '.join(args)}"
            )

        username, phone = args
        if username in self._users_cache:
            raise CommandOperationalError(
                f"user with username {username} already exist. "
                f"If you want to update number, please use 'change' command."
            )

        self._update_number(username, phone)
        return f"Contact {username} created with phone: {phone}."

    @input_error(error_msg_base="Command 'update' failed")
    def change_contact(self, *args: str) -> str:
        """Change contact in _users_cache.

        Args:
            args: List with username and phone of user to add.

        Returns:
            Command output.

        Raises:
            CommandOperationalError: if wrong arguments or user doesn't exist
        """
        if len(args) != 2:
            raise CommandOperationalError(
                "command expects an input of two arguments: username and phone, separated by a space. "
                f"Received: {' '.join(args)}"
            )

        username, phone = args
        if username not in self._users_cache:
            raise CommandOperationalError(
                f"user with username {username} doesn't exist. "
                f"If you want to add number, please use 'add' command."
            )

        self._update_number(username, phone)
        return f"Contact {username} updated with phone: {phone}."

    def _update_number(self, username: str, phone: str) -> bool:
        """Updates number in _users_cache by key.

        Args:
            username: Username key
            phone: Phone value

        Returns:
            True if success.
        """
        self._users_cache[username] = phone
        return True

    @input_error(error_msg_base="Command 'phone' failed")
    def get_contact(self, *args: str) -> str:
        """Get user phone by number.

        Args:
            args: List of one argument - username

        Returns:
            Command output.

        Raises:
            CommandOperationalError: if wrong arguments or user doesn't exist
        """
        if len(args) != 1:
            raise CommandOperationalError(
                "command expects an input of one argument: username. "
                f"Received: {' '.join(args)}"
            )

        username = args[0]
        if username not in self._users_cache:
            raise CommandOperationalError(
                f"user with username {username} doesn't exist. Try another username."
            )

        user_phone = self._users_cache[username]
        return f"Record found: \n{self._print_user_phone(username, user_phone)}"

    def print_all_contacts(self, *args: str) -> str:
        """Prepares contacts to be outputted into console.

        Args:
            args: Command doesn't expect any args, list should be empty.

        Returns:
            Command output.
        """
        command_output = ""
        if args:
            command_output += (
                "Warning: Command doesn't expect any arguments. "
                f"Received: {' '.join(args)}\n"
            )

        command_output += "All Records: \n"
        for username, phone in self._users_cache.items():
            command_output += f"\n{self._print_user_phone(username, phone)}"

        return command_output

    @staticmethod
    def _print_user_phone(username: str, phone: str) -> str:
        """Prepare user's username and phone as an output string."""
        return f"User {username} phone: {phone}"

    @input_error(error_msg_base="Command execution failed")
    def execute_command(self, command: str, args: list[str]) -> str:
        if command not in self.supported_commands:
            raise CommandNotSupported(f"command '{command}' is not supported!")

        command_handler = self.supported_commands[command]
        return command_handler(*args)

    def main(self) -> None:
        while True:
            try:
                user_input = input("Enter a command with arguments separated with a ' ' character: ")

                command, args = self.parse_input(user_input)
                command_output = self.execute_command(command, args)
                print(
                    f"Command '{command}' executed successfully. Result is:"
                    f"\n{command_output}"
                )

            except CliHelperSigStop as e:
                print(e)
                break

            except Exception as e:
                print(
                    f"Unknown exception was encountered during execution: {e}"
                    "The bot will stop ..."
                )
                raise


if __name__ == "__main__":
    cli_helper = CliHelperBot()
    cli_helper.main()
