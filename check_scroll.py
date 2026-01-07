import os

path = r'c:\Users\HP\Desktop\GyeonggooLee\automatic\templates\application_form.html'
with open(path, 'rb') as f:
    raw_data = f.read()

# Try to find the function and replace it
# We use bytes because of potential encoding issues in the environment
target = b'window.location.replace(\'/applyform?status=\' + nextStatus + \'&local_nm=\' + encodeURIComponent(localNm));'
replacement = b"window.location.replace('/applyform?status=' + nextStatus + '&local_nm=' + encodeURIComponent(localNm));"

# Actually, the user wants the scroll to top. 
# The existing $(document).ready has window.scrollTo(0, 0);
# So we don't need to change the redirect itself, but ensure the alert and flow are correct.

print("Current redir line found:", target in raw_data)

# Let's just confirm the scroll to top exists
ready_scroll = b'window.scrollTo(0, 0);'
print("Ready scroll found:", ready_scroll in raw_data)
