import os

for i in os.listdir("templates"):
    with open(f"templates/{i}") as f:
        text = f.read()

    while '  ' in text:
        text = text.replace('  ', ' ')
    
    while '\n' in text:
        text = text.replace('\n', '')
    
    with open(f"templates/min{i}", 'w') as f:
        f.write(text)