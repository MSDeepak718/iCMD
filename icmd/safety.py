CRITICAL_COMMANDS = [
    "rm", "rmdir", "mv", "dd", "mkfs",
    "shutdown", "reboot", "init", "poweroff",
    "kill", "killall", "chmod", "chown",
    "sudo", "su", "mount", "umount",
    "wget", "curl", "scp", "ssh"
]

DANGEROUS_SYMBOLS = [";", "|", "&", ">", ">>"]


def is_dangerous(command):
    parts = command.strip().split()
    if parts[0] in CRITICAL_COMMANDS:
        return True
    for symbol in DANGEROUS_SYMBOLS:
        if symbol in command:
            return True
    return False