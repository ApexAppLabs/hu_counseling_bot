#!/usr/bin/env python3

# Script to create a properly formatted Procfile
procfile_content = "web: gunicorn render_web_service:app --bind 0.0.0.0:$PORT"

with open("Procfile", "w", encoding="utf-8", newline="\n") as f:
    f.write(procfile_content)

print("Procfile created successfully!")
print(f"Content: {repr(open('Procfile', 'rb').read())}")