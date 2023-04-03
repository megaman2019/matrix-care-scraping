STEPS

1. Install Python
2. Setup Pip
3. Get-ExecutionPolicy 
    - If result is Restricted continue to next step.
4. Allow script execution via powershell.
    - Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
5. Activate virtual environment
    - myenv/Scripts/activate.ps1
    (Note: To deactivate, execute - deactivate)
6. Install dependency requirements
    - pip install -r requirements.txt
    (Note: To create requirements.txt execute - pip freeze > requirements.txt)
7. Install chromedriver-binary-auto if not yet installed.