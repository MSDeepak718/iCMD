def clean(command):
    return command.replace("```bash","").replace("```","").strip()